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

/// One design an agent dropped into `cad/`: its meshes, the renders that came
/// with it, and when it last changed — the app opens on the newest one.
struct CADDesign: Identifiable, Hashable {
    var id: String
    /// The README heading, e.g. "Hand gripper — a handheld gripper you wear".
    var name: String
    var folder: String
    var updated: Date
    var models: [CADModel]
    /// The model shown first: a closed assembly when there is one.
    var primary: CADModel?
    var images: [URL]

    /// "Hand gripper" out of "Hand gripper — a handheld gripper you wear".
    var title: String { String(name.split(separator: "—", maxSplits: 1).first ?? Substring(name)).trimmingCharacters(in: .whitespaces) }

    var subtitle: String? {
        let parts = name.split(separator: "—", maxSplits: 1)
        return parts.count > 1 ? parts[1].trimmingCharacters(in: .whitespaces) : nil
    }
}

extension CADModel {
    /// Tessellates off the main thread; STLs of a few MB take a moment.
    func loadMesh() async -> Result<LoadedModel, Error> {
        guard let url else {
            return .failure(MeshLoaderError.unsupported(ext: fileExtension))
        }
        return await withCheckedContinuation { continuation in
            DispatchQueue.global(qos: .userInitiated).async {
                do { continuation.resume(returning: .success(try MeshLoader.load(url: url))) }
                catch { continuation.resume(returning: .failure(error)) }
            }
        }
    }
}

/// Reads `CADModels/manifest.json` — written into the app bundle by
/// `Scripts/stage_cad_models.py` during the build — and the user's imported
/// files in Application Support.
@MainActor
final class CADModelCatalog: ObservableObject {
    @Published private(set) var bundled: [CADModel] = []
    /// Newest first — the order the manifest was written in.
    @Published private(set) var designs: [CADDesign] = []
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
        (designs, bundled) = Self.loadManifest()
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

    private static func loadManifest() -> ([CADDesign], [CADModel]) {
        guard let resources = Bundle.main.resourceURL else { return ([], []) }
        let root = resources.appendingPathComponent("CADModels", isDirectory: true)
        guard let data = try? Data(contentsOf: root.appendingPathComponent("manifest.json")),
              let raw = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let entries = raw["models"] as? [[String: Any]] else { return ([], []) }

        let models = entries.compactMap { entry -> CADModel? in
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
        let byID = Dictionary(models.map { ($0.id, $0) }, uniquingKeysWith: { first, _ in first })

        let designs = (raw["designs"] as? [[String: Any]] ?? []).compactMap { entry -> CADDesign? in
            guard let id = entry["id"] as? String,
                  let name = entry["name"] as? String else { return nil }
            let members = (entry["models"] as? [String] ?? []).compactMap { byID[$0] }
            return CADDesign(
                id: id,
                name: name,
                folder: entry["folder"] as? String ?? id,
                updated: Date(timeIntervalSince1970: entry["updated"] as? TimeInterval ?? 0),
                models: members,
                primary: (entry["primary"] as? String).flatMap { byID[$0] } ?? members.first,
                images: (entry["images"] as? [String] ?? []).map { root.appendingPathComponent($0) })
        }
        return (designs, models)
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
