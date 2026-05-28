# pomona_navigation

Nav2 configuration for **Pomona**. Wraps `nav2_bringup/navigation_launch.py`
with Pomona-specific params + behavior trees.

## Run

```bash
# Nav2 stack against sim (start pomona_gazebo + pomona_slam first)
ros2 launch pomona_navigation nav2.launch.py use_sim_time:=true

# Nav2 stack against real (start pomona_bringup + pomona_slam first)
ros2 launch pomona_navigation nav2.launch.py use_sim_time:=false

# Bundle SLAM + Nav2 in one launch
ros2 launch pomona_navigation nav2_bringup.launch.py use_sim_time:=true
```

## Tuning notes (Scout V2)

- `robot_radius: 0.55` — Scout V2 longest diagonal ≈ 1.0 m, half = 0.5; +0.05 inflation margin.
- `controller_server.FollowPath.max_vel_x: 0.7` — Scout V2 rated 1.5 m/s but throttled for indoor / greenhouse.
- `inflation_layer.inflation_radius: 0.55` — matches `robot_radius`.

Tune against the actual environment width / arm reach as you build out the
4 greenhouse worlds.

## Topics

| Topic | Direction | Description |
|---|---|---|
| `/cmd_vel` | Nav2 → diff_drive | velocity command for Scout base |
| `/scan` | sensors → Nav2 | input from rslidar (real) or ray_sensor (sim) |
| `/map` | SLAM → Nav2 | global static layer |
| `/odom` | base → Nav2 | velocity feedback |
| `/plan` | Nav2 → RViz | computed global path |
| `/local_costmap/costmap` | Nav2 → RViz | local costmap |
