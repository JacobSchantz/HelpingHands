#if os(macOS)
import SwiftUI

/// The Aero Hand tab, built around teaching (teach.py): the saved recordings fill the
/// screen, with two big buttons across the bottom, Record and Stop, and every other
/// command in the dropdowns along the top. The same commands answer
/// `helpinghands://aero/…` URLs, which `scripts/app.sh` opens for the voice session.
struct AeroHandPanel: View {
    @ObservedObject private var runner = AeroHandRunner.shared
    @State private var showLog = false  // Jake: hidden by default
    @State private var renaming: AeroTake?
    @State private var heldFull: Date?  // a long press on Play started a full replay; skip the tap after it
    @State private var deleting: AeroTake?
    @Namespace private var flight

    private let scripts: [(AeroCommand, String)] = [
        (.test, "list.number"), (.dance(song: nil), "music.note"), (.count, "textformat.123"),
        (.teleop(dryRun: false), "camera"), (.home, "house.fill"),
    ]

    private var recording: Bool {
        if case .record? = runner.running { return true }
        return false
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 24) {
            topBar
            recordings.frame(maxWidth: .infinity, maxHeight: .infinity)
            if showLog { log }
            HStack(spacing: 24) {
                recordButton
                stopButton
            }
            .frame(height: 200)
        }
        .padding(32)
        .frame(minWidth: 1000, minHeight: 700)
        .overlay { arrivingCard }
        .background(FillScreen())
        .background(Color(red: 0.05, green: 0.12, blue: 0.16).ignoresSafeArea())
        .navigationTitle("Aero Hand")
        .onAppear {
            if runner.poses.isEmpty { runner.loadPoses() }
            runner.loadTakes()
            runner.watchTakes()
        }
        .sheet(item: $renaming) { take in
            VoiceRenameSheet(take: take) { runner.rename(take, to: $0) }
        }
        .confirmationDialog("Delete \(deleting.map(title) ?? "")?",
                            isPresented: Binding(get: { deleting != nil }, set: { if !$0 { deleting = nil } })) {
            Button("Delete", role: .destructive) { if let take = deleting { runner.delete(take) } }
        } message: {
            Text("It moves to the takes/deleted folder.")
        }
    }

    // MARK: Record and Stop

    /// Idle: Record. Recording: a red dot, the timer and a live bar per servo, in the same spot.
    private var recordButton: some View {
        Button { runner.run(.record) } label: {
            Group {
                if recording {
                    HStack(spacing: 28) {
                        Circle().fill(.white).frame(width: 34, height: 34)
                        TimelineView(.periodic(from: .now, by: 0.1)) { context in
                            Text(clock(context.date.timeIntervalSince(runner.startedAt ?? context.date)))
                                .font(.system(size: 60, weight: .heavy).monospacedDigit())
                        }
                        fingerBars
                    }
                } else {
                    Label("Record", systemImage: "record.circle")
                        .font(.system(size: 60, weight: .heavy))
                }
            }
            .padding(.horizontal, 28)
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
        .buttonStyle(TileStyle(tint: .red))
        .disabled(recording)
        .matchedGeometryEffect(id: "record", in: flight, isSource: true)
        .help("Record, then move the fingers by hand. Stop saves it.")
    }

    /// Ends whatever is running (a recording is saved first) and relaxes every servo (relax.sh).
    private var stopButton: some View {
        Button { runner.stopAndRelax() } label: {
            Label("Stop", systemImage: "stop.fill")
                .font(.system(size: 60, weight: .heavy))
                .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
        .buttonStyle(TileStyle(tint: Color(white: 0.35)))
        .keyboardShortcut(.escape, modifiers: [])
        .help("Stop anything running and relax every servo")
    }

    /// Seven short bars, thumb to pinky, each servo's place in its range while recording.
    private var fingerBars: some View {
        HStack(alignment: .bottom, spacing: 8) {
            ForEach(0..<7, id: \.self) { i in
                let pct = i < runner.live.count ? runner.live[i] : 0
                ZStack(alignment: .bottom) {
                    Capsule().fill(.white.opacity(0.25))
                    Capsule().fill(.white).frame(height: 110 * CGFloat(max(pct, 4)) / 100)
                }
                .frame(width: 16, height: 110)
            }
        }
    }

    /// The new take, flying from the Record button into the top of the list once it's saved.
    @ViewBuilder private var arrivingCard: some View {
        if runner.arriving {
            let landing = runner.arrived
            HStack(spacing: 16) {
                Image(systemName: "waveform").font(.system(size: 34, weight: .bold))
                Text(runner.takes.first { $0.file == landing }.map(title) ?? "New recording")
                    .font(.system(size: 28, weight: .bold)).lineLimit(1)
                Spacer()
            }
            .foregroundStyle(.white)
            .padding(.horizontal, 28)
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(.red.opacity(0.8), in: RoundedRectangle(cornerRadius: 18))
            .matchedGeometryEffect(id: landing.map { "row-\($0)" } ?? "record", in: flight,
                                   properties: .frame, isSource: false)
            .allowsHitTesting(false)
        }
    }

    // MARK: Recordings

    private var recordings: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Recordings").font(.system(size: 36, weight: .heavy)).foregroundStyle(.white.opacity(0.85))
            if runner.takes.isEmpty {
                Text("None yet. Press Record, move the fingers, then Stop.")
                    .font(.system(size: 26)).foregroundStyle(.white.opacity(0.6))
                Spacer()
            } else {
                ScrollView {
                    VStack(spacing: 12) {
                        ForEach(runner.takes) { take in
                            row(take)
                                .opacity(runner.arriving && runner.arrived == take.file ? 0 : 1)
                                .matchedGeometryEffect(id: "row-\(take.file)", in: flight, isSource: true)
                        }
                    }
                }
            }
        }
    }

    /// Play is the key poses at the speed setting; a long press (or the right-click menu) plays
    /// the full take at its recorded timing.
    private func row(_ take: AeroTake) -> some View {
        var playing = false
        if case .replay(let file, _)? = runner.running { playing = file == take.file }
        return HStack(spacing: 16) {
            Button {
                if let held = heldFull, Date().timeIntervalSince(held) < 3 { heldFull = nil; return }
                playing ? runner.stop() : runner.run(.replay(take.file, full: false))
            } label: {
                Image(systemName: playing ? "stop.fill" : "play.fill")
                    .font(.system(size: 34, weight: .bold))
                    .frame(width: 80, height: 72)
            }
            .buttonStyle(TileStyle(tint: playing ? .red : .accentColor))
            .disabled(recording)
            .simultaneousGesture(LongPressGesture(minimumDuration: 0.5).onEnded { _ in
                guard !playing, !recording else { return }
                heldFull = Date()
                runner.run(.replay(take.file, full: true))
            })
            .help(playing ? "Stop" : "Play the motion (hold for the full take at its recorded timing)")
            VStack(alignment: .leading, spacing: 4) {
                Text(title(take)).font(.system(size: 28, weight: .bold)).lineLimit(1)
                Text(take.name.isEmpty ? clock(take.seconds)
                     : "\(take.date.formatted(date: .abbreviated, time: .shortened)) · \(clock(take.seconds))")
                    .font(.system(size: 22).monospacedDigit()).opacity(0.7)
            }
            .foregroundStyle(.white)
            Spacer()
            Button { renaming = take } label: {
                Image(systemName: "pencil").font(.system(size: 26)).frame(width: 52, height: 52)
            }
            .buttonStyle(.borderless).foregroundStyle(.white.opacity(0.8)).help("Rename")
            Button { deleting = take } label: {
                Image(systemName: "trash").font(.system(size: 26)).frame(width: 52, height: 52)
            }
            .buttonStyle(.borderless).foregroundStyle(.white.opacity(0.8)).help("Delete")
        }
        .padding(12)
        .background(.white.opacity(playing ? 0.18 : 0.08), in: RoundedRectangle(cornerRadius: 18))
        .contextMenu {
            Button("Replay motion") { runner.run(.replay(take.file, full: false)) }
                .disabled(recording)
            Button("Replay full (recorded timing)") { runner.run(.replay(take.file, full: true)) }
                .disabled(recording)
            Divider()
            Button("Rename…") { renaming = take }
            Button("Delete…", role: .destructive) { deleting = take }
        }
    }

    /// The name if it has one, else when it was recorded.
    private func title(_ take: AeroTake) -> String {
        take.name.isEmpty ? take.date.formatted(date: .abbreviated, time: .shortened) : take.name
    }

    private func clock(_ seconds: Double) -> String {
        let s = max(0, Int(seconds))
        return String(format: "%d:%02d", s / 60, s % 60)
    }

    // MARK: Everything else

    private var topBar: some View {
        HStack(spacing: 20) {
            dropdown("Commands", icon: "ellipsis.circle", warn: false) {
                Section("Poses") {
                    ForEach(runner.poses, id: \.self) { name in
                        Button(name.capitalized) { runner.run(.pose(name)) }
                    }
                    Button("Relax") { runner.run(.relax) }
                }
                Section("Scripts") {
                    ForEach(scripts, id: \.0.title) { command, icon in
                        Button { runner.run(command) } label: { Label(command.title, systemImage: icon) }
                    }
                }
                Section("Games") {
                    Button { runner.run(.rps(dryRun: false)) } label: {
                        Label("Rock paper scissors", systemImage: "hand.raised.fingers.spread")
                    }
                }
            }
            .help("Poses, scripts and games")
            dropdown("Speed \(runner.speedPct)%", icon: "speedometer", warn: runner.speedPct > 50) {
                ForEach(AeroHandRunner.speeds, id: \.self) { pct in
                    Button("\(pct)%") { runner.speedPct = pct }
                }
            }
            .help("Servo speed for every command and playback (hand_speed.py). Back to 50% every launch.")
            dropdown("Hold \(runner.hold.capitalized)", icon: "hand.raised.fingers.spread.fill",
                     warn: runner.hold != "auto") {
                ForEach(AeroHandRunner.holds, id: \.self) { mode in
                    Button(mode.capitalized) { runner.hold = mode }
                }
            }
            .help("How hard a pose is held: Auto is low power, Medium holds light objects, Firm holds tools (hottest).")
            Button { showLog.toggle() } label: {
                Image(systemName: showLog ? "text.alignleft" : "text.justify.left")
                    .font(.system(size: 22))
                    .frame(minHeight: 44)
            }
            .buttonStyle(.borderless)
            .foregroundStyle(.white.opacity(showLog ? 0.9 : 0.5))
            .help(showLog ? "Hide log" : "Show log")
            Spacer()
        }
    }

    private func dropdown<Content: View>(_ title: String, icon: String, warn: Bool,
                                         @ViewBuilder content: () -> Content) -> some View {
        Menu(content: content) {
            Label(title, systemImage: icon)
                .font(.system(size: 26, weight: .bold))
                .foregroundStyle(warn ? .orange : .white)
                .frame(minHeight: 64)
        }
        .menuStyle(.button)
        .buttonStyle(.bordered)
        .fixedSize()
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
}

/// A plain rounded tile in a tint, exactly the size of its label.
private struct TileStyle: ButtonStyle {
    let tint: Color
    @Environment(\.isEnabled) private var enabled

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .foregroundStyle(.white)
            .background(
                RoundedRectangle(cornerRadius: 22)
                    .fill(tint.opacity(configuration.isPressed ? 0.55 : enabled ? 0.8 : 0.25))
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

/// Routes `helpinghands://aero/…` to the runner and `helpinghands://designs/…`
/// to the design workbench, without SwiftUI opening a new
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
        if url.host == "designs" {
            // helpinghands://designs/<name>: the design workbench (Scripts/design.sh).
            let name = url.path.trimmingCharacters(in: CharacterSet(charactersIn: "/")).removingPercentEncoding ?? ""
            Task { @MainActor in RepoDesigns.shared.open(name: name) }
            return
        }
        Task { @MainActor in AeroHandRunner.shared.handle(url: url) }
    }
}
#endif
