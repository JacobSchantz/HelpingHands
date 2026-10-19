#if os(macOS)
import SwiftUI
import WebKit
import CoreServices

/// One design as `cad/compare/designs.py` lists it, read from the repo's
/// working files (not the bundle), so a design an agent is still editing
/// shows up as it is right now.
struct RepoDesign: Decodable, Identifiable, Hashable {
    struct Pebble: Decodable, Hashable { var id: String; var summary: String }
    var id: String
    var name: String
    var family: String
    var generation: String
    var folder: String
    var scad: String
    var concept: String?
    var notes: String
    var in_progress: [Pebble]
}

/// The live list of designs, the one open in the workbench, and the file
/// watch that keeps both renders current: a saved .scad re-exports that
/// design's STLs, any other change under cad/ (or a pebble being claimed)
/// just redraws. `helpinghands://designs/<name>` and `Scripts/design.sh` land
/// in `open(name:)`.
@MainActor
final class RepoDesigns: ObservableObject {
    static let shared = RepoDesigns()

    @Published private(set) var designs: [RepoDesign] = []
    @Published var open: RepoDesign?
    /// Bumped on every reload; each web view redraws when it changes.
    @Published private(set) var generation = 0
    @Published private(set) var status = ""

    let root = URL(fileURLWithPath: GitInfo.repoRoot, isDirectory: true)
    private var stream: FSEventStreamRef?
    private var pending: Set<String> = []
    private var debounce: DispatchWorkItem?

    /// False in a build that isn't sitting next to its checkout (the phone,
    /// another Mac): then the Designs tab falls back to the bundled designs.
    var available: Bool {
        FileManager.default.fileExists(atPath: root.appendingPathComponent("cad/compare/designs.py").path)
    }

    private init() {
        guard available else { return }
        refresh()
        watch()
    }

    /// Re-reads the design list and redraws every render. The Refresh button.
    func refresh() {
        Task {
            if let data = await run(["cad/compare/designs.py", "--json"]).data,
               let list = try? JSONDecoder().decode([RepoDesign].self, from: data) {
                designs = list
                if let current = open { open = list.first { $0.id == current.id } ?? current }
            }
            generation += 1
        }
    }

    /// "gripper", "glove hand", "demo-gripper-gen-00": the best match comes
    /// forward full screen in the workbench.
    func open(name: String) {
        Task {
            let result = await run(["cad/compare/designs.py", "--match", name])
            guard let data = result.data, let design = try? JSONDecoder().decode(RepoDesign.self, from: data) else {
                status = "No design matches “\(name)”"
                return
            }
            if !designs.contains(where: { $0.id == design.id }) { refresh() }
            open = design
            NSApp.activate(ignoringOtherApps: true)
            if let window = NSApp.windows.first(where: { $0.isVisible && $0.canBecomeMain }) ?? NSApp.windows.first {
                window.makeKeyAndOrderFront(nil)
                window.collectionBehavior.insert(.fullScreenPrimary)
                if !window.styleMask.contains(.fullScreen) { window.toggleFullScreen(nil) }
            }
        }
    }

    func reexport(_ design: RepoDesign) {
        Task { await export([design]) }
    }

    private func export(_ targets: [RepoDesign]) async {
        for design in targets {
            status = "Exporting \(design.generation) STL…"
            let result = await run(["cad/compare/designs.py", "--export", design.id])
            status = result.ok ? "" : "OpenSCAD failed on \(design.generation): \(result.error)"
        }
        refresh()
    }

    // MARK: - Watching the checkout

    private func watch() {
        let paths = ["cad/openscad", "cad/compare", "pebbles/agent"].map { root.appendingPathComponent($0).path } as CFArray
        var context = FSEventStreamContext(version: 0, info: Unmanaged.passUnretained(self).toOpaque(),
                                           retain: nil, release: nil, copyDescription: nil)
        let callback: FSEventStreamCallback = { _, info, count, paths, _, _ in
            guard let info else { return }
            let me = Unmanaged<RepoDesigns>.fromOpaque(info).takeUnretainedValue()
            let changed = (unsafeBitCast(paths, to: NSArray.self) as? [String] ?? []).prefix(count)
            Task { @MainActor in me.changed(Array(changed)) }
        }
        stream = FSEventStreamCreate(nil, callback, &context, paths, FSEventStreamEventId(kFSEventStreamEventIdSinceNow),
                                     0.2, UInt32(kFSEventStreamCreateFlagUseCFTypes | kFSEventStreamCreateFlagFileEvents))
        guard let stream else { return }
        FSEventStreamSetDispatchQueue(stream, .main)
        FSEventStreamStart(stream)
    }

