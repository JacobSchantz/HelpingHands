import AVFoundation
import Foundation
#if canImport(MediaPlayer)
import MediaPlayer
#endif
#if canImport(UIKit)
import UIKit
#endif

/// Reads a plan aloud, one step at a time, and keeps going on its own.
///
/// Everything a listener needs is driven from here rather than from the view,
/// because the screen is explicitly optional: the same commands arrive from the
/// on-screen buttons, from AirPods / the lock screen (`MPRemoteCommandCenter`),
/// and from `PlanVoiceControl`. Audio is configured for spoken playback and
/// keeps running with the screen off, which is what makes a plan listenable
/// end to end without looking.
final class PlanNarrator: NSObject, ObservableObject {
    @Published private(set) var index: Int = 0
    @Published private(set) var isSpeaking = false
    @Published private(set) var isPaused = false
    @Published private(set) var isFinished = false
    @Published private(set) var log: [String] = []
    @Published var rate: Float = PlanNarrator.storedRate {
        didSet {
            UserDefaults.standard.set(rate, forKey: Self.rateKey)
            guard isSpeaking else { return }
            speak(step: index)   // the rate of an in-flight utterance is fixed
        }
    }

    let plan: PlanDocument

    private let synthesizer = AVSpeechSynthesizer()
    private var currentUtterance: AVSpeechUtterance?
    private var currentChunk: Chunk = .step(0)
    private var advance: DispatchWorkItem?
    private var remoteCommandsWired = false

    private static let rateKey = "plan.speech.rate"

    private enum Chunk {
        case step(Int)
        /// Spoken over the top of narration ("step 4 of 37"); `resume` says
        /// whether the plan should carry on afterwards.
        case announcement(resume: Bool)
    }

    private static var storedRate: Float {
        let stored = UserDefaults.standard.float(forKey: rateKey)
        return stored > 0 ? stored : AVSpeechUtteranceDefaultSpeechRate
    }

    init(plan: PlanDocument) {
        self.plan = plan
        super.init()
        synthesizer.delegate = self
        index = PlanProgress.step(for: plan)
        note("Loaded “\(plan.title)” — \(plan.steps.count) steps, ~\(plan.spokenMinutes) min.")
        note("Voice: \(Self.preferredVoice()?.name ?? "system default").")
    }

    var currentStep: PlanStep? {
        plan.steps.indices.contains(index) ? plan.steps[index] : nil
    }

    var positionDescription: String {
        "Step \(min(index + 1, plan.steps.count)) of \(plan.steps.count)"
    }

    // MARK: - Transport

    /// Opens the plan the way a listener expects: says where they are, then
    /// reads on without another tap.
    func begin() {
        configureAudioSession()
        wireRemoteCommands()
        let resuming = index > 0
        let opening = resuming
            ? "Resuming \(plan.title), step \(index + 1) of \(plan.steps.count)."
            : "\(plan.title). \(plan.steps.count) steps, about \(plan.spokenMinutes) minutes."
        announce(opening, thenResume: true)
    }

    func play() {
        configureAudioSession()
        if synthesizer.isPaused {
            synthesizer.continueSpeaking()
            isPaused = false
            isSpeaking = true
            updateNowPlaying()
            note("Resumed.")
            return
        }
        isFinished = false
        speak(step: index)
    }

    func pause() {
        advance?.cancel()
        advance = nil
        if synthesizer.isSpeaking {
            synthesizer.pauseSpeaking(at: .word)
        }
        isPaused = true
        isSpeaking = false
        updateNowPlaying()
        note("Paused at step \(index + 1).")
    }

    func togglePlayPause() {
        isSpeaking ? pause() : play()
    }

    func next() {
        move(to: index + 1)
    }

    func previous() {
        move(to: index - 1)
    }

    func repeatStep() {
        move(to: index)
    }

    func restart() {
        move(to: 0)
    }

    func jump(toSection section: String) {
        guard let target = plan.steps.firstIndex(where: { $0.kind == .heading && $0.display == section }) else { return }
        move(to: target)
    }

    /// Spoken orientation for a listener who has lost the thread.
    func announcePosition() {
        let section = currentStep?.section ?? ""
        let where_ = section.isEmpty ? "" : " In \(section)."
        announce("\(positionDescription).\(where_)", thenResume: isSpeaking)
    }

    /// Reads the headings back so a plan can be navigated without the screen.
    func announceSections() {
        let sections = plan.sections
        guard !sections.isEmpty else {
            announce("This plan has no sections.", thenResume: isSpeaking)
            return
        }
        announce("Sections: " + sections.joined(separator: ". ") + ".", thenResume: isSpeaking)
    }

