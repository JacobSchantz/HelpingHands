# Aero source inspection — paused

This folder preserves a source inspection started when Jake requested an Aero
finger scale study. Work stopped when Jake redirected the task to comparing
MIT-licensed mechanical hands. No finger STLs were extracted or scaled here.

These are **Aero upstream reference files**, not original HelpingHands CAD and
not MIT-licensed assets. Do not include them in an MIT CAD release.

The source is [Chestnut Robotics / Aero Hand Open](https://github.com/Chestnut-Robotics/aero-hand-open)
at commit `7bb2f23485a7d440960c21046da642de132b7745`:

| Local source | Upstream path | SHA-256 |
| --- | --- | --- |
| `source/One_Click_Print_L.3mf` | `hardware/CAD/One_Click_Print_L.3mf` | `0d0c7ae3831ebd585cb2659949d2015e69e862fd14d7a21b8d04352d0d49a2d9` |
| `source/HARDWARE_LICENSE.txt` | `hardware/LICENSE` | `75da7fb1c7271d79b23e48638baf4d7de28f99940c31c6af274bf369dffd74fd` |
| `source/UPSTREAM_LICENSING.md` | `LICENSE.md` | `43bac57ebd06208a7b1f5bcf59a31ca8fd5ef56f936d5c7d12fd56f797b001a7` |

`source/3dmodel.model`, `source/model_settings.config` and
`source/project_settings.config` are unmodified entries extracted from that
3MF for inspection. The 3MF contains the upstream manufacturing plate, rather
than the ROS simulation meshes.

Aero identifies the hardware and documentation license as
**CC BY-NC-SA 4.0**. The complete supplied notices are retained in `source/`.
This entails attribution, a noncommercial condition and the same license for
shared adaptations; the upstream licensing document describes separate
commercial licensing. Inspection does not establish print quality or fit, and
uniform scaling would also scale holes and hardware interfaces.
