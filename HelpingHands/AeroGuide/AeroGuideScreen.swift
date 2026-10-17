import SwiftUI
import UniformTypeIdentifiers
import WebKit

/// The Aero Hand build guide from third_party/aero_hand/guide: a gallery of the
/// build-session animations and diagrams by guide page, plus the assembly PDF.
/// The folder is staged into the bundle as AeroGuide/ by
/// Scripts/stage_aero_guide.py and served over a private `aeroguide://` scheme
/// so the 3D pages can fetch their meshes (file:// pages can't).
struct AeroGuideScreen: View {
    enum Start { case gallery, pdf }

    var start: Start = .gallery
    @StateObject private var browser = GuideBrowser()

    var body: some View {
        Group {
            if GuideBrowser.root != nil {
                GuideWebView(webView: browser.webView)
                    .ignoresSafeArea(edges: .bottom)
            } else {
                ContentUnavailableView(
                    "Guide not bundled",
                    systemImage: "book.closed",
                    description: Text("Build again so Scripts/stage_aero_guide.py copies third_party/aero_hand/guide into the app.")
                )
            }
        }
        .navigationTitle("Aero Hand guide")
        #if os(iOS)
        .navigationBarTitleDisplayMode(.inline)
        #endif
        .toolbar {
            ToolbarItemGroup(placement: .primaryAction) {
                Button {
                    browser.webView.goBack()
                } label: {
                    Label("Back", systemImage: "chevron.backward")
                }
                .disabled(!browser.canGoBack)
                Button {
                    browser.open("index.html")
                } label: {
                    Label("Gallery", systemImage: "square.grid.2x2")
                }
                Button {
                    browser.open(GuideBrowser.pdf)
                } label: {
                    Label("PDF", systemImage: "doc.richtext")
                }
            }
        }
        .onAppear {
            if browser.webView.url == nil {
                browser.open(start == .pdf ? GuideBrowser.pdf : "index.html")
            }
        }
    }
}

@MainActor
final class GuideBrowser: ObservableObject {
    static let scheme = "aeroguide"
    static let pdf = "aero_guide_original.pdf"
    static var root: URL? {
        Bundle.main.resourceURL.map { $0.appendingPathComponent("AeroGuide", isDirectory: true) }
            .flatMap { FileManager.default.fileExists(atPath: $0.path) ? $0 : nil }
    }

    let webView: WKWebView
    @Published var canGoBack = false
    private var observation: NSKeyValueObservation?

    init() {
        let config = WKWebViewConfiguration()
        if let root = Self.root {
            config.setURLSchemeHandler(GuideSchemeHandler(root: root), forURLScheme: Self.scheme)
        }
        #if os(iOS)
        config.allowsInlineMediaPlayback = true
        #endif
        webView = WKWebView(frame: .zero, configuration: config)
        webView.allowsBackForwardNavigationGestures = true
        observation = webView.observe(\.canGoBack, options: [.initial, .new]) { [weak self] view, _ in
            let value = view.canGoBack
            Task { @MainActor in self?.canGoBack = value }
        }
    }

    func open(_ path: String) {
        guard let url = URL(string: "\(Self.scheme)://guide/\(path)") else { return }
        webView.load(URLRequest(url: url))
    }
}

/// Serves AeroGuide/ from the bundle. Missing files answer 404 so pages' own
/// `onerror` fallbacks (e.g. an unrendered page image) kick in.
private final class GuideSchemeHandler: NSObject, WKURLSchemeHandler {
    private let root: URL

    init(root: URL) {
        self.root = root.standardizedFileURL
    }

    func webView(_ webView: WKWebView, start task: WKURLSchemeTask) {
        guard let url = task.request.url else { return }
        let path = url.path.isEmpty || url.path == "/" ? "index.html" : String(url.path.dropFirst())
        let file = root.appendingPathComponent(path).standardizedFileURL
        let inside = file.path.hasPrefix(root.path + "/")
        guard inside, let data = try? Data(contentsOf: file, options: .mappedIfSafe) else {
            task.didReceive(HTTPURLResponse(url: url, statusCode: 404, httpVersion: "HTTP/1.1", headerFields: nil)!)
            task.didFinish()
            return
        }
        let mime = UTType(filenameExtension: file.pathExtension)?.preferredMIMEType ?? "application/octet-stream"
        let headers = [
            "Content-Type": mime,
            "Content-Length": String(data.count),
            "Access-Control-Allow-Origin": "*",
        ]
        task.didReceive(HTTPURLResponse(url: url, statusCode: 200, httpVersion: "HTTP/1.1", headerFields: headers)!)
        task.didReceive(data)
        task.didFinish()
    }

    func webView(_ webView: WKWebView, stop task: WKURLSchemeTask) {}
}

#if os(iOS)
private struct GuideWebView: UIViewRepresentable {
    let webView: WKWebView
    func makeUIView(context: Context) -> WKWebView { webView }
    func updateUIView(_ view: WKWebView, context: Context) {}
}
#else
private struct GuideWebView: NSViewRepresentable {
    let webView: WKWebView
    func makeNSView(context: Context) -> WKWebView { webView }
    func updateNSView(_ view: WKWebView, context: Context) {}
}
#endif
