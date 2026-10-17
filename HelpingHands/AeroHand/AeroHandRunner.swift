#if os(macOS)
import CoreServices
import Foundation
import SwiftUI

/// One Aero Hand command — a button in `AeroHandPanel` and a
/// `helpinghands://aero/<command>[/<arg>]` URL (`scripts/app.sh` opens those).
enum AeroCommand: Equatable {
    case dance(song: String?)     // a random 没有歌词 (no lyrics) track (or the named song), danced along to
    case test                     // song first, then the old fixed routine
    case pose(String)             // any name or alias pose.py knows
    case count                    // Chinese one-hand counting 1..10
    case teleop(dryRun: Bool)     // webcam teleop; its OpenCV window is the live preview
    case rps(dryRun: Bool)        // rock-paper-scissors on camera; the hand's throw is random and committed first
    case home                     // re-home every servo; frees a stalled finger
    case relax                    // zero torque on every servo
    case record                   // transparent mode: move the fingers by hand; Stop saves the take
    case replay(String?, full: Bool)  // play a take (file name in the takes folder; nil = newest): its key
                                      // poses at the speed setting, or `full` at the recorded timing

    /// `helpinghands://aero/pose/peace`, `…/dance`, `…/dance/Song%20Name`, `…/test`, `…/teleop`, `…/rps`,
    /// `…/record`, `…/replay`, `…/replay/take-20261017-155122.json`, `…/replay-full[/take-….json]`.
    /// `stop`, `speed` and `hold` aren't commands; `AeroHandRunner.handle(url:)` takes those.
    init?(path: [String]) {
        let arg = path.count > 1 ? path.dropFirst().joined(separator: " ") : nil
        switch path.first?.lowercased() {
        case "dance", "perform", "performance": self = .dance(song: arg)
        case "test", "routine": self = .test
        case "pose":
            guard let arg else { return nil }
            self = arg.lowercased() == "relax" ? .relax : .pose(arg)  // Relax is a Poses button too
        case "count": self = .count
        case "teleop": self = .teleop(dryRun: arg == "dry-run")
        case "track", "tracking": self = .teleop(dryRun: true)
        case "rps", "rock-paper-scissors", "rock paper scissors": self = .rps(dryRun: arg == "dry-run")
        case "home": self = .home
        case "relax": self = .relax
        case "record", "teach": self = .record
        case "replay", "play": self = .replay(arg == "last" ? nil : arg, full: false)
        case "replay-full", "play-full": self = .replay(arg == "last" ? nil : arg, full: true)
        default: return nil
        }
    }

    var title: String {
        switch self {
        case .dance(let song): return song.map { "Dance: \($0)" } ?? "Dance"
        case .test: return "Test"
        case .pose(let name): return "Pose: \(name)"
        case .count: return "Count to ten"
        case .teleop(let dryRun): return dryRun ? "Tracking only" : "Teleop"
        case .rps(let dryRun): return dryRun ? "RPS (hand still)" : "Rock paper scissors"
        case .home: return "Re-home (if stuck)"
        case .relax: return "Relax"
        case .record: return "Record"
        case .replay(_, let full): return full ? "Playing (full)" : "Playing"
        }
    }

    /// The script (a venv wrapper in third_party/aero_hand/scripts) and its arguments.
    var invocation: (script: String, args: [String]) {
        switch self {
        case .dance(let song): return ("performance.sh", song.map { [$0] } ?? [])
        case .test: return ("performance.sh", ["--routine"])
        case .pose(let name): return ("pose.sh", [name])
        case .count: return ("pose.sh", ["count to ten"])
        case .teleop(let dryRun): return ("teleop.sh", dryRun ? ["--dry-run"] : [])
        case .rps(let dryRun): return ("rps.sh", dryRun ? ["--dry-run"] : [])
        case .home: return ("home.sh", [])
        case .relax: return ("relax.sh", [])
        case .record: return ("teach.sh", ["record"])
        case .replay(let file, let full): return ("teach.sh", ["replay", file ?? "last"] + (full ? ["--full"] : []))
        }
    }
}

/// A saved teach.py take, as `teach.sh list` prints it.
struct AeroTake: Decodable, Identifiable, Equatable {
    let file: String
    let name: String
    let seconds: Double
    let recorded: Double  // seconds since 1970, from the file name

    var id: String { file }
    var date: Date { Date(timeIntervalSince1970: recorded) }
}

/// Runs the aero_hand scripts as children of the app, so macOS asks for (and
/// remembers) camera, microphone and Music access for Helping Hands rather
/// than Terminal. One command at a time: the hand has one serial port, so a new
/// command interrupts the running one first.
@MainActor
final class AeroHandRunner: ObservableObject {
    static let shared = AeroHandRunner()

    /// Where the scripts live. Override with
    /// `defaults write com.helpinghands.app aeroScriptsDir <path>`.
    static var scriptsDir: URL {
        if let custom = UserDefaults.standard.string(forKey: "aeroScriptsDir") {
            return URL(fileURLWithPath: (custom as NSString).expandingTildeInPath)
        }
        return FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent("HelpingHands/third_party/aero_hand/scripts")
    }

