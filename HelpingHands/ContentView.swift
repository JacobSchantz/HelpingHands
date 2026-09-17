import SwiftUI

struct ContentView: View {
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    header
                    armCard(
                        role: "Leader",
                        id: "leader_left",
                        type: "so101_leader",
                        port: "/dev/tty.usbmodem5AAF2627031",
                        icon: "hand.raised.fill"
                    )
                    armCard(
                        role: "Follower",
                        id: "follower_right",
                        type: "so101_follower",
                        port: "/dev/tty.usbmodem5AA90242401",
                        icon: "hand.point.right.fill"
                    )
                    plansCard
                    cadCard
                    teleopNote
                }
                .padding(20)
            }
            .background(Color(red: 0.05, green: 0.12, blue: 0.16).ignoresSafeArea())
            .navigationTitle("Helping Hands")
            .navigationDestination(for: CADModel.self) { ModelDetailView(model: $0) }
        }
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("iBackpack")
                .font(.title2.weight(.semibold))
            Text("SO-101 wearable arms. Teleop still runs from a native Mac terminal so the control loop stays jitter-free.")
                .font(.subheadline)
                .foregroundStyle(.secondary)
        }
    }

    private func armCard(role: String, id: String, type: String, port: String, icon: String) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(spacing: 10) {
                Image(systemName: icon)
                    .font(.title3)
                    .foregroundStyle(Color.accentColor)
                Text(role)
                    .font(.headline)
                Spacer()
                Text(id)
                    .font(.caption.monospaced())
                    .foregroundStyle(.secondary)
            }
            labeled("Type", type)
            labeled("Port", port)
        }
        .padding(16)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
    }

    private var plansCard: some View {
        NavigationLink {
            PlansScreen()
        } label: {
            VStack(alignment: .leading, spacing: 10) {
                HStack(spacing: 10) {
                    Image(systemName: "waveform")
                        .font(.title3)
                        .foregroundStyle(Color.accentColor)
                    Text("Listen to a plan")
                        .font(.headline)
                    Spacer()
                    Image(systemName: "chevron.right")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                Text("Every plan in plans/, read aloud start to finish — or paste one in. Hands-free: AirPods and lock-screen controls, swipe gestures, and spoken commands.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.leading)
            }
            .padding(16)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
        }
        .buttonStyle(.plain)
    }

    private var cadCard: some View {
        NavigationLink {
            ModelViewerScreen()
        } label: {
            VStack(alignment: .leading, spacing: 10) {
                HStack(spacing: 10) {
                    Image(systemName: "cube.transparent")
                        .font(.title3)
                        .foregroundStyle(Color.accentColor)
                    Text("Gripper CAD")
                        .font(.headline)
                    Spacer()
                    Image(systemName: "chevron.right")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                Text("View the SO-101 gripper meshes from the OpenSCAD, Blender and build123d bake-off, or import your own 3D file.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.leading)
            }
            .padding(16)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
        }
        .buttonStyle(.plain)
    }

    private func labeled(_ title: String, _ value: String) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(title)
                .font(.caption)
                .foregroundStyle(.secondary)
            Text(value)
                .font(.footnote.monospaced())
                .textSelection(.enabled)
        }
    }

    private var teleopNote: some View {
        Text("Run `bash teleop.sh` in Terminal.app. Calibration lives in lerobot_calibration/.")
            .font(.footnote)
            .foregroundStyle(.secondary)
    }
}
