import SwiftUI
import UniformTypeIdentifiers

/// The browse screen: every 3D file the CAD bake-off produced, grouped by the
/// tool that produced it, plus anything the user imported.
struct ModelViewerScreen: View {
    @StateObject private var catalog = CADModelCatalog()
    @State private var importing = false

    private static let importTypes: [UTType] = {
        let extensions = MeshLoader.renderableExtensions + MeshLoader.describableExtensions
        var seen = Set<String>()
        let types = extensions.compactMap { UTType(filenameExtension: $0) }
            .filter { seen.insert($0.identifier).inserted }
        return types.isEmpty ? [.data] : types
    }()

    var body: some View {
        List {
            ForEach(catalog.bundledByEngine, id: \.engine) { group in
                Section(group.engine) {
                    ForEach(group.models) { row($0) }
                }
            }

            Section {
                if catalog.imported.isEmpty {
                    Text("Import an STL, OBJ, PLY or USD file to view it here.")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                } else {
                    ForEach(catalog.imported) { model in
                        row(model)
                            .swipeActions {
                                Button(role: .destructive) {
                                    catalog.delete(model)
                                } label: {
                                    Label("Delete", systemImage: "trash")
                                }
                            }
                    }
                }
            } header: {
                Text("Imported")
            } footer: {
                if let error = catalog.lastImportError {
                    Text(error).foregroundStyle(.red)
                }
            }
        }
        .navigationTitle("3D Files")
        .toolbar {
            ToolbarItem {
                Button {
                    importing = true
                } label: {
                    Label("Import", systemImage: "plus")
                }
            }
        }
        .fileImporter(isPresented: $importing,
                      allowedContentTypes: Self.importTypes,
                      allowsMultipleSelection: true) { result in
            if case .success(let urls) = result {
                urls.forEach(catalog.importFile(at:))
            }
        }
        .refreshable { catalog.reload() }
    }

    private func row(_ model: CADModel) -> some View {
        NavigationLink(value: model) {
            HStack(spacing: 12) {
                Image(systemName: model.isRenderable ? "cube" : "doc.text")
                    .foregroundStyle(model.isRenderable ? Color.accentColor : Color.secondary)
                    .frame(width: 22)
                VStack(alignment: .leading, spacing: 2) {
                    Text(model.name)
                    Text(model.isRenderable
                         ? "\(model.fileExtension.uppercased()) · \(model.formattedSize)"
                         : "\(model.fileExtension.uppercased()) · not renderable on device")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
        }
    }
}
