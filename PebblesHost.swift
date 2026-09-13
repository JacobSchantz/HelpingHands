import SwiftUI
import PebblesKit

/// Wired by `pebbles setup`. Overlay the banner with:
///   `.pebblesOverlay()` on the root view (WindowGroup content).
extension PebblesViewModel {
    static let shared = PebblesViewModel(config: PebblesConfig(
        githubRepo: "JacobSchantz/HelpingHands",
        patKey: "github_pat_for_helpinghands_pebbles",
        pebblesPath: "pebbles",
        currentCommitHash: GitInfo.fullHash,
        commitCount: GitInfo.commitCount
    ))
}

extension View {
    func pebblesOverlay() -> some View {
        overlay(alignment: .top) {
            PebblesBannerView(config: PebblesViewModel.shared.config, devScreens: [])
        }
    }
}