    private func changed(_ paths: [String]) {
        let relevant = paths.filter { path in
            !path.contains("/__pycache__/") && !path.hasSuffix("designs.json") && !path.hasSuffix(".zip")
                && !path.contains("/render/") && !path.contains("/compare/gen_")
        }
        guard !relevant.isEmpty else { return }
        pending.formUnion(relevant)
        debounce?.cancel()
        let work = DispatchWorkItem { [weak self] in Task { @MainActor in self?.flush() } }
        debounce = work
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.4, execute: work)
    }

    /// A saved .scad re-exports every generation in that folder that could
    /// read it (its own file, or a shared include); anything else redraws.
    private func flush() {
        let saved = pending.filter { $0.hasSuffix(".scad") }
        pending.removeAll()
        let stale = designs.filter { design in
            let folder = root.appendingPathComponent(design.folder).path + "/"
            return saved.contains { $0 == root.appendingPathComponent(design.scad).path
                || ($0.hasPrefix(folder) && !URL(fileURLWithPath: $0).lastPathComponent.hasPrefix("gen_")) }
        }
        if stale.isEmpty { refresh() } else { Task { await export(stale) } }
    }

    // MARK: - Running the registry

    private struct Output { var ok: Bool; var data: Data?; var error: String }

    private func run(_ args: [String]) async -> Output {
        let root = root
        return await withCheckedContinuation { continuation in
            DispatchQueue.global(qos: .userInitiated).async {
                let process = Process()
                process.executableURL = URL(fileURLWithPath: "/usr/bin/env")
                process.arguments = ["python3"] + args
                process.currentDirectoryURL = root
                var env = ProcessInfo.processInfo.environment
                env["PATH"] = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:" + (env["PATH"] ?? "")
                process.environment = env
                let out = Pipe(), err = Pipe()
                process.standardOutput = out
                process.standardError = err
                do { try process.run() } catch {
                    continuation.resume(returning: Output(ok: false, data: nil, error: error.localizedDescription))
                    return
                }
                let data = out.fileHandleForReading.readDataToEndOfFile()
                let message = String(decoding: err.fileHandleForReading.readDataToEndOfFile(), as: UTF8.self)
                process.waitUntilExit()
                let ok = process.terminationStatus == 0
                continuation.resume(returning: Output(ok: ok, data: ok ? data : nil,
                                                      error: message.split(separator: "\n").last.map(String.init) ?? ""))
            }
        }
    }
}

// MARK: - The viewer page

/// Serves the checkout to the web views as `hhrepo://repo/<path>`, so
/// cad/compare/viewer.html can import its modules and fetch the STLs without
/// a local server, and always reads the file as it is on disk now.
final class RepoSchemeHandler: NSObject, WKURLSchemeHandler {
    let root: URL
    init(root: URL) { self.root = root }

    func webView(_ webView: WKWebView, start task: WKURLSchemeTask) {
        guard let url = task.request.url else { return }
        let file = root.appendingPathComponent(url.path).standardizedFileURL
        guard file.path.hasPrefix(root.standardizedFileURL.path), let data = try? Data(contentsOf: file) else {
            task.didReceive(HTTPURLResponse(url: url, statusCode: 404, httpVersion: nil, headerFields: nil)!)
            task.didFinish()
            return
        }
        let types = ["html": "text/html", "js": "text/javascript", "json": "application/json",
                     "stl": "application/octet-stream", "scad": "text/plain", "png": "image/png"]
        let type = types[file.pathExtension.lowercased()] ?? "application/octet-stream"
        task.didReceive(HTTPURLResponse(url: url, statusCode: 200, httpVersion: nil,
                                        headerFields: ["Content-Type": type, "Cache-Control": "no-store"])!)
        task.didReceive(data)
        task.didFinish()
    }

