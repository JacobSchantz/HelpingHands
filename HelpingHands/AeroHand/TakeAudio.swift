#if os(macOS)
import AVFoundation
import Speech

/// The mic side of a recording: the app owns the mic permission, so it records the whole take,
/// transcribes it on the device, and hands both to `teach.sh audio`. Also plays a take's audio
/// during Replay full, from where teach.py says the first frame is.
@MainActor
final class TakeAudio {
    private var recorder: AVAudioRecorder?
    private var startedAt = 0.0  // wall time the mic started; teach.py lines it up with the take's
    private var player: AVAudioPlayer?

    /// Starts recording the default input (the Mac mic, or whatever input macOS has selected).
    func startRecording(into dir: URL) {
        AVCaptureDevice.requestAccess(for: .audio) { allowed in
            Task { @MainActor in
                guard allowed else { return }
                let url = dir.appendingPathComponent("mic-\(Int(Date().timeIntervalSince1970)).m4a")
                let settings: [String: Any] = [AVFormatIDKey: kAudioFormatMPEG4AAC, AVSampleRateKey: 44_100,
                                               AVNumberOfChannelsKey: 1]
                guard let recorder = try? AVAudioRecorder(url: url, settings: settings), recorder.record()
                else { return }
                self.startedAt = Date().timeIntervalSince1970
                self.recorder = recorder
            }
        }
    }

    /// Stops the mic and transcribes it. Returns the sidecar teach.py's `audio` reads, or nil if the
    /// mic never started.
    func finishRecording() async -> URL? {
        guard let recorder else { return nil }
        recorder.stop()
        self.recorder = nil
        let (transcript, words) = await Self.transcribe(recorder.url)
        let sidecar: [String: Any] = ["file": recorder.url.path, "started_at": startedAt, "transcript": transcript,
                                      "words": words.map { [$0.0, $0.1] }]
        let url = recorder.url.deletingPathExtension().appendingPathExtension("json")
        guard let data = try? JSONSerialization.data(withJSONObject: sidecar),
              (try? data.write(to: url)) != nil else { return nil }
        return url
    }

    /// An empty transcript (and the audio still kept) when speech recognition isn't allowed or hears nothing.
    nonisolated private static func transcribe(_ url: URL) async -> (String, [(Double, String)]) {
        let allowed = await withCheckedContinuation { done in
            SFSpeechRecognizer.requestAuthorization { done.resume(returning: $0 == .authorized) }
        }
        guard allowed, let recognizer = SFSpeechRecognizer(locale: Locale.current) ?? SFSpeechRecognizer(),
              recognizer.isAvailable else { return ("", []) }
        let request = SFSpeechURLRecognitionRequest(url: url)
        request.shouldReportPartialResults = false
        request.requiresOnDeviceRecognition = recognizer.supportsOnDeviceRecognition
        return await withCheckedContinuation { done in
            recognizer.recognitionTask(with: request, resultHandler: once { result, error in
                guard error != nil || result?.isFinal == true else { return false }
                let best = result?.bestTranscription
                done.resume(returning: (best?.formattedString ?? "",
                                        best?.segments.map { ($0.timestamp, $0.substring) } ?? []))
                return true
            })
        }
    }

    /// The recogniser can call back after its final result (an error on teardown); resume only once.
    nonisolated private static func once(
        _ handle: @escaping (SFSpeechRecognitionResult?, Error?) -> Bool
    ) -> (SFSpeechRecognitionResult?, Error?) -> Void {
        let lock = NSLock()
        var done = false
        return { result, error in
            lock.lock()
            defer { lock.unlock() }
            if !done { done = handle(result, error) }
        }
    }

    /// teach.py's "audio <file> <seconds in> <rate>" line, printed as the first frame goes out.
    func play(line: Substring) {
        let parts = line.split(separator: " ")
        guard parts.count >= 4, let from = Double(parts[parts.count - 2]), let rate = Float(parts[parts.count - 1])
        else { return }
        let path = parts[1..<(parts.count - 2)].joined(separator: " ")
        guard let player = try? AVAudioPlayer(contentsOf: URL(fileURLWithPath: path)) else { return }
        player.enableRate = true
        player.rate = min(2, max(0.5, rate))
        player.currentTime = max(0, from)
        player.play()
        self.player = player
    }

    func stopPlaying() {
        player?.stop()
        player = nil
    }
}
#endif
