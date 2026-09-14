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
                    teleopNote
                }
                .padding(20)
            }
            .background(Color(red: 0.05, green: 0.12, blue: 0.16).ignoresSafeArea())
            .navigationTitle("Helping Hands")
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