    func webView(_ webView: WKWebView, stop task: WKURLSchemeTask) {}
}

/// Keeps the workbench's panes on one camera: an orbit in one is replayed in
/// the other.
final class CameraLink {
    private var views: [WeakWeb] = []
    private struct WeakWeb { weak var view: WKWebView? }

    func add(_ view: WKWebView) {
        views.removeAll { $0.view == nil || $0.view === view }
        views.append(WeakWeb(view: view))
    }

    func moved(_ camera: Any, from source: WKWebView) {
        guard let data = try? JSONSerialization.data(withJSONObject: camera),
              let json = String(data: data, encoding: .utf8) else { return }
        for view in views.compactMap(\.view) where view !== source {
            view.evaluateJavaScript("hh.setCamera(\(json))")
        }
    }
}

/// cad/compare/viewer.html on one design in one mode: "web" (the concept),
/// "stl" (the OpenSCAD export) or "diff". The same page render_compare uses.
struct CompareWebView: NSViewRepresentable {
    let design: String
    let mode: String
    var view = "iso"
    var live = true
    var link: CameraLink?
    let generation: Int

    func makeCoordinator() -> Coordinator { Coordinator(link: link) }

    func makeNSView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.setURLSchemeHandler(RepoSchemeHandler(root: RepoDesigns.shared.root), forURLScheme: "hhrepo")
        config.userContentController.add(context.coordinator, name: "hh")
        let web = WKWebView(frame: .zero, configuration: config)
        web.setValue(false, forKey: "drawsBackground")
        context.coordinator.web = web
        link?.add(web)
        return web
    }

    func updateNSView(_ web: WKWebView, context: Context) {
        let c = context.coordinator
        if c.loaded != design + mode {
            c.loaded = design + mode
            var parts = URLComponents(string: "hhrepo://repo/cad/compare/viewer.html")!
            parts.queryItems = [.init(name: "design", value: design), .init(name: "mode", value: mode),
                                .init(name: "view", value: view)] + (live ? [.init(name: "live", value: "1")] : [])
            web.load(URLRequest(url: parts.url!))
            (c.view, c.generation) = (view, generation)
            return
        }
        if c.view != view {
            c.view = view
            web.evaluateJavaScript("hh.setView('\(view)')")
        }
        if c.generation != generation {
            c.generation = generation
            web.evaluateJavaScript("hh.reload()")
        }
    }

    final class Coordinator: NSObject, WKScriptMessageHandler {
        weak var web: WKWebView?
        let link: CameraLink?
        var loaded = "", view = "", generation = -1
        init(link: CameraLink?) { self.link = link }

        func userContentController(_ controller: WKUserContentController, didReceive message: WKScriptMessage) {
            guard let body = message.body as? [String: Any], let camera = body["camera"], let web else { return }
            link?.moved(camera, from: web)
        }
    }
}

// MARK: - Screens

private let backdrop = Color(red: 0.05, green: 0.10, blue: 0.13)

private struct InProgressBadge: View {
    let pebbles: [RepoDesign.Pebble]
    var body: some View {
        Label("In progress", systemImage: "hammer.fill")
            .font(.caption.weight(.semibold))
            .padding(.horizontal, 8).padding(.vertical, 4)
            .background(Color.orange.opacity(0.85), in: Capsule())
            .foregroundStyle(.black)
            .help(pebbles.map { "\($0.id): \($0.summary)" }.joined(separator: "\n"))
    }
}

/// The Mac's Designs tab: every design in the checkout, each card showing its
/// current web render and STL render, redrawn on every save. Click one for
/// the full-screen workbench.
struct RepoDesignsScreen: View {
    @ObservedObject private var designs = RepoDesigns.shared

    var body: some View {
        NavigationStack {
            ScrollView {
                LazyVGrid(columns: [GridItem(.adaptive(minimum: 460), spacing: 16)], spacing: 16) {
                    ForEach(designs.designs) { design in card(design) }
                }
                .padding(20)
            }
            .background(backdrop.ignoresSafeArea())
            .navigationTitle("Designs")
            .toolbar {
                ToolbarItem {
                    if !designs.status.isEmpty { Text(designs.status).font(.caption).foregroundStyle(.secondary) }
                }
                ToolbarItem {
                    Button { designs.refresh() } label: { Label("Refresh", systemImage: "arrow.clockwise") }
                        .keyboardShortcut("r")
                        .help("Re-read every design from the checkout and redraw both renders")
                }
            }
        }
    }

