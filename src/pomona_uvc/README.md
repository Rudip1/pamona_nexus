<div align="center">

# 💡 pomona_uvc

### UV-C lamp on/off control + disinfection **dose map** for the **Pomona** UV-C boom

[![ROS 2](https://img.shields.io/badge/ROS%202-Humble-22314E?logo=ros&logoColor=white)](https://docs.ros.org/en/humble/)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](../../LICENSE)

</div>

---

## What this package does

The `pomona_uvc` robot model carries a UV-C boom with **12 lamp tubes** (left and
right panels, 6 each). In Gazebo each tube renders a blue **ray fan** at the bed
(`gpu_ray` sensors in `pomona_description`). This package adds the **control + dose**
layer on top:

- **ROS services** to switch lamps on/off — all, per-side, or per-lamp.
- A **disinfection dose map** that accumulates UV-C dose under the *lit* lamps as the
  robot moves, published as a `nav_msgs/OccupancyGrid` on `/uvc/dose` — the "blobs"
  you see in RViz.

It's the integration point for a future vision → treatment pipeline: detect a
defective plant, call `/uvc/lamp/<name>`, watch the dose accumulate.

---

## Run

```bash
# alongside the pomona_uvc sim (e.g. empty_world_pomona_uvc_xacro / strawberry_farm)
ros2 launch pomona_uvc uvc_control.launch.py rviz:=true
```

Lamps default **OFF** — nothing is dosed until a service turns them on:

```bash
ros2 service call /uvc/all          std_srvs/srv/SetBool "{data: true}"   # all 12
ros2 service call /uvc/left          std_srvs/srv/SetBool "{data: false}"  # left panel off
ros2 service call /uvc/right         std_srvs/srv/SetBool "{data: true}"   # right panel on
ros2 service call /uvc/lamp/left_3   std_srvs/srv/SetBool "{data: true}"   # one lamp
```

Drive the robot (teleop / Nav2 / the bed mission) and the dose blobs grow under the
active lamps in RViz (`Map` display on `/uvc/dose`, costmap colour scheme).

---

## Interfaces

| Service (`std_srvs/SetBool`) | Effect |
|---|---|
| `/uvc/all` | all 12 lamps |
| `/uvc/left`, `/uvc/right` | one panel (6 lamps) |
| `/uvc/lamp/<name>` | one lamp — `<name>` ∈ `left_0..5`, `right_0..5` |

| Topic | Type | Notes |
|---|---|---|
| `/uvc/dose` | `nav_msgs/OccupancyGrid` | disinfection dose "blobs" for RViz (frame `odom`) |
| `/uvc/lamp_states` | `std_msgs/Int8MultiArray` | 12 lamp states (left_0..5, right_0..5); for downstream use |

Dose model (in `scripts/uvc_controller.py`, adapted from `vf_robot_disinfection`):
per lit lamp, dose deposits in its ground footprint with distance falloff
`f = 0.577·d² − 3.21·d + 4.843`, normalised to `sufficient_dose`. Tune via node
params: `dose_resolution`, `dose_size_m`, `max_radiation_distance`, `sufficient_dose`,
`dose_rate_scale`, `dose_frame` / `base_frame`.

---

## Note — the Gazebo blue rays are always on

Gazebo Classic keeps a *visualised* laser sensor alive through the gzclient visual
subscription, so the blue ray fans **cannot be switched off** from the server
(`SetActive` has no effect). The blue rays mark *where* the UV-C aims; the toggleable
disinfection signal is the `/uvc/dose` map driven by these services.

---

<div align="center">
<sub>

Part of **[Pomona Nexus](../../README.md)** · boom geometry in
**[pomona_description](../pomona_description/README.md)** · used by the mission in
**[pomona_navigation](../pomona_navigation/README.md)** · Author **Pravin Oli** · **Apache-2.0**

</sub>
</div>
