import SwiftUI
import SceneKit
#if canImport(UIKit)
import UIKit
#elseif canImport(AppKit)
import AppKit
#endif

/// The app's first screen: the newest design in `cad/`, already loaded in a
/// 3D viewport with its renders underneath. Swipe sideways under the viewport
/// (or open the list) for older designs. The arms, plans and file browser live
/// behind the toolbar's Workshop button.
struct DesignViewerScreen: View {
    private enum Destination: Hashable {
        case workshop
    }

    @StateObject private var catalog = CADModelCatalog()
    @State private var index = 0
    @State private var showingList = false
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            Group {
                if catalog.designs.isEmpty {
                    empty
                } else {
                    DesignPage(design: catalog.designs[index],
                               position: index,
                               count: catalog.designs.count,
                               step: step)
                        .id(catalog.designs[index].id)
                }
            }
            .background(Color(red: 0.05, green: 0.12, blue: 0.16).ignoresSafeArea())
            .navigationTitle(catalog.designs.isEmpty ? "Helping Hands" : catalog.designs[index].title)
            #if os(iOS)
            .navigationBarTitleDisplayMode(.inline)
            #endif
            .toolbar {
                ToolbarItem(placement: .primaryAction) {
                    Button {
                        path.append(Destination.workshop)
                    } label: {
                        Label("Workshop", systemImage: "wrench.and.screwdriver")
                    }
                }
                ToolbarItem(placement: .navigation) {
                    Button {
                        showingList = true
                    } label: {
                        Label("All designs", systemImage: "list.bullet")
                    }
                    .disabled(catalog.designs.count < 2)
                }
            }
            .navigationDestination(for: Destination.self) { _ in WorkshopScreen() }
            .navigationDestination(for: CADModel.self) { ModelDetailView(model: $0) }
            .sheet(isPresented: $showingList) { list }
        }
    }

    private func step(_ delta: Int) {
        let next = index + delta
        guard catalog.designs.indices.contains(next) else { return }
        withAnimation(.easeInOut(duration: 0.2)) { index = next }
    }

    private var empty: some View {
        VStack(spacing: 12) {
            Image(systemName: "cube.transparent")
                .font(.largeTitle)
                .foregroundStyle(.secondary)
            Text("No designs in this build. Drop STLs into a folder under cad/ (with renders in render/) and rebuild.")
                .font(.footnote)
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)
                .padding(.horizontal, 32)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    private var list: some View {
        NavigationStack {
            List(Array(catalog.designs.enumerated()), id: \.element.id) { offset, design in
                Button {
                    index = offset
                    showingList = false
                } label: {
                    HStack(spacing: 12) {
                        DesignImage(url: design.images.first)
                            .frame(width: 56, height: 56)
                            .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
                        VStack(alignment: .leading, spacing: 2) {
                            Text(design.title)
                                .font(.headline)
                            Text(design.updated.formatted(date: .abbreviated, time: .omitted)
                                 + " · \(design.models.count) file\(design.models.count == 1 ? "" : "s")")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                        Spacer()
                        if offset == index {
                            Image(systemName: "checkmark")
                                .foregroundStyle(Color.accentColor)
                        }
                    }
                    .contentShape(Rectangle())
                }
                .buttonStyle(.plain)
            }
            .navigationTitle("Designs")
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Done") { showingList = false }
                }
            }
        }
        #if os(macOS)
        .frame(minWidth: 360, minHeight: 420)
        #endif
    }
}

/// One design: the viewport on top (drag inside it to orbit, pinch to zoom),
/// and below it the title, a part picker and every render, full width. An
/// assembly design (one with a parts.json) instead draws every piece in the
/// one viewport, pulled apart, with a toggle that snaps them together. A
/// sideways swipe on the lower half changes design — the viewport keeps its
/// drags for the camera.
private struct DesignPage: View {
    let design: CADDesign
    let position: Int
    let count: Int
    let step: (Int) -> Void

    private enum LoadState {
        case loading
        case loaded(LoadedModel)
        case assembly(AssemblyScene)
        case failed(String)
    }

    @State private var selected: CADModel?
    @State private var state: LoadState = .loading
    @State private var cameraGeneration = 0
    @State private var zoomed: Zoom?
    @State private var exploded = true
    /// The generation the camera is framing; nil frames them all.
    @State private var focus: Int?

