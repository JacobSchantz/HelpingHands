# Surgical micro-gripper reference study (voice-ef49247b)

The browsable result is `cad/mobile_gallery/micro_grippers/index.html`, copied
by the existing publisher without CAD execution. It links the primary references
and distinguishes proprietary reference, downloadable visualization meshes and
manufacturing rights. No design version or print geometry changes in this study.

Hardware feedback arrived during the pass. The gallery includes source-mesh
exploded closeups and the interface comparison. Delivered bolt count is9 before
and9 after; a possible9-to7 keyed-cradle reduction is a proposal only. It must
resolve reaction torque, axial capture, screw access and loosening before CAD
is versioned. The cable/spring fine-motion concept may add parts.

## Reproduce the measurements and render

From the repository root, download the servo STEP to a temporary directory:

```sh
curl -L https://raw.githubusercontent.com/TheRobotStudio/SO-ARM100/a758567c3978dfeefe282ede0500085a48fe8f78/STEP/SO100/STS3215_03a.step -o /tmp/STS3215_03a.step
cad/build123d/.venv/bin/python cad/reference/micro_grippers/inspect_sts.py /tmp/STS3215_03a.step cad/reference/micro_grippers/sts_measurements.json /tmp/sts3215.stl
cad/blender/.venv/bin/python cad/reference/micro_grippers/render_hardware.py /tmp/sts3215.stl
```

`inspect_sts.py` also inspects the retained pinned SO-101 fixed-jaw STEP. Its
four3.2 mm bores independently match the servo's14 mm PCD. STS case front
cylinders have modeled1.5 mm diameter and axial length; those are not verified
usable thread depth. The SO-101 assembly guide specifies the thread sizes and
installation counts: https://huggingface.co/docs/lerobot/so101#gripper--handle

`hls_measurements.json` is a fresh run of v326's existing `check_hardware.py`
against a scratch copy of its reference/exports/params/source. Running it there
avoided writing anything into the accepted print candidate. Input hashes are
included. The original checker still lives with the design.

HLS drawing: retained `reference/HLS3606M-C001.pdf`, editionA/0,22April2024,
pages4,6,7, also https://www.feetechrc.com/Data/feetechrc/upload/file/20240807/6385862508379674057566108.pdf
Aero STEP provenance: retained v326 `reference/provenance.json`, upstream
7bb2f23485a7d440960c21046da642de132b7745, servo solid304 / plate248. Drawing
p7 explicitly calls8-M2 onØ12; the supplied production revision and physical
thread pitch/depth still require inspection. P6 ears differ longitudinally by
0.25 mm from the pinned STEP; existing pilot slots account for it. Nominal
center-screw floor margin is only0.2 mm. Tilted driver engagement is unmeasured.

The rendered STS front horn and center-head regions are sliced from the source
mesh and separated for inspection; they are not reconstructed manufacturing
parts. Modeled internal/vendor screws visible in reference motors are not extra
installation bolts. No source CAD was incorporated into a new mechanism.

Desktop and CDP390 px mobile rendering checked; all gallery images loaded and
mobile scrollWidth==innerWidth==390. The18 existing gallery/publisher tests
passed. No physical phone, motor motion, strength, actual hardware revision,
anti-loosening treatment or clinical suitability was verified.
