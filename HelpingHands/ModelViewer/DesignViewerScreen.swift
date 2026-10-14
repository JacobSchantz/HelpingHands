import SwiftUI
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
/// and below it the title, a part picker and every render, full width. A
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
        case failed(String)
    }

    @State private var selected: CADModel?
    @State private var state: LoadState = .loading
    @State private var cameraGeneration = 0
    @State private var zoomed: Zoom?

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
                ProgressView("Loading \(current?.name ?? "model")…")
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

            if design.models.count > 1 {
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

            if let current {
                NavigationLink(value: current) {
                    Label("Details for \(current.name)", systemImage: "info.circle")
                        .font(.footnote)
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
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
