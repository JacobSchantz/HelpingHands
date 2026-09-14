import SwiftUI
import PebblesKit

@main
struct HelpingHandsApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .preferredColorScheme(.dark)
                .pebblesOverlay()
        }
    }
}