    private struct Zoom: Identifiable {
        let url: URL
        var id: URL { url }
    }

    private var current: CADModel? { selected ?? design.primary }

    var body: some View {
        VStack(spacing: 0) {
            viewport
                .frame(maxWidth: .infinity)
                .frame(minHeight: 300)
                .layoutPriority(1)
            Divider().opacity(0.3)
            ScrollView { details.padding(20) }
                .simultaneousGesture(swipe)
        }
        .task(id: current?.id) { await load() }
        .onChange(of: exploded) { _, apart in
            if case .assembly(let assembly) = state { assembly.setExploded(apart, animated: true) }
        }
        .sheet(item: $zoomed) { zoom in
            DesignImage(url: zoom.url, fit: true)
                .padding()
                .onTapGesture { zoomed = nil }
                #if os(macOS)
                .frame(minWidth: 600, minHeight: 450)
                #endif
        }
    }

    private var swipe: some Gesture {
        DragGesture(minimumDistance: 40)
            .onEnded { value in
                let dx = value.translation.width
                guard abs(dx) > abs(value.translation.height) * 1.5 else { return }
                step(dx < 0 ? 1 : -1)
            }
    }

    @ViewBuilder private var viewport: some View {
        switch state {
        case .loading:
            ZStack {
                Color.black.opacity(0.3)
                ProgressView(design.parts.isEmpty ? "Loading \(current?.name ?? "model")…"
                                                  : "Loading \(design.parts.count) pieces…")
            }
        case .loaded(let loaded):
            ModelSceneView(model: loaded, wireframe: false, spinning: false,
                           cameraGeneration: cameraGeneration)
                .overlay(alignment: .bottomTrailing) {
                    Button {
                        cameraGeneration += 1
                    } label: {
                        Image(systemName: "scope")
                            .padding(10)
                            .background(.ultraThinMaterial, in: Circle())
                    }
                    .buttonStyle(.plain)
                    .help("Reset view")
                    .padding(12)
                }
        case .assembly(let assembly):
            SceneView(scene: assembly.scene, pointOfView: assembly.camera,
                      options: [.allowsCameraControl, .autoenablesDefaultLighting],
                      antialiasingMode: .multisampling2X)
                .id(cameraGeneration)
                .overlay(alignment: .top) {
                    if design.groups.count > 1 { generationBar(assembly) }
                }
                .overlay(alignment: .bottom) {
                    HStack {
                        Button {
                            exploded.toggle()
                        } label: {
                            Label(exploded ? "Assemble" : "Explode",
                                  systemImage: exploded ? "arrow.down.right.and.arrow.up.left"
                                                        : "arrow.up.left.and.arrow.down.right")
                                .font(.footnote.weight(.semibold))
                                .padding(.horizontal, 12)
                                .padding(.vertical, 8)
                                .background(.ultraThinMaterial, in: Capsule())
                        }
                        .buttonStyle(.plain)
                        Spacer()
                        Button {
                            assembly.resetCamera(group: focus)
                            cameraGeneration += 1
                        } label: {
                            Image(systemName: "scope")
                                .padding(10)
                                .background(.ultraThinMaterial, in: Circle())
                        }
                        .buttonStyle(.plain)
                        .help("Reset view")
                    }
                    .padding(12)
                }
        case .failed(let message):
            ZStack {
                Color.black.opacity(0.3)
                if let image = design.images.first {
                    // No mesh the phone can draw (a STEP-only design): show
                    // its render instead of an error.
                    DesignImage(url: image, fit: true)
                } else {
                    Text(message)
                        .font(.footnote)
                        .multilineTextAlignment(.center)
                        .foregroundStyle(.secondary)
                        .padding(.horizontal, 28)
                }
            }
        }
    }

