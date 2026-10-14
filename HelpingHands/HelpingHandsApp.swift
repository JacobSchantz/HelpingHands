import SwiftUI
import PebblesKit

@main
struct HelpingHandsApp: App {
    var body: some Scene {
        WindowGroup {
            DesignViewerScreen()
                .preferredColorScheme(.dark)
                .pebblesOverlay()
        }
    }
}
