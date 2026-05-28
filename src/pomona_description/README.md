# pomona_description

URDF / xacro / meshes for **Pomona** — shared by `pomona_gazebo` (sim) and
`pomona_bringup` (real robot). Launch-only package, no nodes.

## Robot composition

| Component        | Make / Model            | Xacro file              |
|------------------|-------------------------|-------------------------|
| Mobile base      | AgileX Scout V2         | `scout_v2.xacro`        |
| Wheels (4×)      | scout type1 / type2     | `scout_wheel_type{1,2}.xacro` |
| Manipulator      | UFactory xArm6 (6-DOF)  | `xarm6.xacro`           |
| Gripper          | DH Robotics AG95        | `ag95_gripper.xacro`    |
| Sensors          | rslidar / Xsens / D435  | `sensors.xacro`         |
| Sim plugins      | gazebo_ros classic 11   | `gazebo_plugins.xacro`  |
| Root             | combines all above      | `pomona.xacro`          |

## Use

### Standalone viewer (no Gazebo, no real robot)
```bash
ros2 launch pomona_description display.launch.py
```

### From another package (xacro at launch time)
```python
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution
from launch_ros.descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare

xacro_path = PathJoinSubstitution([
    FindPackageShare("pomona_description"), "urdf", "xacro", "pomona.xacro"
])
robot_description = ParameterValue(
    Command([FindExecutable(name="xacro"), " ", xacro_path, " use_sim:=true"]),
    value_type=str,
)
```

The single `use_sim:=true/false` switch toggles whether the Gazebo plugin
block is included.

### Pre-baked URDF (for SDF pipeline)
```bash
bash scripts/xacro_to_urdf.sh
# generates urdf/urdf/{pomona.urdf, pomona_sim.urdf}
```

## Geometry reference

- Scout V2 base: 0.925 × 0.380 × 0.210 m, wheelbase 0.498, track 0.583
- Wheel radius 0.165 m, wheel length 0.117 m, 4 wheels skid-steer
- xArm6 mount on Scout base: xyz=(0.212, 0, 0.26) — from real robot
- AG95 gripper mount: xArm6 link_eef, zero offset
- D435 camera mount: link_eef + xyz=(0,0,0.06) rpy=(0,-1.57,3.14) (real-robot calibration)
- rslidar mount: base_link + xyz=(0,0,0.138)

## Attribution

See `meshes/ATTRIBUTION` and top-level `NOTICE.md`. Geometry, meshes, and
joint origins are adapted from upstream `scout_ros`, `xarm_ros`, and
`dh_robotics_ag95_model`.
