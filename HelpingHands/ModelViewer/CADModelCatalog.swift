import Foundation

/// One openable 3D file: either baked into the app from `cad/` at build time or
/// imported by the user at runtime.
struct CADModel: Identifiable, Hashable {
    enum Origin: Hashable {
        case bundled
        case imported
    }

    var id: String
    var name: String
    var engine: String
    var fileExtension: String
    var byteCount: Int
    /// `nil` when the payload wasn't bundled (STEP files ship as metadata only).
    var url: URL?
    var origin: Origin
    /// Pre-parsed ISO-10303-21 header for bundled STEP files.
    var headerFields: [String: String]

    var isRenderable: Bool {
        guard let url else { return false }
        return MeshLoader.isRenderable(url)
    }

    var formattedSize: String {
        ByteCountFormatter.string(fromByteCount: Int64(byteCount), countStyle: .file)
    }
}

/// Reads `CADModels/manifest.json` — written into the app bundle by
/// `Scripts/stage_cad_models.py` during the build — and the user's imported
/// files in Application Support.
@MainActor
final class CADModelCatalog: ObservableObject {
    @Published private(set) var bundled: [CADModel] = []
    @Published private(set) var imported: [CADModel] = []
    @Published private(set) var lastImportError: String?

    static let importDirectory: URL = {
        let base = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first
            ?? URL(fileURLWithPath: NSTemporaryDirectory())
        let dir = base.appendingPathComponent("ImportedModels", isDirectory: true)
        try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        return dir
    }()

    init() {
        reload()
    }

    /// Bundled models grouped by the CAD engine that produced them, engines in
    /// a stable order so the bake-off always reads the same way.
    var bundledByEngine: [(engine: String, models: [CADModel])] {
        let groups = Dictionary(grouping: bundled, by: \.engine)
        return groups.keys.sorted().map { key in
            (engine: key, models: groups[key]!.sorted { $0.name < $1.name })
        }
    }

    func reload() {
        bundled = Self.loadManifest()
        imported = Self.loadImported()
    }

    /// Copies a picked file into Application Support so it survives relaunches
    /// and doesn't depend on a security-scoped URL staying valid.
    func importFile(at source: URL) {
        let scoped = source.startAccessingSecurityScopedResource()
        defer { if scoped { source.stopAccessingSecurityScopedResource() } }

        var destination = Self.importDirectory.appendingPathComponent(source.lastPathComponent)
        var attempt = 2
        while FileManager.default.fileExists(atPath: destination.path) {
            let stem = source.deletingPathExtension().lastPathComponent
            destination = Self.importDirectory
                .appendingPathComponent("\(stem)-\(attempt).\(source.pathExtension)")
            attempt += 1
        }
        do {
            try FileManager.default.copyItem(at: source, to: destination)
            lastImportError = nil
        } catch {
            lastImportError = error.localizedDescription
        }
        imported = Self.loadImported()
    }

    func delete(_ model: CADModel) {
        guard model.origin == .imported, let url = model.url else { return }
        try? FileManager.default.removeItem(at: url)
        imported = Self.loadImported()
    }

    // MARK: - Loading

    private static func loadManifest() -> [CADModel] {
        guard let resources = Bundle.main.resourceURL else { return [] }
        let root = resources.appendingPathComponent("CADModels", isDirectory: true)
        guard let data = try? Data(contentsOf: root.appendingPathComponent("manifest.json")),
              let raw = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let entries = raw["models"] as? [[String: Any]] else { return [] }

        return entries.compactMap { entry in
            guard let id = entry["id"] as? String,
                  let name = entry["name"] as? String,
                  let engine = entry["engine"] as? String else { return nil }
            let path = entry["path"] as? String
            return CADModel(
                id: id,
                name: name,
                engine: engine,
                fileExtension: (entry["ext"] as? String ?? "").lowercased(),
                byteCount: entry["bytes"] as? Int ?? 0,
                url: path.map { root.appendingPathComponent($0) },
                origin: .bundled,
                headerFields: entry["header"] as? [String: String] ?? [:])
        }
    }

    private static func loadImported() -> [CADModel] {
        let urls = (try? FileManager.default.contentsOfDirectory(
            at: importDirectory,
            includingPropertiesForKeys: [.fileSizeKey],
            options: [.skipsHiddenFiles])) ?? []

        return urls.sorted { $0.lastPathComponent < $1.lastPathComponent }.map { url in
            let size = (try? url.resourceValues(forKeys: [.fileSizeKey]).fileSize) ?? 0
            return CADModel(
                id: "imported/" + url.lastPathComponent,
                name: url.deletingPathExtension().lastPathComponent,
                engine: "Imported",
                fileExtension: url.pathExtension.lowercased(),
                byteCount: size,
                url: url,
                origin: .imported,
                headerFields: [:])
        }
    }
}
