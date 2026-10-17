#if os(macOS)
import Foundation

/// One Aero Hand command — a button in `AeroHandPanel` and a
/// `helpinghands://aero/<command>[/<arg>]` URL (`scripts/app.sh` opens those).
enum AeroCommand: Equatable {
    case perform(song: String?)   // song first (random ¿? track), then dance to it
    case routine                  // song, then the old fixed routine
    case listen                   // dance dry run: mic beat tracking only
    case pose(String)             // any name or alias pose.py knows
    case count                    // Chinese one-hand counting 1..10
    case teleop(dryRun: Bool)     // webcam teleop; its OpenCV window is the live preview
    case home

    /// `helpinghands://aero/pose/peace`, `…/perform`, `…/perform/Song%20Name`, `…/teleop`.
    /// `stop` and `fast` aren't commands; `AeroHandRunner.handle(url:)` takes those.
    init?(path: [String]) {
        let arg = path.count > 1 ? path.dropFirst().joined(separator: " ") : nil
        switch path.first?.lowercased() {
        case "perform", "performance", "dance": self = .perform(song: arg)
        case "routine": self = .routine
        case "listen": self = .listen
        case "pose": guard let arg else { return nil }; self = .pose(arg)
        case "count": self = .count
        case "teleop": self = .teleop(dryRun: arg == "dry-run")
        case "track", "tracking": self = .teleop(dryRun: true)
        case "home": self = .home
        default: return nil
        }
    }

    var title: String {
        switch self {
        case .perform(let song): return song.map { "Perform \($0)" } ?? "Perform"
        case .routine: return "Fixed routine"
        case .listen: return "Listen only"
        case .pose(let name): return "Pose: \(name)"
        case .count: return "Count to ten"
        case .teleop(let dryRun): return dryRun ? "Tracking only" : "Teleop"
        case .home: return "Home"
        }
    }

    /// The script (a venv wrapper in third_party/aero_hand/scripts) and its arguments.
    var invocation: (script: String, args: [String]) {
        switch self {
        case .perform(let song): return ("performance.sh", song.map { [$0] } ?? [])
        case .routine: return ("performance.sh", ["--routine"])
        case .listen: return ("performance.sh", ["--dry-run"])
        case .pose(let name): return ("pose.sh", [name])
        case .count: return ("pose.sh", ["count to ten"])
        case .teleop(let dryRun): return ("teleop.sh", dryRun ? ["--dry-run"] : [])
        case .home: return ("home.sh", [])
        }
    }
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
    /// Off on every launch: the scripts' 50% cap (hand_speed.py) applies unless this is on.
    @Published var fullSpeed = false

    private var process: Process?
    private var next: AeroCommand?

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

    func handle(url: URL) {
        guard url.scheme == "helpinghands", url.host == "aero" else { return }
        let path = url.pathComponents.filter { $0 != "/" }
        switch path.first?.lowercased() {
        case "stop":
            next = nil
            stop()
        case "fast":
            fullSpeed = path.dropFirst().first?.lowercased() != "off"
            append("speed: \(fullSpeed ? "full (100%)" : "capped at 50%")\n")
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
        let process = makeProcess(script: "pose.sh", args: ["--list"], fullSpeed: false)
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

    private func start(_ command: AeroCommand) {
        let (script, args) = command.invocation
        let process = makeProcess(script: script, args: args, fullSpeed: fullSpeed)
        let pipe = Pipe()
        process.standardOutput = pipe
        process.standardError = pipe
        pipe.fileHandleForReading.readabilityHandler = { handle in
            let data = handle.availableData
            guard !data.isEmpty else { return }
            let text = String(decoding: data, as: UTF8.self)
            Task { @MainActor in self.append(text) }
        }
        process.terminationHandler = { finished in
            pipe.fileHandleForReading.readabilityHandler = nil
            let status = finished.terminationStatus
            Task { @MainActor in self.finished(status: status) }
        }
        append("▶︎ \(command.title)\(fullSpeed ? " (full speed)" : "")\n")
        do {
            try process.run()
            self.process = process
            running = command
        } catch {
            append("couldn't start \(script): \(error.localizedDescription)\n")
        }
    }

    private func finished(status: Int32) {
        append(status == 0 ? "✓ done\n" : "✗ exited \(status)\n")
        process = nil
        running = nil
        if let next {
            self.next = nil
            start(next)
        }
    }

    private func makeProcess(script: String, args: [String], fullSpeed: Bool) -> Process {
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/bin/sh")
        process.arguments = [Self.scriptsDir.appendingPathComponent(script).path] + args
        process.currentDirectoryURL = Self.scriptsDir
        var env = ProcessInfo.processInfo.environment
        env["PYTHONUNBUFFERED"] = "1"
        if fullSpeed { env["AERO_SPEED_PCT"] = "100" } else { env.removeValue(forKey: "AERO_SPEED_PCT") }
        process.environment = env
        return process
    }

    private func append(_ text: String) {
        log += text
        if log.count > 20_000 { log = String(log.suffix(15_000)) }
    }
}
#endif
