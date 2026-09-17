import Foundation
import SceneKit
import ModelIO
import SceneKit.ModelIO

#if os(macOS)
typealias SceneFloat = CGFloat
#else
typealias SceneFloat = Float
#endif

/// Anything the viewer managed to turn into a SceneKit node, plus the framing
/// numbers the camera and the stats bar need.
struct LoadedModel {
    var node: SCNNode
    var center: SIMD3<Float>
    var boundingRadius: Float
    /// STL/STEP from these CAD tools are authored in millimetres.
    var sizeMillimeters: SIMD3<Float>
    var triangleCount: Int?
    var loaderName: String
}

enum MeshLoaderError: LocalizedError {
    case unsupported(ext: String)
    case empty

    var errorDescription: String? {
        switch self {
        case .unsupported(let ext):
            return ".\(ext) is a boundary-representation CAD format — rendering it needs a geometry kernel the phone doesn't have. Export an STL or OBJ from the same model and open that."
        case .empty:
            return "The file loaded but contained no geometry."
        }
    }
}

enum MeshLoader {
    /// Formats we can actually draw. STL goes through `STLParser`; the rest
    /// through Model I/O, which handles OBJ/PLY/USD natively on both platforms.
    static let renderableExtensions = ["stl", "obj", "ply", "usd", "usda", "usdc", "usdz", "abc"]
    /// Formats we can identify and describe but not tessellate.
    static let describableExtensions = ["step", "stp", "iges", "igs", "3mf", "f3d"]

    static func isRenderable(_ url: URL) -> Bool {
        renderableExtensions.contains(url.pathExtension.lowercased())
    }

    static func load(url: URL) throws -> LoadedModel {
        let ext = url.pathExtension.lowercased()
        if ext == "stl" {
            let mesh = try STLParser.parse(try Data(contentsOf: url, options: .mappedIfSafe))
            guard mesh.triangleCount > 0 else { throw MeshLoaderError.empty }
            let node = SCNNode(geometry: mesh.makeGeometry())
            return LoadedModel(node: node,
                               center: mesh.center,
                               boundingRadius: mesh.boundingRadius,
                               sizeMillimeters: mesh.size,
                               triangleCount: mesh.triangleCount,
                               loaderName: "Built-in STL reader")
        }
        guard renderableExtensions.contains(ext) else { throw MeshLoaderError.unsupported(ext: ext) }

        let asset = MDLAsset(url: url)
        guard asset.count > 0 else { throw MeshLoaderError.empty }
        let scene = SCNScene(mdlAsset: asset)
        let node = SCNNode()
        for child in scene.rootNode.childNodes { node.addChildNode(child) }

        let box = node.boundingBox
        let lo = SIMD3<Float>(Float(box.min.x), Float(box.min.y), Float(box.min.z))
        let hi = SIMD3<Float>(Float(box.max.x), Float(box.max.y), Float(box.max.z))
        let size = hi - lo
        let half = size / 2
        let radius = max(sqrt(half.x * half.x + half.y * half.y + half.z * half.z), 0.0001)

        var triangles = 0
        for mesh in asset.childObjects(of: MDLMesh.self) as? [MDLMesh] ?? [] {
            for case let submesh as MDLSubmesh in mesh.submeshes ?? NSMutableArray() {
                if submesh.geometryType == .triangles { triangles += submesh.indexCount / 3 }
            }
        }

        return LoadedModel(node: node,
                           center: (lo + hi) / 2,
                           boundingRadius: radius,
                           sizeMillimeters: size,
                           triangleCount: triangles > 0 ? triangles : nil,
                           loaderName: "Model I/O")
    }
}

/// STEP files can't be rendered here, but their ISO-10303-21 header is plain
/// text and says which kernel wrote them — worth showing instead of a dead end.
enum StepHeader {
    struct Field: Identifiable {
        var id: String { label }
        let label: String
        let value: String
    }

    static func read(url: URL) -> [Field] {
        guard let handle = try? FileHandle(forReadingFrom: url) else { return [] }
        defer { try? handle.close() }
        let head = (try? handle.read(upToCount: 4096)) ?? Data()
        guard let text = String(data: head, encoding: .utf8)
                ?? String(data: head, encoding: .isoLatin1) else { return [] }
        return parse(text)
    }

    static func parse(_ text: String) -> [Field] {
        // Everything up to ENDSEC is the header; strip newlines so multi-line
        // entities read as one string.
        let header = text.components(separatedBy: "ENDSEC").first ?? text
        let flat = header.replacingOccurrences(of: "\n", with: " ")
            .replacingOccurrences(of: "\r", with: " ")
        var fields: [Field] = []

        let quoted = quotedStrings(in: entity("FILE_NAME", in: flat) ?? "")
        if let name = quoted.first, !name.isEmpty { fields.append(Field(label: "Name", value: name)) }
        if quoted.count > 1, !quoted[1].isEmpty { fields.append(Field(label: "Written", value: quoted[1])) }
        // FILE_NAME's 6th and 7th strings are the originating system and author.
        if quoted.count > 5, !quoted[5].isEmpty {
            fields.append(Field(label: "Preprocessor", value: quoted[5]))
        }
        if quoted.count > 6, !quoted[6].isEmpty, quoted[6] != "Unknown" {
            fields.append(Field(label: "Originating system", value: quoted[6]))
        }
        if let desc = quotedStrings(in: entity("FILE_DESCRIPTION", in: flat) ?? "").first, !desc.isEmpty {
            fields.append(Field(label: "Description", value: desc))
        }
        if let schema = quotedStrings(in: entity("FILE_SCHEMA", in: flat) ?? "").first, !schema.isEmpty {
            fields.append(Field(label: "Schema", value: schema))
        }
        return fields
    }

    private static func entity(_ name: String, in text: String) -> String? {
        guard let start = text.range(of: name + "(") else { return nil }
        guard let end = text.range(of: ");", range: start.upperBound..<text.endIndex) else { return nil }
        return String(text[start.upperBound..<end.lowerBound])
    }

    private static func quotedStrings(in text: String) -> [String] {
        text.components(separatedBy: "'").enumerated()
            .filter { $0.offset % 2 == 1 }
            .map { $0.element.trimmingCharacters(in: .whitespaces) }
    }
}
