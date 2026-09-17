import SwiftUI

/// One model on screen: the SceneKit viewport on top, the numbers that matter
/// for the gripper bake-off underneath.
struct ModelDetailView: View {
    let model: CADModel

    private enum LoadState {
        case loading
        case loaded(LoadedModel)
        case failed(String)
    }

    @State private var state: LoadState = .loading
    @State private var wireframe = false
    @State private var spinning = false
    @State private var cameraGeneration = 0

    var body: some View {
        VStack(spacing: 0) {
            viewport
                .frame(maxWidth: .infinity, minHeight: 280)
            Divider().opacity(0.3)
            ScrollView { details.padding(20) }
        }
        .background(Color(red: 0.05, green: 0.12, blue: 0.16).ignoresSafeArea())
        .navigationTitle(model.name)
        .toolbar {
            ToolbarItemGroup {
                if case .loaded = state {
                    Button {
                        spinning.toggle()
                    } label: {
                        Image(systemName: spinning ? "pause.circle" : "arrow.triangle.2.circlepath")
                    }
                    .help(spinning ? "Stop spinning" : "Spin")

                    Button {
                        wireframe.toggle()
                    } label: {
                        Image(systemName: wireframe ? "cube.fill" : "grid")
                    }
                    .help(wireframe ? "Solid" : "Wireframe")

                    Button {
                        cameraGeneration += 1
                    } label: {
                        Image(systemName: "scope")
                    }
                    .help("Reset view")
                }
            }
        }
        .task(id: model.id) { await load() }
    }

    @ViewBuilder private var viewport: some View {
        switch state {
        case .loading:
            ZStack {
                Color.black.opacity(0.3)
                ProgressView("Tessellating…")
            }
        case .loaded(let loaded):
            ModelSceneView(model: loaded,
                           wireframe: wireframe,
                           spinning: spinning,
                           cameraGeneration: cameraGeneration)
        case .failed(let message):
            ZStack {
                Color.black.opacity(0.3)
                VStack(spacing: 12) {
                    Image(systemName: "cube.transparent")
                        .font(.largeTitle)
                        .foregroundStyle(.secondary)
                    Text(message)
                        .font(.footnote)
                        .multilineTextAlignment(.center)
                        .foregroundStyle(.secondary)
                        .padding(.horizontal, 28)
                }
            }
        }
    }

    private var details: some View {
        VStack(alignment: .leading, spacing: 14) {
            if case .loaded(let loaded) = state {
                row("Bounding box", format(loaded.sizeMillimeters))
                if let triangles = loaded.triangleCount {
                    row("Triangles", triangles.formatted(.number.grouping(.automatic)))
                }
                row("Loaded by", loaded.loaderName)
            }
            row("Source", model.engine)
            row("Format", model.fileExtension.uppercased())
            if model.byteCount > 0 { row("File size", model.formattedSize) }

            let header = headerFields
            if !header.isEmpty {
                Text("STEP header")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(.secondary)
                    .padding(.top, 6)
                ForEach(header, id: \.0) { row($0.0, $0.1) }
            }

            if case .loaded = state {
                Text("Drag to orbit, pinch or scroll to zoom, two fingers to pan.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                    .padding(.top, 6)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    /// Bundled STEP headers are parsed at build time; imported ones are read
    /// from the file on the spot.
    private var headerFields: [(String, String)] {
        if !model.headerFields.isEmpty {
            return model.headerFields.sorted { $0.key < $1.key }.map { ($0.key, $0.value) }
        }
        guard let url = model.url, !model.isRenderable else { return [] }
        return StepHeader.read(url: url).map { ($0.label, $0.value) }
    }

    private func row(_ title: String, _ value: String) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(title)
                .font(.caption)
                .foregroundStyle(.secondary)
            Text(value)
                .font(.footnote.monospaced())
                .textSelection(.enabled)
        }
    }

    private func format(_ size: SIMD3<Float>) -> String {
        String(format: "%.1f × %.1f × %.1f mm", size.x, size.y, size.z)
    }

    private func load() async {
        state = .loading
        guard let url = model.url else {
            state = .failed(MeshLoaderError.unsupported(ext: model.fileExtension).localizedDescription
                            + "\n\nOnly this file's header shipped with the app.")
            return
        }
        let outcome: Result<LoadedModel, Error> = await withCheckedContinuation { continuation in
            DispatchQueue.global(qos: .userInitiated).async {
                do { continuation.resume(returning: .success(try MeshLoader.load(url: url))) }
                catch { continuation.resume(returning: .failure(error)) }
            }
        }
        switch outcome {
        case .success(let loaded): state = .loaded(loaded)
        case .failure(let error): state = .failed(error.localizedDescription)
        }
    }
}