    /// One chip per generation, oldest first, plus "All": tap one and the
    /// camera frames that generation. Explode keeps working on all of them.
    private func generationBar(_ assembly: AssemblyScene) -> some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                chip("All", selected: focus == nil) { frame(nil, assembly) }
                ForEach(Array(design.groups.enumerated()), id: \.offset) { g, label in
                    chip(label, selected: focus == g) { frame(g, assembly) }
                }
            }
            .padding(12)
        }
    }

    private func chip(_ text: String, selected: Bool, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Text(text)
                .font(.footnote.weight(.semibold))
                .padding(.horizontal, 12)
                .padding(.vertical, 7)
                .background(selected ? AnyShapeStyle(Color.accentColor.opacity(0.85))
                                     : AnyShapeStyle(.ultraThinMaterial), in: Capsule())
        }
        .buttonStyle(.plain)
    }

    private func frame(_ group: Int?, _ assembly: AssemblyScene) {
        focus = group
        assembly.resetCamera(group: group)
        cameraGeneration += 1
    }

    private var details: some View {
        VStack(alignment: .leading, spacing: 14) {
            VStack(alignment: .leading, spacing: 4) {
                if let subtitle = design.subtitle {
                    Text(subtitle)
                        .font(.subheadline)
                }
                Text("\(design.updated.formatted(date: .abbreviated, time: .shortened)) · \(design.folder)")
                    .font(.caption.monospaced())
                    .foregroundStyle(.secondary)
                if count > 1 {
                    Text(position == 0
                         ? "Newest of \(count) designs — swipe left for older ones"
                         : "\(position + 1) of \(count) · swipe to browse")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }

            if !design.parts.isEmpty {
                partsLegend
            } else if design.models.count > 1 {
                partPicker
            }

            ForEach(design.images, id: \.self) { url in
                VStack(alignment: .leading, spacing: 4) {
                    DesignImage(url: url, fit: true)
                        .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
                        .onTapGesture { zoomed = Zoom(url: url) }
                    Text(url.deletingPathExtension().lastPathComponent.replacingOccurrences(of: "_", with: " "))
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }

            if design.parts.isEmpty, let current {
                NavigationLink(value: current) {
                    Label("Details for \(current.name)", systemImage: "info.circle")
                        .font(.footnote)
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    /// One row per printed piece, in its viewport colour; tap for that STL alone.
    private var partsLegend: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(design.groups.count > 1
                 ? "\(design.groups.count) generations, \(design.parts.count) pieces — each prints on its own"
                 : "\(design.parts.count) pieces — each prints on its own")
                .font(.caption)
                .foregroundStyle(.secondary)
            ForEach(design.parts) { part in
                if design.groups.count > 1, design.parts.first(where: { $0.group == part.group })?.id == part.id,
                   design.groups.indices.contains(part.group) {
                    Text(design.groups[part.group])
                        .font(.footnote.weight(.semibold))
                        .padding(.top, 6)
                }
                NavigationLink(value: part.model) {
                    HStack(spacing: 10) {
                        Circle()
                            .fill(Color(red: Double(part.color.x), green: Double(part.color.y), blue: Double(part.color.z)))
                            .overlay(Circle().stroke(.white.opacity(0.3)))
                            .frame(width: 14, height: 14)
                        Text(part.name)
                            .font(.subheadline)
                        Spacer()
                        if !part.material.isEmpty, !part.name.contains(part.material) {
                            Text(part.material)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                        Text(part.model.formattedSize)
                            .font(.caption.monospaced())
                            .foregroundStyle(.secondary)
                        Image(systemName: "chevron.right")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                    .contentShape(Rectangle())
                }
                .buttonStyle(.plain)
            }
        }
    }

    private var partPicker: some View {
        Picker("Part", selection: Binding(
            get: { current?.id ?? "" },
            set: { id in selected = design.models.first { $0.id == id } })) {
            ForEach(design.models) { model in
                Text(model.isRenderable ? model.name : "\(model.name) (\(model.fileExtension.uppercased()))")
                    .tag(model.id)
            }
        }
        .pickerStyle(.menu)
    }

    private func load() async {
        state = .loading
        if !design.parts.isEmpty {
            var meshes: [(CADPart, LoadedModel)] = []
            for part in design.parts {
                switch await part.model.loadMesh() {
                case .success(let loaded): meshes.append((part, loaded))
                case .failure(let error):
                    state = .failed("\(part.name): \(error.localizedDescription)")
                    return
                }
            }
            state = .assembly(AssemblyScene(parts: meshes, groups: design.groups, exploded: exploded))
            return
        }
        guard let current else {
            state = .failed("This design has no 3D files.")
            return
        }
        switch await current.loadMesh() {
        case .success(let loaded): state = .loaded(loaded)
        case .failure(let error): state = .failed(error.localizedDescription)
        }
    }
}

/// Every piece of an assembly design in one SceneKit scene. The meshes are
/// exported in their assembled positions, so a piece sits at its generation's
/// slot when assembled and at its `explode` offset from there when pulled
/// apart. A design with several generations lines them up left to right along
/// X, oldest first, each with a floating label. The scene and the camera are
/// kept here, not rebuilt per SwiftUI update, so the explode animation and the
/// user's orbit both survive re-renders.
final class AssemblyScene {
    let scene = SCNScene()
    private(set) var camera = SCNNode()
    private var pieces: [(node: SCNNode, base: SIMD3<Float>, offset: SIMD3<Float>)] = []
    /// Per generation, its centre and radius in scene coordinates.
    private var framings: [(center: SIMD3<Float>, radius: Float)] = []
    private let radius: Float
    private static let gap: Float = 50

    init(parts: [(CADPart, LoadedModel)], groups: [String], exploded: Bool) {
        scene.background.contents = PlatformColor(red: 0.05, green: 0.10, blue: 0.14, alpha: 1)

        // Each generation's footprint, assembled and pulled apart, so toggling
        // never pushes a piece into its neighbour or out of shot.
        let count = max(groups.count, (parts.map(\.0.group).max() ?? 0) + 1)
        var bounds = Array(repeating: (lo: SIMD3<Float>(repeating: .greatestFiniteMagnitude),
                                       hi: SIMD3<Float>(repeating: -.greatestFiniteMagnitude)), count: count)
        for (part, mesh) in parts {
            for shift in [SIMD3<Float>.zero, part.explode] {
                bounds[part.group].lo = simd_min(bounds[part.group].lo, mesh.center - mesh.sizeMillimeters / 2 + shift)
                bounds[part.group].hi = simd_max(bounds[part.group].hi, mesh.center + mesh.sizeMillimeters / 2 + shift)
            }
        }
        var slots = [SIMD3<Float>](repeating: .zero, count: count)
        var cursor: Float = 0
        var lo = SIMD3<Float>(repeating: .greatestFiniteMagnitude)
        var hi = -lo
        for g in bounds.indices where bounds[g].lo.x <= bounds[g].hi.x {
            slots[g] = SIMD3(cursor - bounds[g].lo.x, 0, 0)
            cursor += bounds[g].hi.x - bounds[g].lo.x + Self.gap
            lo = simd_min(lo, bounds[g].lo + slots[g])
            hi = simd_max(hi, bounds[g].hi + slots[g])
        }
        let center = (lo + hi) / 2
        radius = max(simd_length(hi - lo) / 2, 0.001)
        // CAD Z-up -> SceneKit Y-up, after the content is centred.
        func toScene(_ p: SIMD3<Float>) -> SIMD3<Float> { let q = p - center; return SIMD3(q.x, q.z, -q.y) }
        framings = bounds.indices.map { g in
            let (a, b) = (bounds[g].lo + slots[g], bounds[g].hi + slots[g])
            return (toScene((a + b) / 2), max(simd_length(b - a) / 2, 0.001))
        }

        let content = SCNNode()
        content.simdPosition = -center
        for (part, mesh) in parts {
            let material = SCNMaterial()
            material.lightingModel = .physicallyBased
            material.diffuse.contents = PlatformColor(red: CGFloat(part.color.x), green: CGFloat(part.color.y),
                                                      blue: CGFloat(part.color.z), alpha: 1)
            material.metalness.contents = 0.15
            material.roughness.contents = 0.5
            material.isDoubleSided = true
            let node = mesh.node.clone()
            node.name = part.name
            Self.apply(material, to: node)
            let base = slots[part.group]
            node.simdPosition = base + (exploded ? part.explode : .zero)
            content.addChildNode(node)
            pieces.append((node, base, part.explode))
        }
        if groups.count > 1 {
            for (g, text) in groups.enumerated() where g < count {
                let label = Self.label(text, height: max(radius * 0.06, 6))
                let top = (bounds[g].lo + bounds[g].hi) / 2 + slots[g]
                label.simdPosition = SIMD3(top.x, top.y, bounds[g].hi.z + radius * 0.08)
                content.addChildNode(label)
            }
        }

        let pivot = SCNNode()
        pivot.addChildNode(content)
        pivot.simdEulerAngles = SIMD3<Float>(-.pi / 2, 0, 0)
        scene.rootNode.addChildNode(pivot)

        let ambient = SCNNode()
        ambient.light = SCNLight()
        ambient.light?.type = .ambient
        ambient.light?.intensity = 400
        scene.rootNode.addChildNode(ambient)
        let key = SCNNode()
        key.light = SCNLight()
        key.light?.type = .directional
        key.light?.intensity = 750
        key.simdEulerAngles = SIMD3<Float>(-0.9, 0.6, 0)
        scene.rootNode.addChildNode(key)

        resetCamera()
    }

    var groupCount: Int { framings.count }

    func setExploded(_ apart: Bool, animated: Bool) {
        SCNTransaction.begin()
        SCNTransaction.animationDuration = animated ? 0.6 : 0
        for piece in pieces { piece.node.simdPosition = piece.base + (apart ? piece.offset : .zero) }
        SCNTransaction.commit()
    }

    /// A fresh camera node: `allowsCameraControl` moves the old one in place.
    /// `group` frames one generation; nil frames them all.
    func resetCamera(group: Int? = nil) {
        let framing = group.flatMap { framings.indices.contains($0) ? framings[$0] : nil }
        let target = framing?.center ?? .zero
        let reach = framing?.radius ?? radius
        let lens = SCNCamera()
        lens.fieldOfView = 45
        let distance = reach / tan(Float(lens.fieldOfView / 2) * .pi / 180) * 1.3
        lens.zNear = Double(max(reach * 0.01, 0.01))
        lens.zFar = Double(max(distance, radius * 3) * 10)
        let node = SCNNode()
        node.camera = lens
        // A lineup of generations reads best nearly head-on, oldest on the left.
        let direction = group == nil && framings.count > 1 ? SIMD3<Float>(0.2, 0.4, 0.89)
                                                             : SIMD3<Float>(0.55, 0.35, 0.75)
        node.simdPosition = target + direction * distance
        node.simdLook(at: target, up: SIMD3<Float>(0, 1, 0), localFront: SIMD3<Float>(0, 0, -1))
        camera = node
    }

    /// Flat text that always faces the camera, centred over its generation.
    private static func label(_ text: String, height: Float) -> SCNNode {
        let geometry = SCNText(string: text, extrusionDepth: 0)
        geometry.font = .systemFont(ofSize: 10, weight: .semibold)
        geometry.flatness = 0.2
        let material = SCNMaterial()
        material.lightingModel = .constant
        material.diffuse.contents = PlatformColor.white
        material.isDoubleSided = true
        geometry.materials = [material]
        let glyphs = SCNNode(geometry: geometry)
        let (lo, hi) = glyphs.boundingBox
        glyphs.pivot = SCNMatrix4MakeTranslation((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, 0)
        glyphs.simdScale = SIMD3(repeating: height / max(Float(hi.y - lo.y), 0.001))
        let holder = SCNNode()
        holder.addChildNode(glyphs)
        holder.constraints = [SCNBillboardConstraint()]
        return holder
    }

    private static func apply(_ material: SCNMaterial, to node: SCNNode) {
        node.geometry?.materials = [material]
        node.childNodes.forEach { apply(material, to: $0) }
    }
}

/// A bundled render, decoded off the main thread so swiping between designs
/// doesn't stall on megabyte PNGs.
struct DesignImage: View {
    let url: URL?
    var fit = false

    @State private var image: Image?

    var body: some View {
        Group {
            if let image {
                if fit {
                    image.resizable().scaledToFit()
                } else {
                    image.resizable().scaledToFill()
                }
            } else {
                Rectangle()
                    .fill(Color.black.opacity(0.3))
                    .overlay {
                        Image(systemName: "cube.transparent").foregroundStyle(.secondary)
                    }
                    .aspectRatio(fit ? 4 / 3 : 1, contentMode: .fit)
            }
        }
        .task(id: url) { image = await Self.decode(url) }
    }

    private static func decode(_ url: URL?) async -> Image? {
        guard let url else { return nil }
        return await withCheckedContinuation { continuation in
            DispatchQueue.global(qos: .userInitiated).async {
                #if canImport(UIKit)
                let decoded = UIImage(contentsOfFile: url.path).map { Image(uiImage: $0) }
                #else
                let decoded = NSImage(contentsOf: url).map { Image(nsImage: $0) }
                #endif
                continuation.resume(returning: decoded)
            }
        }
    }
}