    @Published private(set) var running: AeroCommand?
    @Published private(set) var log = ""
    @Published private(set) var poses: [String] = []
    /// Servo speed as a percent of full, for every command (AERO_SPEED_PCT, read by
    /// hand_speed.py). Back to 50% on every launch.
    static let speeds = [25, 50, 60, 80, 100]
    @Published var speedPct = 50
    /// How hard a pose (or grip) is held once reached (AERO_HOLD, read by hold.py):
    /// auto is the low-power hold, medium holds light objects, firm holds tools.
    static let holds = ["auto", "medium", "firm"]
    @Published var hold = "auto"
    /// Saved recordings, newest first.
    @Published private(set) var takes: [AeroTake] = []
    /// While recording: each servo's place in its range, 0 (open) to 100 (teach.py's "pos" lines).
    @Published private(set) var live: [Int] = []
    @Published private(set) var startedAt: Date?
    /// A recording just stopped: its card shows on the Record button until the take loads,
    /// then flies to `arrived`, the new take's row at the top of the list.
    @Published private(set) var arriving = false
    @Published private(set) var arrived: String?

    /// teach.py's takes folder, watched so the list follows renames, deletes and labels
    /// made outside the app (teach.py, auto-labels, voice renames).
    static let takesDir = FileManager.default.homeDirectoryForCurrentUser
        .appendingPathComponent("HelpingHands-tools/aero/takes")
    private var takesStream: FSEventStreamRef?
    private var beforeRecord: Set<String> = []

    private var process: Process?
    private var next: AeroCommand?
    private var partialLine = ""

    func run(_ command: AeroCommand) {
        if process != nil {
            next = command
            stop()
            return
        }
        start(command)
    }

    /// SIGINT first so the scripts' `finally` blocks ease the hand open and close
    /// the port; SIGTERM if it hasn't exited 3 s later.
    func stop() {
        guard let process, process.isRunning else { return }
        append("■ stopping\n")
        process.interrupt()
        DispatchQueue.main.asyncAfter(deadline: .now() + 3) { [weak process] in
            if let process, process.isRunning { process.terminate() }
        }
    }

    /// The Stop button: ends whatever is running (teach.py saves a recording on the way out),
    /// then relaxes every servo.
    func stopAndRelax() {
        run(.relax)
    }

    func handle(url: URL) {
        guard url.scheme == "helpinghands", url.host == "aero" else { return }
        let path = url.pathComponents.filter { $0 != "/" }
        switch path.first?.lowercased() {
        case "stop":
            stopAndRelax()
        case "speed":
            guard let pct = path.dropFirst().first.flatMap({ Int($0.trimmingCharacters(in: ["%"])) }),
                  (1...100).contains(pct) else { append("unknown URL \(url.absoluteString)\n"); return }
            speedPct = pct
            append("speed: \(pct)%\n")
        case "hold":
            guard let mode = path.dropFirst().first?.lowercased(), Self.holds.contains(mode)
            else { append("unknown URL \(url.absoluteString)\n"); return }
            hold = mode
            append("hold: \(mode)\n")
        case "fast":  // old alias: on = 100%, off = 50%
            speedPct = path.dropFirst().first?.lowercased() == "off" ? 50 : 100
            append("speed: \(speedPct)%\n")
        default:
            if let command = AeroCommand(path: path) {
                run(command)
            } else {
                append("unknown URL \(url.absoluteString)\n")
            }
        }
    }

    /// Fills `poses` from `pose.sh --list`, so a pose added to POSES gets a button
    /// without touching Swift.
    func loadPoses() {
        let process = makeProcess(script: "pose.sh", args: ["--list"], speedPct: 50, hold: "auto")
        let pipe = Pipe()
        process.standardOutput = pipe
        process.terminationHandler = { _ in
            let text = String(decoding: pipe.fileHandleForReading.readDataToEndOfFile(), as: UTF8.self)
            let names = text.split(separator: "\n").compactMap { line in
                line.split(separator: ":", maxSplits: 1).first.map(String.init)
            }
            Task { @MainActor in self.poses = names }
        }
        do { try process.run() } catch { append("can't list poses: \(error.localizedDescription)\n") }
    }

    /// Fills `takes` from `teach.sh list`. After a recording, the new take arrives animated.
    func loadTakes() {
        quick(["list"]) { text in
            let takes = text.split(separator: "\n").compactMap {
                try? JSONDecoder().decode(AeroTake.self, from: Data($0.utf8))
            }
            guard self.arriving, self.arrived == nil else { self.takes = takes; return }
            guard let new = takes.first(where: { !self.beforeRecord.contains($0.file) }) else {
                self.takes = takes  // nothing saved (too short, or it failed)
                self.arriving = false
                return
            }
            withAnimation(.spring(duration: 0.7)) {
                self.takes = takes
                self.arrived = new.file
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.75) {
                self.arriving = false
                self.arrived = nil
                self.loadTakes()  // an auto-label may have landed mid-flight
            }
        }
    }

