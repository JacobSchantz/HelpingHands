import SwiftUI
import UniformTypeIdentifiers
#if canImport(UIKit)
import UIKit
#elseif canImport(AppKit)
import AppKit
#endif

/// The plan library: everything under `plans/` plus anything added on device.
/// Opening a row starts reading it aloud — there is no second "play" tap,
/// because the point of the screen is to stop needing the screen.
struct PlansScreen: View {
    @StateObject private var library = PlanLibrary()
    @State private var importing = false
    @State private var pasting = false

    private static let importTypes: [UTType] = {
        var seen = Set<String>()
        let types = ([UTType.plainText, UTType.text] + PlanLibrary.readableExtensions
            .compactMap { UTType(filenameExtension: $0) })
            .filter { seen.insert($0.identifier).inserted }
        return types.isEmpty ? [.data] : types
    }()

    var body: some View {
        List {
            Section {
                ForEach(library.bundled) { row($0) }
            } header: {
                Text("From the repo")
            } footer: {
                Text("Markdown under plans/, staged into the app at build time.")
            }

            Section {
                if library.imported.isEmpty {
                    Text("Paste a plan or import a .md / .txt file to listen to it here.")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                } else {
                    ForEach(library.imported) { plan in
                        row(plan)
                            .swipeActions {
                                Button(role: .destructive) {
                                    library.delete(plan)
                                } label: {
                                    Label("Delete", systemImage: "trash")
                                }
                            }
                    }
                }
            } header: {
                Text("Added on this device")
            } footer: {
                if let error = library.lastImportError {
                    Text(error).foregroundStyle(.red)
                }
            }
        }
        .navigationTitle("Plans")
        .toolbar {
            ToolbarItem {
                Menu {
                    Button {
                        pasting = true
                    } label: {
                        Label("Paste a plan", systemImage: "doc.on.clipboard")
                    }
                    Button {
                        importing = true
                    } label: {
                        Label("Import a file", systemImage: "folder")
                    }
                } label: {
                    Label("Add", systemImage: "plus")
                }
            }
        }
        .fileImporter(isPresented: $importing,
                      allowedContentTypes: Self.importTypes,
                      allowsMultipleSelection: true) { result in
            if case .success(let urls) = result {
                urls.forEach(library.importFile(at:))
            }
        }
        .sheet(isPresented: $pasting) {
            PlanPasteView { text, title in
                library.addPasted(text, title: title)
            }
        }
        .refreshable { library.reload() }
    }

    private func row(_ plan: PlanDocument) -> some View {
        NavigationLink {
            PlanListenerView(plan: plan)
        } label: {
            HStack(spacing: 12) {
                Image(systemName: "waveform")
                    .foregroundStyle(Color.accentColor)
                    .frame(width: 22)
                VStack(alignment: .leading, spacing: 2) {
                    Text(plan.title)
                    Text("\(plan.summaryLine) · \(plan.source)")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
        }
        .accessibilityLabel("\(plan.title). \(plan.summaryLine). Opens and starts reading aloud.")
    }
}

/// Dropping a plan in by hand: paste the text, give it a name, listen.
struct PlanPasteView: View {
    var onSave: (String, String) -> Void

    @Environment(\.dismiss) private var dismiss
    @State private var title = ""
    @State private var text = ""

    var body: some View {
        NavigationStack {
            Form {
                Section("Name") {
                    TextField("Tool caddy", text: $title)
                }
                Section("Plan") {
                    TextEditor(text: $text)
                        .frame(minHeight: 220)
                        .font(.body.monospaced())
                }
                Section {
                    Button {
                        text = PlanClipboard.read() ?? text
                    } label: {
                        Label("Paste from clipboard", systemImage: "doc.on.clipboard")
                    }
                }
            }
            .navigationTitle("Add a plan")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Save") {
                        onSave(text, title)
                        dismiss()
                    }
                    .disabled(text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                }
            }
        }
    }
}

/// One clipboard helper for both platforms.
enum PlanClipboard {
    static func read() -> String? {
        #if canImport(UIKit)
        return UIPasteboard.general.string
        #elseif canImport(AppKit)
        return NSPasteboard.general.string(forType: .string)
        #else
        return nil
        #endif
    }

    static func write(_ text: String) {
        #if canImport(UIKit)
        UIPasteboard.general.string = text
        #elseif canImport(AppKit)
        NSPasteboard.general.clearContents()
        NSPasteboard.general.setString(text, forType: .string)
        #endif
    }
}