    func faster() {
        rate = min(rate + 0.05, AVSpeechUtteranceMaximumSpeechRate)
        announce("Speed \(Int((rate / AVSpeechUtteranceDefaultSpeechRate) * 100)) percent.", thenResume: isSpeaking)
    }

    func slower() {
        rate = max(rate - 0.05, AVSpeechUtteranceMinimumSpeechRate)
        announce("Speed \(Int((rate / AVSpeechUtteranceDefaultSpeechRate) * 100)) percent.", thenResume: isSpeaking)
    }

    func stop() {
        advance?.cancel()
        advance = nil
        cancelCurrent()
        isSpeaking = false
        isPaused = false
        PlanProgress.save(step: index, for: plan)
        releaseRemoteCommands()
        deactivateAudioSession()
    }

    // MARK: - Speaking

    private func move(to target: Int) {
        guard !plan.steps.isEmpty else { return }
        let clamped = min(max(target, 0), plan.steps.count - 1)
        isFinished = false
        speak(step: clamped)
    }

    private func speak(step target: Int) {
        guard plan.steps.indices.contains(target) else { return }
        configureAudioSession()
        advance?.cancel()
        advance = nil
        cancelCurrent()

        index = target
        PlanProgress.save(step: target, for: plan)

        let utterance = makeUtterance(plan.steps[target].spoken)
        currentUtterance = utterance
        currentChunk = .step(target)
        isSpeaking = true
        isPaused = false
        updateNowPlaying()
        synthesizer.speak(utterance)
    }

    private func announce(_ text: String, thenResume: Bool) {
        configureAudioSession()
        advance?.cancel()
        advance = nil
        cancelCurrent()

        let utterance = makeUtterance(text)
        currentUtterance = utterance
        currentChunk = .announcement(resume: thenResume)
        isSpeaking = thenResume
        isPaused = false
        synthesizer.speak(utterance)
        note("Said: \(text)")
    }

    private func makeUtterance(_ text: String) -> AVSpeechUtterance {
        let utterance = AVSpeechUtterance(string: text)
        utterance.voice = Self.preferredVoice()
        utterance.rate = rate
        utterance.postUtteranceDelay = 0
        return utterance
    }

    /// Dropping the reference first means the delegate ignores the `didCancel`
    /// this stop is about to produce.
    private func cancelCurrent() {
        currentUtterance = nil
        if synthesizer.isSpeaking || synthesizer.isPaused {
            synthesizer.stopSpeaking(at: .immediate)
        }
    }

    private func finished(step target: Int) {
        guard target + 1 < plan.steps.count else {
            isSpeaking = false
            isPaused = false
            isFinished = true
            index = max(plan.steps.count - 1, 0)
            PlanProgress.save(step: 0, for: plan)
            updateNowPlaying()
            note("Reached the end of the plan.")
            let closing = makeUtterance("End of plan.")
            currentUtterance = closing
            currentChunk = .announcement(resume: false)
            synthesizer.speak(closing)
            return
        }

        index = target + 1
        PlanProgress.save(step: index, for: plan)
        updateNowPlaying()

        // A beat between steps: long enough to hear the seam (and to get a
        // voice command in), short enough that the plan still flows.
        let next = plan.steps[index]
        let gap = next.kind == .heading ? 0.8 : 0.45
        let work = DispatchWorkItem { [weak self] in
            guard let self, self.isSpeaking else { return }
            self.speak(step: self.index)
        }
        advance = work
        DispatchQueue.main.asyncAfter(deadline: .now() + gap, execute: work)
    }

