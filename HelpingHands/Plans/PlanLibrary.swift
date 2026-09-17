import Foundation

/// Every plan the app can read aloud: the markdown under `plans/` (staged into
/// the bundle by `Scripts/stage_plans.py`), plus whatever the user imported or
/// pasted, which lives in Application Support so it survives relaunches.
@MainActor
final class PlanLibrary: ObservableObject {
    @Published private(set) var bundled: [PlanDocument] = []
    @Published private(set) var imported: [PlanDocument] = []
    @Published private(set) var lastImportError: String?

    static let importDirectory: URL = {
        let base = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first
            ?? URL(fileURLWithPath: NSTemporaryDirectory())
        let directory = base.appendingPathComponent("Plans", isDirectory: true)
        try? FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        return directory
    }()

    static let readableExtensions = ["md", "markdown", "txt", "text"]

    init() {
        reload()
    }

    func reload() {
        bundled = Self.loadBundled()
        imported = Self.loadImported()
    }

    /// Copies a picked file in rather than holding on to a security-scoped URL.
    func importFile(at source: URL) {
        let scoped = source.startAccessingSecurityScopedResource()
        defer { if scoped { source.stopAccessingSecurityScopedResource() } }

        do {
            let text = try String(contentsOf: source, encoding: .utf8)
            try write(text: text, named: source.deletingPathExtension().lastPathComponent)
            lastImportError = nil
        } catch {
            lastImportError = error.localizedDescription
        }
        imported = Self.loadImported()
    }

    /// Pasted text becomes a plan file with the same shape as an imported one.
    @discardableResult
    func addPasted(_ text: String, title: String) -> PlanDocument? {
        let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return nil }
        let name = title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
            ? "Pasted plan"
            : title.trimmingCharacters(in: .whitespacesAndNewlines)
        do {
            let url = try write(text: trimmed, named: name)
            lastImportError = nil
            imported = Self.loadImported()
            return imported.first { $0.url == url }
        } catch {
            lastImportError = error.localizedDescription
            return nil
        }
    }

    func delete(_ plan: PlanDocument) {
        guard plan.origin == .imported, let url = plan.url else { return }
        try? FileManager.default.removeItem(at: url)
        imported = Self.loadImported()
    }

    @discardableResult
    private func write(text: String, named name: String) throws -> URL {
        let stem = name.isEmpty ? "Plan" : name
        var destination = Self.importDirectory.appendingPathComponent("\(stem).md")
        var attempt = 2
        while FileManager.default.fileExists(atPath: destination.path) {
            destination = Self.importDirectory.appendingPathComponent("\(stem)-\(attempt).md")
            attempt += 1
        }
        try text.write(to: destination, atomically: true, encoding: .utf8)
        return destination
    }

    // MARK: - Loading

    private static func loadBundled() -> [PlanDocument] {
        guard let resources = Bundle.main.resourceURL else { return [] }
        let root = resources.appendingPathComponent("Plans", isDirectory: true)

        guard let data = try? Data(contentsOf: root.appendingPathComponent("manifest.json")),
              let raw = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let entries = raw["plans"] as? [[String: Any]] else {
            return []
        }

        return entries.compactMap { entry in
            guard let id = entry["id"] as? String,
                  let file = entry["file"] as? String else { return nil }
            let url = root.appendingPathComponent(file)
            guard let markdown = try? String(contentsOf: url, encoding: .utf8) else { return nil }
            return PlanDocument.parse(
                markdown: markdown,
                id: "bundled/" + id,
                fallbackTitle: entry["title"] as? String ?? id,
                source: entry["source"] as? String ?? "plans/\(file)",
                origin: .bundled,
                url: url)
        }
        .sorted { $0.title.localizedCaseInsensitiveCompare($1.title) == .orderedAscending }
    }

    private static func loadImported() -> [PlanDocument] {
        let urls = (try? FileManager.default.contentsOfDirectory(
            at: importDirectory,
            includingPropertiesForKeys: [.contentModificationDateKey],
            options: [.skipsHiddenFiles])) ?? []

        return urls
            .filter { readableExtensions.contains($0.pathExtension.lowercased()) }
            .sorted { $0.lastPathComponent < $1.lastPathComponent }
            .compactMap { url in
                guard let markdown = try? String(contentsOf: url, encoding: .utf8) else { return nil }
                return PlanDocument.parse(
                    markdown: markdown,
                    id: "imported/" + url.lastPathComponent,
                    fallbackTitle: url.deletingPathExtension().lastPathComponent,
                    source: "Added on this device",
                    origin: .imported,
                    url: url)
            }
    }
}

/// Where the listener stopped, so re-opening a plan offers to carry on instead
/// of restarting a forty-minute read.
enum PlanProgress {
    private static let prefix = "plan.progress."

    static func step(for plan: PlanDocument) -> Int {
        let stored = UserDefaults.standard.integer(forKey: prefix + plan.id)
        return plan.steps.indices.contains(stored) ? stored : 0
    }

    static func save(step: Int, for plan: PlanDocument) {
        UserDefaults.standard.set(step, forKey: prefix + plan.id)
    }
}