    /// Reloads `takes` on any change in the takes folder (FSEvents, file-level, 0.3 s
    /// coalescing), so a rename or delete from teach.py or a voice session shows at once.
    func watchTakes() {
        guard takesStream == nil else { return }
        try? FileManager.default.createDirectory(at: Self.takesDir, withIntermediateDirectories: true)
        var context = FSEventStreamContext(version: 0, info: Unmanaged.passUnretained(self).toOpaque(),
                                           retain: nil, release: nil, copyDescription: nil)
        let callback: FSEventStreamCallback = { _, info, _, _, _, _ in
            guard let info else { return }
            let runner = Unmanaged<AeroHandRunner>.fromOpaque(info).takeUnretainedValue()
            MainActor.assumeIsolated { runner.takesChanged() }
        }
        guard let stream = FSEventStreamCreate(
            nil, callback, &context, [Self.takesDir.path] as CFArray,
            FSEventStreamEventId(kFSEventStreamEventIdSinceNow), 0.3,
            FSEventStreamCreateFlags(kFSEventStreamCreateFlagFileEvents | kFSEventStreamCreateFlagNoDefer))
        else { return }
        FSEventStreamSetDispatchQueue(stream, .main)
        FSEventStreamStart(stream)
        takesStream = stream
    }

    /// Mid-recording the new file waits; `finished` loads it so it can fly in.
    private func takesChanged() {
        if case .record? = running { return }
        if arriving { return }
        loadTakes()
    }

    func rename(_ take: AeroTake, to name: String) {
        quick(["rename", take.file, name]) { _ in self.loadTakes() }
    }

    /// Moves the take to takes/deleted, so a wrong click can be undone by hand.
    func delete(_ take: AeroTake) {
        quick(["delete", take.file]) { _ in self.loadTakes() }
    }

    /// teach.sh file commands: no serial port, so they run beside whatever is moving the hand.
    private func quick(_ args: [String], then: @escaping @MainActor (String) -> Void) {
        let process = makeProcess(script: "teach.sh", args: args, speedPct: 50, hold: "auto")
        let pipe = Pipe()
        process.standardOutput = pipe
        process.terminationHandler = { _ in
            let text = String(decoding: pipe.fileHandleForReading.readDataToEndOfFile(), as: UTF8.self)
            Task { @MainActor in then(text) }
        }
        do { try process.run() } catch { append("teach.sh \(args[0]): \(error.localizedDescription)\n") }
    }

    private func start(_ command: AeroCommand) {
        let (script, args) = command.invocation
        let process = makeProcess(script: script, args: args, speedPct: speedPct, hold: hold)
        let pipe = Pipe()
        process.standardOutput = pipe
        process.standardError = pipe
        pipe.fileHandleForReading.readabilityHandler = { handle in
            let data = handle.availableData
            guard !data.isEmpty else { return }
            let text = String(decoding: data, as: UTF8.self)
            Task { @MainActor in self.output(text) }
        }
        process.terminationHandler = { finished in
            pipe.fileHandleForReading.readabilityHandler = nil
            let status = finished.terminationStatus
            Task { @MainActor in self.finished(status: status) }
        }
        append("▶︎ \(command.title) (\(speedPct)%, hold \(hold))\n")
        do {
            try process.run()
            self.process = process
            running = command
            startedAt = Date()
            if case .record = command { beforeRecord = Set(takes.map(\.file)) }
            live = []
        } catch {
            append("couldn't start \(script): \(error.localizedDescription)\n")
        }
    }

    private func finished(status: Int32) {
        append(status == 0 ? "✓ done\n" : "✗ exited \(status)\n")
        if case .record? = running {
            arriving = true
            loadTakes()
        }
        process = nil
        running = nil
        startedAt = nil
        partialLine = ""
        if let next {
            self.next = nil
            start(next)
        }
    }

    private func makeProcess(script: String, args: [String], speedPct: Int, hold: String) -> Process {
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/bin/sh")
        process.arguments = [Self.scriptsDir.appendingPathComponent(script).path] + args
        process.currentDirectoryURL = Self.scriptsDir
        var env = ProcessInfo.processInfo.environment
        env["PYTHONUNBUFFERED"] = "1"
        env["AERO_SPEED_PCT"] = String(speedPct)
        env["AERO_HOLD"] = hold
        process.environment = env
        return process
    }

    /// Script output, whole lines at a time: "pos" lines feed `live`, the rest go to the log.
    private func output(_ text: String) {
        let lines = (partialLine + text).split(separator: "\n", omittingEmptySubsequences: false)
        partialLine = String(lines.last ?? "")
        for line in lines.dropLast() {
            if line.hasPrefix("pos ") {
                live = line.split(separator: " ").dropFirst().compactMap { Int($0) }
            } else {
                append(line + "\n")
            }
        }
    }

    private func append(_ text: String) {
        log += text
        if log.count > 20_000 { log = String(log.suffix(15_000)) }
    }
}
#endif
