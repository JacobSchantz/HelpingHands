#if os(macOS)
import SwiftUI

/// Every aero_hand command as a button (Mac only) — the Aero Hand tab. The same commands answer
/// `helpinghands://aero/…` URLs, which `scripts/app.sh` opens for the voice session.
struct AeroHandPanel: View {
    @ObservedObject private var runner = AeroHandRunner.shared
    @State private var showLog = false  // Jake: hidden by default, the buttons get the room

    // Read from about four feet away, and everything on one screen: the buttons
    // share whatever height is left, so a bigger window means bigger buttons.
    private let spacing: CGFloat = 16
    private let titleHeight: CGFloat = 40
    private let scripts: [(AeroCommand, String)] = [
        (.test, "list.number"), (.dance(song: nil), "music.note"), (.count, "textformat.123"),
        (.home, "house.fill"), (.teleop(dryRun: false), "camera"),
    ]

    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            status
            GeometryReader { geo in grid(in: geo.size) }
            if showLog { log }
        }
        .padding(32)
        .frame(minWidth: 1000, minHeight: 700)
        .background(FillScreen())
        .background(Color(red: 0.05, green: 0.12, blue: 0.16).ignoresSafeArea())
        .navigationTitle("Aero Hand")
        .onAppear { if runner.poses.isEmpty { runner.loadPoses() } }
    }

    /// pose.py's button poses, then Relax (relax.sh, zero torque) as the last pose.
    private var poses: [(AeroCommand, String)] {
        runner.poses.map { (.pose($0), $0) } + [(.relax, "relax")]
    }

    /// Poses on top, then Scripts and Games sharing the last row.
    private func grid(in size: CGSize) -> some View {
        let poses = poses
        let columns = max(1, min(poses.count, Int(size.width / 210)))
        let poseRows = Int((Double(poses.count) / Double(columns)).rounded(.up))
        let rows = CGFloat(poseRows + 1)
        let rowHeight = max(60, (size.height - 2 * (titleHeight + spacing) - spacing * (rows - 1)) / rows)
        let tileWidth = (size.width - spacing * CGFloat(scripts.count)) / CGFloat(scripts.count + 1)
        return VStack(alignment: .leading, spacing: spacing) {
            sectionTitle("Poses")
            LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: spacing), count: columns),
                      spacing: spacing) {
                ForEach(poses, id: \.1) { command, name in
                    tile(command, nil, label: name, height: rowHeight)
                }
            }
            HStack(alignment: .top, spacing: spacing) {
                VStack(alignment: .leading, spacing: spacing) {
                    sectionTitle("Scripts")
                    HStack(spacing: spacing) {
                        ForEach(scripts, id: \.0.title) { command, icon in
                            tile(command, icon, height: rowHeight)
                        }
                    }
                }
                VStack(alignment: .leading, spacing: spacing) {
                    sectionTitle("Games")
                    tile(.rps(dryRun: false), "hand.raised.fingers.spread", height: rowHeight)
                        .frame(width: tileWidth)
                }
            }
        }
    }

    private var log: some View {
        ScrollViewReader { proxy in
            ScrollView {
                Text(runner.log.isEmpty ? "Output appears here." : runner.log)
                    .font(.system(size: 18, design: .monospaced))
                    .foregroundStyle(runner.log.isEmpty ? .secondary : .primary)
                    .textSelection(.enabled)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(12)
                Color.clear.frame(height: 1).id("end")
            }
            .frame(height: 90)
            .background(.black.opacity(0.4), in: RoundedRectangle(cornerRadius: 14))
            .onChange(of: runner.log) { _, _ in proxy.scrollTo("end") }
        }
    }

    private var status: some View {
        HStack(spacing: 24) {
            Image(systemName: runner.running == nil ? "hand.raised" : "hand.raised.fill")
                .font(.system(size: 48))
                .foregroundStyle(runner.running == nil ? .white : .green)
            Text(runner.running?.title ?? "Idle")
                .font(.system(size: 44, weight: .bold))
                .foregroundStyle(runner.running == nil ? .white : .green)
                .lineLimit(1)
                .minimumScaleFactor(0.5)
            Spacer()
            Menu {
                ForEach(AeroHandRunner.speeds, id: \.self) { pct in
                    Button("\(pct)%") { runner.speedPct = pct }
                }
            } label: {
                Label("Speed \(runner.speedPct)%", systemImage: "speedometer")
                    .font(.system(size: 30, weight: .bold))
                    .foregroundStyle(runner.speedPct > 50 ? .orange : .white)
                    .frame(minHeight: 72)
            }
            .menuStyle(.button)
            .buttonStyle(.bordered)
            .fixedSize()
            .help("Servo speed for every command (hand_speed.py). Back to 50% every launch.")
            Menu {
                ForEach(AeroHandRunner.holds, id: \.self) { mode in
                    Button(mode.capitalized) { runner.hold = mode }
                }
            } label: {
                Label("Hold \(runner.hold.capitalized)", systemImage: "hand.raised.fingers.spread.fill")
                    .font(.system(size: 30, weight: .bold))
                    .foregroundStyle(runner.hold == "auto" ? .white : .orange)
                    .frame(minHeight: 72)
            }
            .menuStyle(.button)
            .buttonStyle(.bordered)
            .fixedSize()
            .help("How hard a pose is held: Auto is low power, Medium holds light objects, Firm holds tools (hottest).")
            Button { showLog.toggle() } label: {
                Image(systemName: showLog ? "text.alignleft" : "text.justify.left")
                    .font(.system(size: 22))
                    .frame(minHeight: 44)
            }
            .buttonStyle(.borderless)
            .foregroundStyle(.white.opacity(showLog ? 0.9 : 0.5))
            .help(showLog ? "Hide log" : "Show log")
            Button(role: .destructive) { runner.stop() } label: {
                Label("Stop", systemImage: "stop.fill")
                    .font(.system(size: 34, weight: .bold))
                    .frame(minWidth: 200, minHeight: 72)
            }
            .buttonStyle(.borderedProminent)
            .tint(.red)
            .keyboardShortcut(.escape, modifiers: [])
            .disabled(runner.running == nil)
        }
    }

    private func sectionTitle(_ title: String) -> some View {
        Text(title).font(.system(size: 32, weight: .heavy)).foregroundStyle(.white.opacity(0.85))
            .frame(height: titleHeight)
    }

    /// Text scales with the row height (capped), and wraps to two lines before shrinking.
    private func tile(_ command: AeroCommand, _ icon: String?, label: String? = nil,
                      height: CGFloat) -> some View {
        let size = min(44, max(22, height * 0.26))
        return Button { runner.run(command) } label: {
            VStack(spacing: 6) {
                if let icon { Image(systemName: icon).font(.system(size: size * 0.9)) }
                Text(label ?? command.title)
                    .font(.system(size: size, weight: .bold))
                    .multilineTextAlignment(.center)
                    .lineLimit(2)
                    .minimumScaleFactor(0.5)
            }
            .padding(.horizontal, 8)
            .frame(maxWidth: .infinity, minHeight: height, maxHeight: height)
        }
        .buttonStyle(TileStyle(active: runner.running == command))
    }
}

/// A plain rounded tile, exactly the size of its label (`.bordered` adds padding
/// outside the computed row height, which pushed the last row off screen).
private struct TileStyle: ButtonStyle {
    let active: Bool

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .foregroundStyle(.white)
            .background(
                RoundedRectangle(cornerRadius: 22)
                    .fill(active ? Color.accentColor : .white.opacity(configuration.isPressed ? 0.25 : 0.1))
            )
            .contentShape(RoundedRectangle(cornerRadius: 22))
    }
}

/// Grows the app window to most of the screen the first time this tab shows
/// (macOS 14 has no `defaultWindowPlacement`), and lets it go full screen.
/// Once per launch, so switching back to this tab never resizes the window.
private struct FillScreen: NSViewRepresentable {
    @MainActor private static var filled = false

    func makeNSView(context: Context) -> NSView {
        let view = NSView()
        DispatchQueue.main.async {
            guard !Self.filled, let window = view.window,
                  let screen = window.screen ?? NSScreen.main else { return }
            Self.filled = true
            window.collectionBehavior.insert(.fullScreenPrimary)
            guard !window.styleMask.contains(.fullScreen) else { return }
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
