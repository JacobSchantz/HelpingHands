import SwiftUI
import PebblesKit

@main
struct HelpingHandsApp: App {
    #if os(macOS)
    @NSApplicationDelegateAdaptor(AeroURLDelegate.self) private var aeroURLs
    #endif

    var body: some Scene {
        // On the Mac this is a single `Window`, not a `WindowGroup`: there is no
        // File › New Window, a Dock click reopens the same window, and
        // helpinghands:// URLs go to AeroURLDelegate instead of spawning windows.
        #if os(macOS)
        Window("Helping Hands", id: "main") { root }
            .keyboardShortcut("h", modifiers: [.command, .shift])
        #else
        WindowGroup { root }
        #endif
    }

    private var root: some View {
        RootTabs()
            .preferredColorScheme(.dark)
            .pebblesOverlay()
    }
}

/// The whole app: the Aero Hand controls, the designs, and the workshop
/// (arms, build guide, plans, every 3D file), one tab each.
struct RootTabs: View {
    private enum Tab: Hashable { case aeroHand, designs, workshop }

    #if os(macOS)
    @State private var tab = Tab.aeroHand
    @ObservedObject private var repo = RepoDesigns.shared
    #else
    @State private var tab = Tab.designs
    #endif

    var body: some View {
        TabView(selection: $tab) {
            AeroHandTab()
                .tabItem { Label("Aero Hand", systemImage: "hand.raised.fingers.spread.fill") }
                .tag(Tab.aeroHand)
            designs
                .tabItem { Label("Designs", systemImage: "cube.transparent") }
                .tag(Tab.designs)
            NavigationStack { WorkshopScreen() }
                .tabItem { Label("Workshop", systemImage: "wrench.and.screwdriver") }
                .tag(Tab.workshop)
        }
        #if os(macOS)
        // "work on <design>" (design.sh / helpinghands://designs/<name>): the
        // workbench covers the whole window, which RepoDesigns makes full screen.
        .overlay {
            if let open = repo.open { DesignWorkbenchView(design: open).transition(.opacity) }
        }
        .onChange(of: repo.open?.id) { _, id in if id != nil { tab = .designs } }
        #endif
    }

    /// On the Mac next to its checkout, the designs as they are on disk right
    /// now (agents' unfinished work included); elsewhere, the ones baked into the build.
    @ViewBuilder private var designs: some View {
        #if os(macOS)
        if repo.available { RepoDesignsScreen() } else { DesignViewerScreen() }
        #else
        DesignViewerScreen()
        #endif
    }
}

/// The controls spawn the aero_hand scripts and talk to the hand over USB, so
/// they only run on the Mac; the phone's tab says where to find them.
private struct AeroHandTab: View {
    var body: some View {
        #if os(macOS)
        AeroHandPanel()
        #else
        VStack(spacing: 12) {
            Image(systemName: "desktopcomputer")
                .font(.largeTitle)
                .foregroundStyle(.secondary)
            Text("The Aero Hand is plugged into the Mac. Open Helping Hands there to drive it.")
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)
                .padding(.horizontal, 32)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color(red: 0.05, green: 0.12, blue: 0.16).ignoresSafeArea())
        #endif
    }
}