    private func card(_ design: RepoDesign) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text(design.name).font(.headline).lineLimit(1)
                Spacer()
                if !design.in_progress.isEmpty { InProgressBadge(pebbles: design.in_progress) }
            }
            HStack(spacing: 8) {
                pane("Web concept", CompareWebView(design: design.id, mode: "web", live: false, generation: designs.generation))
                pane("OpenSCAD STL", CompareWebView(design: design.id, mode: "stl", live: false, generation: designs.generation))
            }
            .frame(height: 220)
        }
        .padding(14)
        .background(Color.white.opacity(0.05), in: RoundedRectangle(cornerRadius: 14, style: .continuous))
        .contentShape(Rectangle())
        .overlay { Color.clear.contentShape(Rectangle()).onTapGesture { designs.open = design } }
    }

    private func pane(_ title: String, _ web: CompareWebView) -> some View {
        web.frame(minWidth: 0, maxWidth: .infinity)
            .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
            .overlay(alignment: .bottomLeading) {
                Text(title).font(.caption2.weight(.semibold)).padding(6).foregroundStyle(.secondary)
            }
    }
}

/// Full screen on one design: the web concept large on the left, the
/// OpenSCAD STL beside it on the same camera (orbit either, both move), the
/// silhouette diff on request. Both redraw on every save.
struct DesignWorkbenchView: View {
    let design: RepoDesign
    @ObservedObject private var designs = RepoDesigns.shared
    @State private var view = "iso"
    @State private var diff = false
    @State private var link = CameraLink()

    var body: some View {
        VStack(spacing: 0) {
            bar
            GeometryReader { geometry in
                HStack(spacing: 2) {
                    pane("JavaScript model", mode: "web")
                        .frame(width: max(0, (geometry.size.width - 2) / 2), height: geometry.size.height)
                        .clipped()
                    pane(diff ? "Difference · pink JavaScript · cyan OpenSCAD" : "OpenSCAD model", mode: diff ? "diff" : "stl")
                        .frame(width: max(0, (geometry.size.width - 2) / 2), height: geometry.size.height)
                        .clipped()
                }
            }
        }
        .background(backdrop.ignoresSafeArea())
    }

    private var bar: some View {
        HStack(spacing: 14) {
            Button { designs.open = nil } label: { Label("Designs", systemImage: "chevron.left") }
                .keyboardShortcut(.cancelAction)
            Menu {
                ForEach(designs.designs) { choice in
                    Button(choice.name) { designs.open = choice }
                }
            } label: {
                Label(design.name, systemImage: "chevron.down").font(.headline).lineLimit(1)
            }
            if !design.in_progress.isEmpty { InProgressBadge(pebbles: design.in_progress) }
            Spacer()
            if !designs.status.isEmpty { Text(designs.status).font(.caption).foregroundStyle(.secondary).lineLimit(1) }
            Picker("View", selection: $view) {
                ForEach(["front", "side", "top", "iso", "exploded"], id: \.self) { Text($0.capitalized).tag($0) }
            }
            .pickerStyle(.segmented)
            .frame(width: 380)
            Toggle("Diff", isOn: $diff).toggleStyle(.button)
            Button { designs.reexport(design) } label: { Label("Re-export", systemImage: "cube") }
                .help("Run OpenSCAD on \(design.scad) now")
            Button { designs.refresh() } label: { Label("Refresh", systemImage: "arrow.clockwise") }
                .keyboardShortcut("r")
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
        .background(.ultraThinMaterial)
    }

    private func pane(_ title: String, mode: String) -> some View {
        CompareWebView(design: design.id, mode: mode, view: view, link: link, generation: designs.generation)
            .id(design.id + mode)
            .overlay(alignment: .topLeading) {
                Text(title).font(.caption.weight(.semibold)).padding(8)
                    .background(.black.opacity(0.4), in: RoundedRectangle(cornerRadius: 6)).padding(10)
            }
    }
}
#endif
