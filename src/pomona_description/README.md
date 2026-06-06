# pomona_description

URDF / xacro / meshes for **Pomona** — shared by `pomona_gazebo` (sim) and
`pomona_bringup` (real robot). Launch-only package, no nodes.

## Robot composition

| Component        | Make / Model            | Xacro file              |
|------------------|-------------------------|-------------------------|
| Mobile base      | AgileX Scout V2         | `scout_v2.xacro`        |
| Wheels (4×)      | scout type1 / type2     | `scout_wheel_type{1,2}.xacro` |
| Mounting box     | white deck cuboid + display | `mount.xacro`       |
| Manipulator      | UFactory xArm6 (6-DOF)  | `xarm6.xacro`           |
| Gripper          | DH Robotics AG95        | `ag95_gripper.xacro`    |
| Sensors          | rslidar / Xsens / D435  | `sensors.xacro`         |
| Sim plugins      | gazebo_ros classic 11   | `gazebo_plugins.xacro`  |
| Sim control      | gazebo_ros2_control     | `ros2_control.xacro` (sim only) |
| Root             | combines all above      | `pomona.xacro`          |

`mount.xacro` adds the white box (`box_link`) that physically carries the arm,
LiDAR, and display — ported from the goldmines `scout_xarm_base` package.
`ros2_control.xacro` is included only under `use_sim:=true`; it declares the
`GazeboSystem` hardware and the gazebo_ros2_control plugin (controllers
themselves are configured in `pomona_gazebo/config/gazebo_ros2_control_sim.yaml`).
The real robot (`use_sim:=false`) carries neither plugin block — the physical
arm is driven by vendor `xarm_ros2`.

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
- Mounting box (`box_link`): base_link + xyz=(0,0,0.113)
- xArm6 mount on Scout base: xyz=(0.212, 0, 0.26) — from real robot
- AG95 gripper mount: xArm6 link_eef, zero offset
- D435 camera mount: link_eef + xyz=(0,0,0.06) rpy=(0,-1.57,3.14) (real-robot calibration)
- rslidar mount: box_link + xyz=(0.37655, 0, 0.003) (front of the box)

## Attribution

See `meshes/ATTRIBUTION` and top-level `NOTICE.md`. Geometry, meshes, and
joint origins are adapted from upstream `scout_ros`, `xarm_ros`,
`dh_robotics_ag95_model`, and the goldmines `scout_xarm_base` (mounting box).
