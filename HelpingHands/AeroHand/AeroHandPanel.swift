#if os(macOS)
import SwiftUI

/// Every aero_hand command as a button (Mac only). The same commands answer
/// `helpinghands://aero/…` URLs, which `scripts/app.sh` opens for the voice session.
struct AeroHandPanel: View {
    @ObservedObject private var runner = AeroHandRunner.shared
    @State private var song = ""

    private let columns = [GridItem(.adaptive(minimum: 110), spacing: 8)]

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            status
            section("Performance") {
                button(.perform(song: nil), "music.note")
                button(.routine, "list.number")
                button(.listen, "ear")
            }
            HStack {
                TextField("Song name", text: $song)
                    .textFieldStyle(.roundedBorder)
                    .onSubmit(performSong)
                Button("Perform song", action: performSong)
                    .disabled(song.trimmingCharacters(in: .whitespaces).isEmpty)
            }
            section("Poses") {
                button(.count, "textformat.123")
                ForEach(runner.poses, id: \.self) { name in
                    button(.pose(name), nil, label: name)
                }
            }
            section("Teleop & setup") {
                button(.teleop(dryRun: false), "camera")
                button(.teleop(dryRun: true), "hand.raised")
                button(.home, "house")
            }
            ScrollViewReader { proxy in
                ScrollView {
                    Text(runner.log.isEmpty ? "Output appears here." : runner.log)
                        .font(.caption.monospaced())
                        .foregroundStyle(runner.log.isEmpty ? .secondary : .primary)
                        .textSelection(.enabled)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(8)
                    Color.clear.frame(height: 1).id("end")
                }
                .background(.black.opacity(0.3), in: RoundedRectangle(cornerRadius: 8))
                .onChange(of: runner.log) { _, _ in proxy.scrollTo("end") }
            }
        }
        .padding(20)
        .frame(minWidth: 520, minHeight: 560)
        .background(Color(red: 0.05, green: 0.12, blue: 0.16).ignoresSafeArea())
        .navigationTitle("Aero Hand")
        .onAppear { if runner.poses.isEmpty { runner.loadPoses() } }
    }

    private var status: some View {
        HStack(spacing: 12) {
            Image(systemName: runner.running == nil ? "hand.raised" : "hand.raised.fill")
                .font(.title2)
                .foregroundStyle(Color.accentColor)
            Text(runner.running?.title ?? "Idle")
                .font(.headline)
            Spacer()
            Toggle("Full speed", isOn: $runner.fullSpeed)
                .toggleStyle(.switch)
                .help("Off: servos capped at 50% (hand_speed.py). Resets every launch.")
            Button(role: .destructive) { runner.stop() } label: {
                Label("Stop", systemImage: "stop.fill")
            }
            .keyboardShortcut(.escape, modifiers: [])
            .disabled(runner.running == nil)
        }
    }

    private func section<Content: View>(_ title: String, @ViewBuilder content: () -> Content) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title).font(.subheadline.weight(.semibold)).foregroundStyle(.secondary)
            LazyVGrid(columns: columns, alignment: .leading, spacing: 8, content: content)
        }
    }

    private func button(_ command: AeroCommand, _ icon: String?, label: String? = nil) -> some View {
        Button { runner.run(command) } label: {
            Group {
                if let icon {
                    Label(label ?? command.title, systemImage: icon)
                } else {
                    Text(label ?? command.title)
                }
            }
            .frame(maxWidth: .infinity)
        }
        .buttonStyle(.bordered)
        .tint(runner.running == command ? Color.accentColor : nil)
    }

    private func performSong() {
        let name = song.trimmingCharacters(in: .whitespaces)
        guard !name.isEmpty else { return }
        runner.run(.perform(song: name))
    }
}

/// Routes `helpinghands://aero/…` to the runner without SwiftUI opening a new
/// window for each URL (which `onOpenURL` on a WindowGroup does on the Mac).
final class AeroURLDelegate: NSObject, NSApplicationDelegate {
    func applicationWillFinishLaunching(_ notification: Notification) {
        NSAppleEventManager.shared().setEventHandler(
            self, andSelector: #selector(handleURL(_:reply:)),
            forEventClass: AEEventClass(kInternetEventClass), andEventID: AEEventID(kAEGetURL))
    }

    @objc private func handleURL(_ event: NSAppleEventDescriptor, reply: NSAppleEventDescriptor) {
        guard let string = event.paramDescriptor(forKeyword: keyDirectObject)?.stringValue,
              let url = URL(string: string) else { return }
        Task { @MainActor in AeroHandRunner.shared.handle(url: url) }
    }
}
#endif
