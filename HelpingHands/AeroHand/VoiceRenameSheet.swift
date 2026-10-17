#if os(macOS)
import AVFoundation
import Speech
import SwiftUI

/// Renaming a recording by voice: opens already listening, shows the words as they're heard,
/// and saves after a short pause. Enter or Save saves now; typing takes over from the mic.
struct VoiceRenameSheet: View {
    let take: AeroTake
    let save: (String) -> Void
    @StateObject private var dictation = Dictation()
    @State private var text = ""
    @State private var typed = false
    @Environment(\.dismiss) private var dismiss

    /// Silence after the last heard word before the name saves itself.
    private static let pause: Duration = .seconds(1.5)

    var body: some View {
        VStack(alignment: .leading, spacing: 24) {
            Label(dictation.status, systemImage: dictation.listening ? "mic.fill" : "mic.slash")
                .font(.system(size: 26, weight: .bold))
                .foregroundStyle(dictation.listening ? .red : .secondary)
            TextField(take.name.isEmpty ? "Say a name" : take.name,
                      text: Binding(get: { text }, set: { text = $0; typed = true }))
                .font(.system(size: 36, weight: .bold))
                .textFieldStyle(.plain)
                .onSubmit(commit)
            HStack {
                Button("Cancel", role: .cancel) { dismiss() }
                    .keyboardShortcut(.cancelAction)
                Spacer()
                Button("Save", action: commit)
                    .keyboardShortcut(.defaultAction)
                    .disabled(text.trimmingCharacters(in: .whitespaces).isEmpty)
            }
            .font(.system(size: 22))
        }
        .padding(32)
        .frame(width: 640)
        .onAppear { dictation.start() }
        .onDisappear { dictation.stop() }
        .onChange(of: dictation.transcript) { _, heard in
            if !typed { text = heard }
        }
        .task(id: dictation.transcript) {
            guard !dictation.transcript.isEmpty, !typed else { return }
            try? await Task.sleep(for: Self.pause)
            if !Task.isCancelled { commit() }
        }
    }

    private func commit() {
        let name = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !name.isEmpty else { return }
        dictation.stop()
        save(name)
        dismiss()
    }
}

/// Live speech-to-text from the Mac's microphone (on-device when it can be).
@MainActor
final class Dictation: ObservableObject {
    @Published private(set) var transcript = ""
    @Published private(set) var listening = false
    @Published private(set) var status = "Starting the mic…"

    private let recognizer = SFSpeechRecognizer(locale: Locale.current) ?? SFSpeechRecognizer()
    private let engine = AVAudioEngine()
    private var request: SFSpeechAudioBufferRecognitionRequest?
    private var task: SFSpeechRecognitionTask?

    func start() {
        guard let recognizer, recognizer.isAvailable else {
            status = "Speech recognition unavailable; type the name"
            return
        }
        SFSpeechRecognizer.requestAuthorization { auth in
            Task { @MainActor in
                guard auth == .authorized else {
                    self.status = "Speech recognition not allowed (System Settings ▸ Privacy); type the name"
                    return
                }
                self.listen(with: recognizer)
            }
        }
    }

    func stop() {
        task?.cancel()
        task = nil
        request?.endAudio()
        request = nil
        if engine.isRunning {
            engine.stop()
            engine.inputNode.removeTap(onBus: 0)
        }
        listening = false
    }

    private func listen(with recognizer: SFSpeechRecognizer) {
        let request = SFSpeechAudioBufferRecognitionRequest()
        request.shouldReportPartialResults = true
        request.requiresOnDeviceRecognition = recognizer.supportsOnDeviceRecognition
        self.request = request
        let input = engine.inputNode
        input.installTap(onBus: 0, bufferSize: 1024, format: input.outputFormat(forBus: 0),
                         block: Self.feed(request))
        engine.prepare()
        do {
            try engine.start()
        } catch {
            status = "Mic didn't start (\(error.localizedDescription)); type the name"
            return
        }
        listening = true
        status = "Listening… say the name"
        task = recognizer.recognitionTask(with: request, resultHandler: Self.results { heard, failed in
            if let heard { self.transcript = heard }
            if failed, self.listening {
                self.stop()
                self.status = "Stopped listening; type the name or press Save"
            }
        })
    }

    // Built outside the main actor: the audio tap and the recogniser call these on their own threads.
    nonisolated private static func feed(_ request: SFSpeechAudioBufferRecognitionRequest) -> AVAudioNodeTapBlock {
        { buffer, _ in request.append(buffer) }
    }

    nonisolated private static func results(
        _ handle: @escaping @MainActor (String?, Bool) -> Void
    ) -> (SFSpeechRecognitionResult?, Error?) -> Void {
        { result, error in
            let heard = result?.bestTranscription.formattedString
            Task { @MainActor in handle(heard, error != nil) }
        }
    }
}
#endif
