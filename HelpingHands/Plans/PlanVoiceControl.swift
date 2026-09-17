import AVFoundation
import Foundation
import Speech

/// The spoken commands a listener can give while a plan is playing.
enum PlanVoiceCommand: String {
    case next, back, again, pause, resume, restart, whereAmI, sections, faster, slower

    /// Matched against the tail of the running transcript, so a command lands
    /// even when the recogniser has been listening for a while.
    static func match(in transcript: String) -> (command: PlanVoiceCommand, trigger: String)? {
        let words = transcript
            .lowercased()
            .components(separatedBy: CharacterSet.alphanumerics.inverted)
            .filter { !$0.isEmpty }
        guard !words.isEmpty else { return nil }
        let tail = words.suffix(5).joined(separator: " ")

        let phrases: [(String, PlanVoiceCommand)] = [
            ("next step", .next), ("next", .next), ("go on", .next), ("skip", .next), ("continue", .resume),
            ("go back", .back), ("previous", .back), ("back up", .back), ("back", .back),
            ("say that again", .again), ("repeat that", .again), ("repeat", .again), ("again", .again),
            ("pause", .pause), ("stop", .pause), ("hold on", .pause), ("wait", .pause),
            ("resume", .resume), ("keep going", .resume), ("carry on", .resume), ("play", .resume),
            ("start over", .restart), ("from the top", .restart),
            ("where am i", .whereAmI), ("where was i", .whereAmI),
            ("what are the sections", .sections), ("sections", .sections), ("table of contents", .sections),
            ("faster", .faster), ("speed up", .faster),
            ("slower", .slower), ("slow down", .slower)
        ]

        for (phrase, command) in phrases where tail.contains(phrase) {
            return (command, phrase)
        }
        return nil
    }
}

/// Hands-free control: listens for short commands while a plan plays.
///
/// It is opt-in per listening session because it has to take the microphone and
/// move the audio session to `.playAndRecord`/`.voiceChat`, which is also what
/// buys the echo cancellation that keeps the recogniser from transcribing the
/// plan being read out of the speaker. A second guard drops any command whose
/// trigger word appears in the step currently being spoken, so a plan that says
/// "next" out loud can't drive itself.
final class PlanVoiceControl: NSObject, ObservableObject {
    @Published private(set) var isListening = false
    @Published private(set) var status = "Off"
    @Published private(set) var lastHeard = ""

    /// Delivered on the main queue.
    var onCommand: ((PlanVoiceCommand) -> Void)?
    var onLog: ((String) -> Void)?
    /// The text being spoken right now, used to drop echoes of the plan itself.
    var spokenTextProvider: (() -> String)?
    /// Called after the microphone is released so playback audio can be restored.
    var onStop: (() -> Void)?

    private let recognizer = SFSpeechRecognizer(locale: Locale.current) ?? SFSpeechRecognizer()
    private let engine = AVAudioEngine()
    private var request: SFSpeechAudioBufferRecognitionRequest?
    private var task: SFSpeechRecognitionTask?
    private var lastCommandAt = Date.distantPast
    private var restarting = false

    func toggle() {
        isListening ? stop() : start()
    }

    func start() {
        guard !isListening else { return }
        guard let recognizer, recognizer.isAvailable else {
            update(status: "Speech recognition unavailable on this device")
            return
        }

        SFSpeechRecognizer.requestAuthorization { [weak self] authorization in
            DispatchQueue.main.async {
                guard let self else { return }
                guard authorization == .authorized else {
                    self.update(status: "Speech recognition not allowed (Settings ▸ Helping Hands)")
                    return
                }
                self.requestMicrophone { granted in
                    guard granted else {
                        self.update(status: "Microphone not allowed (Settings ▸ Helping Hands)")
                        return
                    }
                    self.beginListening()
                }
            }
        }
    }

