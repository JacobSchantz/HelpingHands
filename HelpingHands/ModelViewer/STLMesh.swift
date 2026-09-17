import Foundation
import SceneKit

/// A tessellated triangle mesh plus the few numbers a CAD bake-off cares about.
///
/// SceneKit has no STL importer and Model I/O's STL path is inconsistent across
/// OS versions, so binary and ASCII STL are parsed here directly. Everything the
/// viewer needs — geometry, bounds, triangle count — comes out of one pass.
struct TriangleMesh {
    var positions: [Float]   // 3 floats per vertex, 3 vertices per triangle
    var normals: [Float]     // matches `positions`, flat (per-facet) shading
    var triangleCount: Int
    var min: SIMD3<Float>
    var max: SIMD3<Float>

    var size: SIMD3<Float> { max - min }
    var center: SIMD3<Float> { (min + max) / 2 }
    /// Radius of the bounding sphere, used to frame the camera.
    var boundingRadius: Float {
        let half = size / 2
        return Swift.max(sqrt(half.x * half.x + half.y * half.y + half.z * half.z), 0.0001)
    }

    func makeGeometry() -> SCNGeometry {
        let vertexCount = triangleCount * 3
        let stride = MemoryLayout<Float>.size * 3

        let vertexData = positions.withUnsafeBufferPointer { Data(buffer: $0) }
        let normalData = normals.withUnsafeBufferPointer { Data(buffer: $0) }

        let vertexSource = SCNGeometrySource(
            data: vertexData, semantic: .vertex, vectorCount: vertexCount,
            usesFloatComponents: true, componentsPerVector: 3,
            bytesPerComponent: MemoryLayout<Float>.size, dataOffset: 0, dataStride: stride)
        let normalSource = SCNGeometrySource(
            data: normalData, semantic: .normal, vectorCount: vertexCount,
            usesFloatComponents: true, componentsPerVector: 3,
            bytesPerComponent: MemoryLayout<Float>.size, dataOffset: 0, dataStride: stride)

        // STL has no shared-vertex table, so indices are simply 0..<vertexCount.
        var indices = [UInt32](repeating: 0, count: vertexCount)
        for i in 0..<vertexCount { indices[i] = UInt32(i) }
        let indexData = indices.withUnsafeBufferPointer { Data(buffer: $0) }
        let element = SCNGeometryElement(
            data: indexData, primitiveType: .triangles,
            primitiveCount: triangleCount, bytesPerIndex: MemoryLayout<UInt32>.size)

        return SCNGeometry(sources: [vertexSource, normalSource], elements: [element])
    }
}

enum STLParseError: LocalizedError {
    case tooShort
    case notSTL
    case truncated

    var errorDescription: String? {
        switch self {
        case .tooShort: return "The file is too small to be an STL."
        case .notSTL: return "This doesn't look like a binary or ASCII STL file."
        case .truncated: return "The STL file ends mid-triangle."
        }
    }
}

enum STLParser {
    /// Binary STL: 80-byte header, UInt32 triangle count, then 50 bytes per
    /// facet. The leading bytes are NOT a reliable format sniff — OpenSCAD
    /// writes "OpenSCAD..." and build123d writes "STL Exported..." into the
    /// binary header — so the length arithmetic decides, with ASCII as fallback.
    static func parse(_ data: Data) throws -> TriangleMesh {
        guard data.count >= 15 else { throw STLParseError.tooShort }
        if data.count >= 84 {
            let declared = data.withUnsafeBytes { raw -> UInt32 in
                var value: UInt32 = 0
                withUnsafeMutableBytes(of: &value) { dst in
                    dst.copyMemory(from: UnsafeRawBufferPointer(rebasing: raw[80..<84]))
                }
                return UInt32(littleEndian: value)
            }
            if Int(declared) > 0 && data.count >= 84 + Int(declared) * 50 {
                return parseBinary(data, triangleCount: Int(declared))
            }
        }
        return try parseASCII(data)
    }

