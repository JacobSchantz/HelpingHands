import SwiftUI
import PebblesKit

@main
struct HelpingHandsApp: App {
    #if os(macOS)
    @NSApplicationDelegateAdaptor(AeroURLDelegate.self) private var aeroURLs
    #endif

    var body: some Scene {
        WindowGroup {
            DesignViewerScreen()
                .preferredColorScheme(.dark)
                .pebblesOverlay()
        }
        #if os(macOS)
        Window("Aero Hand", id: "aero-hand") {
            AeroHandPanel()
                .preferredColorScheme(.dark)
        }
        .keyboardShortcut("h", modifiers: [.command, .shift])
        #endif
    }
}