    func stop() {
        restarting = false
        task?.cancel()
        task = nil
        request?.endAudio()
        request = nil
        if engine.isRunning {
            engine.stop()
            engine.inputNode.removeTap(onBus: 0)
        }
        isListening = false
        update(status: "Off")
        onStop?()
    }

    // MARK: - Internals

    private func requestMicrophone(_ completion: @escaping (Bool) -> Void) {
        #if os(iOS)
        if #available(iOS 17.0, *) {
            AVAudioApplication.requestRecordPermission { granted in
                DispatchQueue.main.async { completion(granted) }
            }
        } else {
            AVAudioSession.sharedInstance().requestRecordPermission { granted in
                DispatchQueue.main.async { completion(granted) }
            }
        }
        #else
        completion(true)
        #endif
    }

    private func beginListening() {
        #if os(iOS)
        do {
            let session = AVAudioSession.sharedInstance()
            // `.voiceChat` turns on the hardware echo canceller, which is the
            // only reason listening and speaking can overlap at all.
            try session.setCategory(.playAndRecord,
                                    mode: .voiceChat,
                                    options: [.defaultToSpeaker, .allowBluetooth, .allowBluetoothA2DP])
            try session.setActive(true)
        } catch {
            update(status: "Audio session refused the microphone: \(error.localizedDescription)")
            return
        }
        #endif

        startTask()
    }

    private func startTask() {
        guard let recognizer else { return }

        let request = SFSpeechAudioBufferRecognitionRequest()
        request.shouldReportPartialResults = true
        if recognizer.supportsOnDeviceRecognition {
            request.requiresOnDeviceRecognition = true
        }
        self.request = request

        let input = engine.inputNode
        let format = input.outputFormat(forBus: 0)
        input.removeTap(onBus: 0)
        input.installTap(onBus: 0, bufferSize: 1024, format: format) { buffer, _ in
            request.append(buffer)
        }

        engine.prepare()
        do {
            try engine.start()
        } catch {
            update(status: "Microphone failed to start: \(error.localizedDescription)")
            return
        }

        task = recognizer.recognitionTask(with: request) { [weak self] result, error in
            guard let self else { return }
            if let result {
                DispatchQueue.main.async { self.handle(transcript: result.bestTranscription.formattedString) }
            }
            if error != nil || (result?.isFinal ?? false) {
                DispatchQueue.main.async { self.restartTask() }
            }
        }

        isListening = true
        update(status: recognizer.supportsOnDeviceRecognition ? "Listening (on device)" : "Listening")
        log("Voice control on — say next, back, repeat, pause, resume, where am I.")
    }

    /// Recognition tasks end on their own after about a minute of audio; a
    /// fresh one keeps hands-free control alive for a long plan.
    private func restartTask() {
        guard isListening, !restarting else { return }
        restarting = true
        task?.cancel()
        task = nil
        request?.endAudio()
        request = nil
        if engine.isRunning {
            engine.stop()
            engine.inputNode.removeTap(onBus: 0)
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) { [weak self] in
            guard let self, self.isListening else { return }
            self.restarting = false
            self.startTask()
        }
    }

    private func handle(transcript: String) {
        lastHeard = String(transcript.suffix(60))
        guard Date().timeIntervalSince(lastCommandAt) > 1.0 else { return }
        guard let (command, trigger) = PlanVoiceCommand.match(in: transcript) else { return }

        let spoken = (spokenTextProvider?() ?? "").lowercased()
        if !spoken.isEmpty, spoken.contains(trigger) {
            log("Ignored “\(trigger)” — the plan is saying that word right now.")
            return
        }

        lastCommandAt = Date()
        log("Heard command: \(trigger) → \(command.rawValue)")
        onCommand?(command)
        restartTask()
    }

    private func update(status: String) {
        if Thread.isMainThread {
            self.status = status
        } else {
            DispatchQueue.main.async { self.status = status }
        }
        log(status)
    }

    private func log(_ message: String) {
        onLog?(message)
    }
}
