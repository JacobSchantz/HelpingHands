#if os(macOS)
import SwiftUI

/// Every aero_hand command as a button (Mac only). The same commands answer
/// `helpinghands://aero/…` URLs, which `scripts/app.sh` opens for the voice session.
struct AeroHandPanel: View {
    @ObservedObject private var runner = AeroHandRunner.shared

    // Read from about four feet away: big type, big targets, generous spacing.
    private let columns = [GridItem(.adaptive(minimum: 300), spacing: 20)]
    private let bodyFont = Font.system(size: 30, weight: .semibold)

    var body: some View {
        VStack(alignment: .leading, spacing: 24) {
            status  // pinned so Stop stays on screen
            ScrollView { controls.padding(.trailing, 12) }
            log
        }
        .padding(40)
        .frame(minWidth: 1000, minHeight: 800)
        .background(FillScreen())
        .background(Color(red: 0.05, green: 0.12, blue: 0.16).ignoresSafeArea())
        .navigationTitle("Aero Hand")
        .onAppear { if runner.poses.isEmpty { runner.loadPoses() } }
    }

    private var controls: some View {
        VStack(alignment: .leading, spacing: 32) {
            VStack(alignment: .leading, spacing: 16) {
                sectionTitle("Performance")
                HStack(spacing: 20) {
                    bigButton(.test, "list.number")
                    bigButton(.dance(song: nil), "music.note")
                }
            }
            section("Poses") {
                button(.count, "textformat.123")
                ForEach(runner.poses, id: \.self) { name in
                    button(.pose(name), nil, label: name)
                }
            }
            section("Games") {
                button(.rps(dryRun: false), "hand.raised.fingers.spread")
            }
            section("Teleop & setup") {
                button(.teleop(dryRun: false), "camera")
                button(.teleop(dryRun: true), "hand.raised")
                button(.home, "house")
            }
        }
    }

    private var log: some View {
        ScrollViewReader { proxy in
            ScrollView {
                Text(runner.log.isEmpty ? "Output appears here." : runner.log)
                    .font(.system(size: 20, design: .monospaced))
                    .foregroundStyle(runner.log.isEmpty ? .secondary : .primary)
                    .textSelection(.enabled)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(16)
                Color.clear.frame(height: 1).id("end")
            }
            .frame(height: 160)
            .background(.black.opacity(0.4), in: RoundedRectangle(cornerRadius: 14))
            .onChange(of: runner.log) { _, _ in proxy.scrollTo("end") }
        }
    }

    private var status: some View {
        HStack(spacing: 28) {
            Image(systemName: runner.running == nil ? "hand.raised" : "hand.raised.fill")
                .font(.system(size: 56))
                .foregroundStyle(runner.running == nil ? .white : .green)
            Text(runner.running?.title ?? "Idle")
                .font(.system(size: 48, weight: .bold))
                .foregroundStyle(runner.running == nil ? .white : .green)
                .lineLimit(1)
                .minimumScaleFactor(0.5)
            Spacer()
            Toggle(isOn: $runner.fullSpeed) {
                Text("Full speed").font(bodyFont).foregroundStyle(runner.fullSpeed ? .orange : .white)
            }
            .toggleStyle(.switch)
            .controlSize(.large)
            .help("Off: servos capped at 50% (hand_speed.py). Resets every launch.")
            Button(role: .destructive) { runner.stop() } label: {
                Label("Stop", systemImage: "stop.fill")
                    .font(.system(size: 34, weight: .bold))
                    .padding(.horizontal, 28)
                    .frame(height: 88)
            }
            .buttonStyle(.borderedProminent)
            .tint(.red)
            .keyboardShortcut(.escape, modifiers: [])
            .disabled(runner.running == nil)
        }
    }

    private func section<Content: View>(_ title: String, @ViewBuilder content: () -> Content) -> some View {
        VStack(alignment: .leading, spacing: 16) {
            sectionTitle(title)
            LazyVGrid(columns: columns, alignment: .leading, spacing: 20, content: content)
        }
    }

    private func sectionTitle(_ title: String) -> some View {
        Text(title).font(.system(size: 38, weight: .heavy)).foregroundStyle(.white.opacity(0.85))
    }

    private func bigButton(_ command: AeroCommand, _ icon: String) -> some View {
        Button { runner.run(command) } label: {
            Label(command.title, systemImage: icon)
                .font(.system(size: 48, weight: .bold))
                .frame(maxWidth: .infinity, minHeight: 160)
        }
        .buttonStyle(.bordered)
        .controlSize(.large)
        .tint(runner.running == command ? Color.accentColor : nil)
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
            .font(bodyFont)
            .lineLimit(1)
            .minimumScaleFactor(0.6)
            .frame(maxWidth: .infinity, minHeight: 96)
        }
        .buttonStyle(.bordered)
        .controlSize(.large)
        .tint(runner.running == command ? Color.accentColor : nil)
    }
}

/// Grows the Aero Hand window to most of the screen the first time it opens
/// (macOS 14 has no `defaultWindowPlacement`).
private struct FillScreen: NSViewRepresentable {
    func makeNSView(context: Context) -> NSView {
        let view = NSView()
        DispatchQueue.main.async {
            guard let window = view.window, let screen = window.screen ?? NSScreen.main else { return }
            window.setFrame(screen.visibleFrame.insetBy(dx: screen.visibleFrame.width * 0.04,
                                                        dy: screen.visibleFrame.height * 0.04),
                            display: true)
        }
        return view
    }

    func updateNSView(_ nsView: NSView, context: Context) {}
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
