# strawberry — Gazebo models

Six **static, textured** strawberry plant models, promoted from
`cad_assets_studio/strawberry`. Each is `model.config` + `model.sdf` + `meshes/`
+ `textures/`, upright (pose `1.5708 0 1.5708` baked in), no collision.

| Model | State |
|---|---|
| `strawberry_ripe` | red berries (pickable) |
| `strawberry_halfripe` | pink-white berries |
| `strawberry_unripe` | green berries |
| `strawberry_flower` | flowering |
| `strawberry_mildew` | powdery mildew — UV-C target |
| `strawberry_leafscorch` | leaf scorch |

Reference as `model://strawberry_<state>` (add this dir to `GAZEBO_MODEL_PATH` —
it is two levels under `models/`). Scene world: `worlds/strawberry_farm.world`.
Pipeline + sources: the **crop-asset-pipeline** skill and `cad_assets_studio/`.
