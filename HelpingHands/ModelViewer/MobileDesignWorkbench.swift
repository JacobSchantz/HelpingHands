#if os(iOS)
import SwiftUI
import WebKit

/// The same web geometry and OpenSCAD exports as the Mac, bundled for offline viewing.
struct MobileDesignWorkbench: View {
    private struct Design: Decodable, Identifiable {
        let id: String
        let name: String
        let newest: Bool
    }
    private struct Registry: Decodable { let designs: [Design] }
    @State private var designs: [Design] = []
    @State private var selected = ""
    @State private var mode = "web"
    @State private var revision = 0
    @State private var showFiles = false
    private let root = Bundle.main.resourceURL!.appendingPathComponent("DesignViewer")

    var body: some View {
        NavigationStack {
            VStack(spacing: 8) {
                if designs.isEmpty {
                    ContentUnavailableView("No interactive designs in this build", systemImage: "cube.transparent",
                                           description: Text("Use CAD files to browse the bundled models."))
                } else {
                    Picker("Design", selection: $selected) {
                        ForEach(designs) { Text($0.name).tag($0.id) }
                    }
                    .pickerStyle(.menu)
                    .padding(.horizontal)
                    Picker("Model", selection: $mode) {
                        Text("Web model").tag("web")
                        Text("OpenSCAD").tag("stl")
                    }
                    .pickerStyle(.segmented)
                    .padding(.horizontal)
                    BundledDesignWebView(root: root, design: selected, mode: mode, revision: revision)
                    Text("Drag to rotate · Pinch to zoom")
                        .font(.caption).foregroundStyle(.secondary)
                }
            }
            .background(Color(red: 0.05, green: 0.10, blue: 0.13))
            .navigationTitle("Designs")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("CAD files") { showFiles = true }
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button { revision += 1 } label: { Label("Reset view", systemImage: "arrow.counterclockwise") }
                }
            }
            .sheet(isPresented: $showFiles) { DesignViewerScreen() }
            .task {
                guard designs.isEmpty,
                      let data = try? Data(contentsOf: root.appendingPathComponent("cad/compare/designs.json")),
                      let registry = try? JSONDecoder().decode(Registry.self, from: data) else { return }
                designs = registry.designs.sorted { $0.name.localizedStandardCompare($1.name) == .orderedAscending }
                selected = designs.first { $0.id.hasPrefix("glove-hand-") && $0.newest }?.id ?? designs.first?.id ?? ""
            }
        }
    }
}

private struct BundledDesignWebView: UIViewRepresentable {
    let root: URL
    let design: String
    let mode: String
    let revision: Int

    func makeUIView(context: Context) -> WKWebView {
        let configuration = WKWebViewConfiguration()
        configuration.setURLSchemeHandler(BundledDesignScheme(root: root), forURLScheme: "hhdesign")
        let web = WKWebView(frame: .zero, configuration: configuration)
        web.isOpaque = false
        web.backgroundColor = .clear
        web.scrollView.isScrollEnabled = false
        return web
    }

    func updateUIView(_ web: WKWebView, context: Context) {
        var url = URLComponents(string: "hhdesign://bundle/cad/compare/viewer.html")!
        url.queryItems = [.init(name: "design", value: design), .init(name: "mode", value: mode),
                          .init(name: "live", value: "1"), .init(name: "revision", value: String(revision))]
        guard web.url != url.url else { return }
        web.load(URLRequest(url: url.url!))
    }
}

private final class BundledDesignScheme: NSObject, WKURLSchemeHandler {
    let root: URL
    init(root: URL) { self.root = root.standardizedFileURL }

    func webView(_ webView: WKWebView, start task: WKURLSchemeTask) {
        guard let url = task.request.url else { return }
        let file = root.appendingPathComponent(url.path).standardizedFileURL
        guard file.path.hasPrefix(root.path + "/"), let data = try? Data(contentsOf: file) else {
            task.didFailWithError(URLError(.fileDoesNotExist))
            return
        }
        let types = ["html": "text/html", "js": "text/javascript", "json": "application/json", "stl": "application/octet-stream", "scad": "text/plain"]
        task.didReceive(HTTPURLResponse(url: url, statusCode: 200, httpVersion: nil,
                                       headerFields: ["Content-Type": types[file.pathExtension] ?? "application/octet-stream"])!)
        task.didReceive(data)
        task.didFinish()
    }

    func webView(_ webView: WKWebView, stop task: WKURLSchemeTask) {}
}
#endif
