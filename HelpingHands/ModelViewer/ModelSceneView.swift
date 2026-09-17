import SwiftUI
import SceneKit

#if os(macOS)
typealias PlatformColor = NSColor
#else
typealias PlatformColor = UIColor
#endif

/// Wraps a `LoadedModel` in a framed SceneKit scene. SwiftUI's `SceneView`
/// handles the pinch/drag camera on both iOS and macOS, so the only work here
/// is building the scene, orienting it Y-up, and parking the camera far enough
/// out that the whole part is in frame.
struct ModelSceneView: View {
    let model: LoadedModel
    var wireframe: Bool
    var spinning: Bool
    /// Bumping this rebuilds the camera, which is how "Reset view" works —
    /// `allowsCameraControl` mutates the node in place, so a fresh node is the
    /// only way back to the framing we chose.
    var cameraGeneration: Int

    var body: some View {
        SceneView(
            scene: makeScene(),
            pointOfView: makeCamera(),
            options: [.allowsCameraControl, .autoenablesDefaultLighting],
            antialiasingMode: .multisampling2X
        )
        .id(cameraGeneration)
    }

    private func makeScene() -> SCNScene {
        let scene = SCNScene()
        scene.background.contents = PlatformColor(red: 0.05, green: 0.10, blue: 0.14, alpha: 1)

        let material = SCNMaterial()
        material.lightingModel = .physicallyBased
        material.diffuse.contents = PlatformColor(red: 0.62, green: 0.68, blue: 0.74, alpha: 1)
        material.metalness.contents = 0.25
        material.roughness.contents = 0.45
        material.isDoubleSided = true
        material.fillMode = wireframe ? .lines : .fill

        let content = model.node.clone()
        apply(material, to: content)
        // Shift the part so its centre sits on the origin; the camera and the
        // spin action both pivot around that.
        content.simdPosition = -model.center

        let pivot = SCNNode()
        pivot.addChildNode(content)
        // CAD exports are Z-up, SceneKit is Y-up.
        pivot.simdEulerAngles = SIMD3<Float>(-.pi / 2, 0, 0)

        let spinner = SCNNode()
        spinner.addChildNode(pivot)
        if spinning {
            spinner.runAction(.repeatForever(.rotateBy(x: 0, y: .pi * 2, z: 0, duration: 14)))
        }
        scene.rootNode.addChildNode(spinner)

        let ambient = SCNNode()
        ambient.light = SCNLight()
        ambient.light?.type = .ambient
        ambient.light?.intensity = 350
        scene.rootNode.addChildNode(ambient)

        let key = SCNNode()
        key.light = SCNLight()
        key.light?.type = .directional
        key.light?.intensity = 700
        key.simdEulerAngles = SIMD3<Float>(-0.9, 0.6, 0)
        scene.rootNode.addChildNode(key)

        return scene
    }

    private func apply(_ material: SCNMaterial, to node: SCNNode) {
        node.geometry?.materials = [material]
        node.childNodes.forEach { apply(material, to: $0) }
    }

    private func makeCamera() -> SCNNode {
        let camera = SCNCamera()
        camera.fieldOfView = 45
        let radius = model.boundingRadius
        // Pull back far enough for the bounding sphere plus a little air, and
        // widen the clipping range so big and tiny parts both survive.
        let distance = radius / tan(Float(camera.fieldOfView / 2) * .pi / 180) * 1.5
        camera.zNear = Double(max(radius * 0.01, 0.01))
        camera.zFar = Double(distance * 10)

        let node = SCNNode()
        node.camera = camera
        node.simdPosition = SIMD3<Float>(distance * 0.55, distance * 0.45, distance * 0.75)
        node.simdLook(at: .zero, up: SIMD3<Float>(0, 1, 0), localFront: SIMD3<Float>(0, 0, -1))
        return node
    }
}