    private static func parseBinary(_ data: Data, triangleCount: Int) -> TriangleMesh {
        var positions = [Float](repeating: 0, count: triangleCount * 9)
        var normals = [Float](repeating: 0, count: triangleCount * 9)
        var lo = SIMD3<Float>(repeating: .greatestFiniteMagnitude)
        var hi = SIMD3<Float>(repeating: -.greatestFiniteMagnitude)

        data.withUnsafeBytes { raw in
            let base = raw.baseAddress!.advanced(by: 84)
            for t in 0..<triangleCount {
                let facet = base.advanced(by: t * 50)
                var f = [Float](repeating: 0, count: 12)
                // The facet payload is unaligned inside the 50-byte record, so
                // it has to be copied out rather than bound in place.
                f.withUnsafeMutableBytes { dst in
                    dst.copyMemory(from: UnsafeRawBufferPointer(start: facet, count: 48))
                }
                let a = SIMD3<Float>(f[3], f[4], f[5])
                let b = SIMD3<Float>(f[6], f[7], f[8])
                let c = SIMD3<Float>(f[9], f[10], f[11])
                var n = SIMD3<Float>(f[0], f[1], f[2])
                if !n.isUsableNormal { n = computedNormal(a, b, c) }

                for (i, v) in [a, b, c].enumerated() {
                    let o = t * 9 + i * 3
                    positions[o] = v.x; positions[o + 1] = v.y; positions[o + 2] = v.z
                    normals[o] = n.x; normals[o + 1] = n.y; normals[o + 2] = n.z
                    lo = lo.replacing(with: v, where: v .< lo)
                    hi = hi.replacing(with: v, where: v .> hi)
                }
            }
        }
        return TriangleMesh(positions: positions, normals: normals,
                            triangleCount: triangleCount, min: lo, max: hi)
    }

    private static func parseASCII(_ data: Data) throws -> TriangleMesh {
        guard let text = String(data: data, encoding: .utf8)
                ?? String(data: data, encoding: .isoLatin1) else { throw STLParseError.notSTL }

        var positions: [Float] = []
        var normals: [Float] = []
        var lo = SIMD3<Float>(repeating: .greatestFiniteMagnitude)
        var hi = SIMD3<Float>(repeating: -.greatestFiniteMagnitude)
        var facetNormal = SIMD3<Float>(repeating: 0)
        var loop: [SIMD3<Float>] = []
        var sawFacet = false

        for rawLine in text.split(whereSeparator: \.isNewline) {
            let parts = rawLine.split(whereSeparator: \.isWhitespace)
            guard let keyword = parts.first else { continue }
            switch keyword {
            case "facet":
                sawFacet = true
                facetNormal = parts.count >= 5 ? vector(from: parts.suffix(3)) : SIMD3(repeating: 0)
                loop.removeAll(keepingCapacity: true)
            case "vertex":
                guard parts.count >= 4 else { continue }
                loop.append(vector(from: parts.suffix(3)))
            case "endfacet":
                guard loop.count == 3 else { loop.removeAll(keepingCapacity: true); continue }
                var n = facetNormal
                if !n.isUsableNormal { n = computedNormal(loop[0], loop[1], loop[2]) }
                for v in loop {
                    positions.append(contentsOf: [v.x, v.y, v.z])
                    normals.append(contentsOf: [n.x, n.y, n.z])
                    lo = lo.replacing(with: v, where: v .< lo)
                    hi = hi.replacing(with: v, where: v .> hi)
                }
                loop.removeAll(keepingCapacity: true)
            default:
                continue
            }
        }

        guard sawFacet else { throw STLParseError.notSTL }
        guard !positions.isEmpty else { throw STLParseError.truncated }
        return TriangleMesh(positions: positions, normals: normals,
                            triangleCount: positions.count / 9, min: lo, max: hi)
    }

    private static func vector(from parts: ArraySlice<Substring>) -> SIMD3<Float> {
        let values = parts.map { Float($0) ?? 0 }
        return SIMD3<Float>(values[0], values[1], values[2])
    }

    private static func computedNormal(_ a: SIMD3<Float>, _ b: SIMD3<Float>, _ c: SIMD3<Float>) -> SIMD3<Float> {
        let n = cross(b - a, c - a)
        let len = sqrt(n.x * n.x + n.y * n.y + n.z * n.z)
        return len > 0 ? n / len : SIMD3<Float>(0, 0, 1)
    }
}

private extension SIMD3 where Scalar == Float {
    /// STL facet normals are often written as (0,0,0); those need recomputing.
    var isUsableNormal: Bool {
        let len = sqrt(x * x + y * y + z * z)
        return len > 0.0001 && len.isFinite
    }
}