    static func preferredVoice() -> AVSpeechSynthesisVoice? {
        let language = AVSpeechSynthesisVoice.currentLanguageCode()
        let candidates = AVSpeechSynthesisVoice.speechVoices().filter { $0.language == language }
        // A downloaded enhanced/premium voice is dramatically easier to listen
        // to for half an hour; fall back to whatever the system has.
        if #available(iOS 16.0, macOS 13.0, *) {
            if let premium = candidates.first(where: { $0.quality == .premium }) { return premium }
        }
        if let enhanced = candidates.first(where: { $0.quality == .enhanced }) { return enhanced }
        return AVSpeechSynthesisVoice(language: language) ?? candidates.first
    }

    // MARK: - Diagnostics

    func note(_ message: String) {
        let stamp = Self.stampFormatter.string(from: Date())
        onMain {
            self.log.append("[\(stamp)] \(message)")
            if self.log.count > 400 { self.log.removeFirst(self.log.count - 400) }
        }
    }

    var logText: String {
        ([
            "Plan: \(plan.title) (\(plan.source))",
            "Steps: \(plan.steps.count) · words: \(plan.wordCount) · rate: \(rate)",
            "Position: \(positionDescription) · speaking: \(isSpeaking) · paused: \(isPaused)"
        ] + log).joined(separator: "\n")
    }

    private static let stampFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm:ss"
        return formatter
    }()

    private func onMain(_ work: @escaping () -> Void) {
        if Thread.isMainThread { work() } else { DispatchQueue.main.async(execute: work) }
    }

    // MARK: - Audio session & remote control

    /// `.playback`/`.spokenAudio` is what lets narration continue with the
    /// screen locked; `PlanVoiceControl` swaps in a recording category while it
    /// is listening and hands it back here when it stops.
    func configureAudioSession() {
        #if os(iOS)
        do {
            let session = AVAudioSession.sharedInstance()
            if session.category != .playAndRecord {
                try session.setCategory(.playback, mode: .spokenAudio, options: [.duckOthers])
            }
            try session.setActive(true)
        } catch {
            note("Audio session error: \(error.localizedDescription)")
        }
        #endif
    }

    private func deactivateAudioSession() {
        #if os(iOS)
        try? AVAudioSession.sharedInstance().setActive(false, options: [.notifyOthersOnDeactivation])
        #endif
    }

    private func wireRemoteCommands() {
        #if canImport(MediaPlayer)
        guard !remoteCommandsWired else { return }
        remoteCommandsWired = true
        let center = MPRemoteCommandCenter.shared()

        center.playCommand.addTarget { [weak self] _ in
            self?.onMain { self?.play() }
            return .success
        }
        center.pauseCommand.addTarget { [weak self] _ in
            self?.onMain { self?.pause() }
            return .success
        }
        center.togglePlayPauseCommand.addTarget { [weak self] _ in
            self?.onMain { self?.togglePlayPause() }
            return .success
        }
        center.nextTrackCommand.addTarget { [weak self] _ in
            self?.onMain { self?.next() }
            return .success
        }
        center.previousTrackCommand.addTarget { [weak self] _ in
            self?.onMain { self?.previous() }
            return .success
        }
        [center.playCommand, center.pauseCommand, center.togglePlayPauseCommand,
         center.nextTrackCommand, center.previousTrackCommand].forEach { $0.isEnabled = true }
        note("Headphone and lock-screen controls wired (play, pause, next, back).")
        #endif
    }

    private func releaseRemoteCommands() {
        #if canImport(MediaPlayer)
        guard remoteCommandsWired else { return }
        remoteCommandsWired = false
        let center = MPRemoteCommandCenter.shared()
        [center.playCommand, center.pauseCommand, center.togglePlayPauseCommand,
         center.nextTrackCommand, center.previousTrackCommand].forEach { $0.removeTarget(nil) }
        MPNowPlayingInfoCenter.default().nowPlayingInfo = nil
        #endif
    }

    private func updateNowPlaying() {
        #if canImport(MediaPlayer)
        let section = currentStep?.section ?? ""
        var info: [String: Any] = [
            MPMediaItemPropertyTitle: section.isEmpty ? plan.title : section,
            MPMediaItemPropertyArtist: plan.title,
            MPMediaItemPropertyAlbumTitle: positionDescription,
            MPNowPlayingInfoPropertyPlaybackRate: isSpeaking ? 1.0 : 0.0
        ]
        info[MPNowPlayingInfoPropertyPlaybackQueueCount] = plan.steps.count
        info[MPNowPlayingInfoPropertyPlaybackQueueIndex] = index
        MPNowPlayingInfoCenter.default().nowPlayingInfo = info
        #endif
    }
}

extension PlanNarrator: AVSpeechSynthesizerDelegate {
    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didFinish utterance: AVSpeechUtterance) {
        onMain {
            guard utterance === self.currentUtterance else { return }
            self.currentUtterance = nil
            switch self.currentChunk {
            case .step(let target):
                self.finished(step: target)
            case .announcement(let resume):
                if resume {
                    self.speak(step: self.index)
                } else {
                    self.isSpeaking = false
                    self.updateNowPlaying()
                }
            }
        }
    }

    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didCancel utterance: AVSpeechUtterance) {
        onMain {
            guard utterance === self.currentUtterance else { return }
            self.currentUtterance = nil
        }
    }
}
