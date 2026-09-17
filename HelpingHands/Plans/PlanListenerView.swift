import SwiftUI

/// The listening screen. It starts reading on open and keeps reading to the
/// end, so the screen is there to *look at if you want to* — every control has
/// an eyes-free twin: a full-screen gesture, a headphone button, or a spoken
/// command.
struct PlanListenerView: View {
    let plan: PlanDocument

    @StateObject private var narrator: PlanNarrator
    @StateObject private var voice = PlanVoiceControl()
    @State private var copied = false
    @State private var showingLog = false

    init(plan: PlanDocument) {
        self.plan = plan
        _narrator = StateObject(wrappedValue: PlanNarrator(plan: plan))
    }

    var body: some View {
        VStack(spacing: 18) {
            heading
            stage
            transport
            secondaryControls
            voiceRow
        }
        .padding(20)
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top)
        .background(Color(red: 0.05, green: 0.12, blue: 0.16).ignoresSafeArea())
        .navigationTitle(plan.title)
        #if os(iOS)
        .navigationBarTitleDisplayMode(.inline)
        #endif
        .toolbar {
            ToolbarItem {
                Menu {
                    ForEach(plan.sections, id: \.self) { section in
                        Button(section) { narrator.jump(toSection: section) }
                    }
                    Divider()
                    Button("Listening log") { showingLog = true }
                } label: {
                    Label("Sections", systemImage: "list.bullet")
                }
            }
        }
        .sheet(isPresented: $showingLog) { logSheet }
        .onAppear(perform: startListening)
        .onDisappear {
            voice.stop()
            narrator.stop()
        }
    }

    // MARK: - Pieces

    private var heading: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(narrator.currentStep?.section ?? plan.title)
                .font(.headline)
                .foregroundStyle(Color.accentColor)
            ProgressView(value: Double(narrator.index + 1), total: Double(max(plan.steps.count, 1)))
                .tint(Color.accentColor)
            Text("\(narrator.positionDescription) · \(plan.summaryLine)")
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .accessibilityElement(children: .combine)
    }

    /// The whole middle of the screen is the remote control: tap to pause,
    /// swipe sideways to move a step, down to hear it again, up for the section
    /// list. No button to find, so it works with the phone in a pocket-glance.
    private var stage: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text(narrator.currentStep?.display ?? "Ready.")
                .font(.title3)
                .lineSpacing(4)
                .minimumScaleFactor(0.6)
                .frame(maxWidth: .infinity, alignment: .leading)
            if narrator.isFinished {
                Text("End of plan.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }
            Text("Tap to pause · swipe ← → to move · swipe ↓ to repeat · ↑ for sections")
                .font(.caption2)
                .foregroundStyle(.secondary)
        }
        .padding(18)
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 20, style: .continuous))
        .contentShape(Rectangle())
        .onTapGesture { narrator.togglePlayPause() }
        .gesture(
            DragGesture(minimumDistance: 40)
                .onEnded { value in
                    let horizontal = value.translation.width
                    let vertical = value.translation.height
                    if abs(horizontal) > abs(vertical) {
                        horizontal < 0 ? narrator.next() : narrator.previous()
                    } else {
                        vertical > 0 ? narrator.repeatStep() : narrator.announceSections()
                    }
                }
        )
        .accessibilityLabel("Current step")
        .accessibilityValue(narrator.currentStep?.display ?? "Ready")
    }

    private var transport: some View {
        HStack(spacing: 24) {
            transportButton("backward.fill", "Previous step", action: narrator.previous)
            Button(action: narrator.togglePlayPause) {
                Image(systemName: narrator.isSpeaking ? "pause.circle.fill" : "play.circle.fill")
                    .font(.system(size: 72))
                    .foregroundStyle(Color.accentColor)
            }
            .buttonStyle(.plain)
            .accessibilityLabel(narrator.isSpeaking ? "Pause" : "Play")
            transportButton("forward.fill", "Next step", action: narrator.next)
        }
    }

    private func transportButton(_ symbol: String, _ label: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Image(systemName: symbol)
                .font(.system(size: 34))
                .frame(width: 64, height: 64)
                .background(.ultraThinMaterial, in: Circle())
        }
        .buttonStyle(.plain)
        .accessibilityLabel(label)
    }

    private var secondaryControls: some View {
        HStack(spacing: 10) {
            smallButton("arrow.counterclockwise", "Repeat", action: narrator.repeatStep)
            smallButton("backward.end.fill", "Start over", action: narrator.restart)
            smallButton("tortoise.fill", "Slower", action: narrator.slower)
            smallButton("hare.fill", "Faster", action: narrator.faster)
            smallButton("location.fill", "Where am I", action: narrator.announcePosition)
        }
    }

    private func smallButton(_ symbol: String, _ label: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            VStack(spacing: 4) {
                Image(systemName: symbol).font(.body)
                Text(label).font(.caption2)
            }
            .frame(maxWidth: .infinity, minHeight: 52)
            .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12, style: .continuous))
        }
        .buttonStyle(.plain)
        .accessibilityLabel(label)
    }

    private var voiceRow: some View {
        VStack(spacing: 8) {
            Button {
                voice.toggle()
            } label: {
                HStack(spacing: 10) {
                    Image(systemName: voice.isListening ? "mic.fill" : "mic.slash")
                    VStack(alignment: .leading, spacing: 2) {
                        Text(voice.isListening ? "Voice control on" : "Voice control off")
                            .font(.subheadline.weight(.semibold))
                        Text(voice.isListening
                             ? "Say next, back, repeat, pause, resume, where am I"
                             : "Turn on to run the plan hands-free")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                    Spacer()
                }
                .padding(14)
                .frame(maxWidth: .infinity)
                .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 14, style: .continuous))
            }
            .buttonStyle(.plain)

            if voice.isListening, !voice.lastHeard.isEmpty {
                Text("Heard: \(voice.lastHeard)")
                    .font(.caption2)
                    .foregroundStyle(.secondary)
                    .frame(maxWidth: .infinity, alignment: .leading)
            }

            Button {
                PlanClipboard.write(logText)
                copied = true
            } label: {
                Label(copied ? "Log copied" : "Copy listening log", systemImage: copied ? "checkmark" : "doc.on.doc")
                    .font(.caption)
            }
            .buttonStyle(.plain)
            .foregroundStyle(.secondary)
        }
    }

    private var logSheet: some View {
        NavigationStack {
            ScrollView {
                Text(logText)
                    .font(.caption.monospaced())
                    .textSelection(.enabled)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding()
            }
            .navigationTitle("Listening log")
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Copy") {
                        PlanClipboard.write(logText)
                        copied = true
                    }
                }
            }
        }
    }

    private var logText: String {
        narrator.logText + "\nVoice control: \(voice.status)"
    }

    // MARK: - Wiring

    private func startListening() {
        let narrator = self.narrator
        voice.spokenTextProvider = { [weak narrator] in narrator?.currentStep?.spoken ?? "" }
        voice.onLog = { [weak narrator] message in narrator?.note("Voice: \(message)") }
        voice.onStop = { [weak narrator] in narrator?.configureAudioSession() }
        voice.onCommand = { [weak narrator] command in
            guard let narrator else { return }
            switch command {
            case .next: narrator.next()
            case .back: narrator.previous()
            case .again: narrator.repeatStep()
            case .pause: narrator.pause()
            case .resume: narrator.play()
            case .restart: narrator.restart()
            case .whereAmI: narrator.announcePosition()
            case .sections: narrator.announceSections()
            case .faster: narrator.faster()
            case .slower: narrator.slower()
            }
        }
        narrator.begin()
    }
}
