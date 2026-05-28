# pomona_slam

SLAM Toolbox configuration for **Pomona**. Online async mapping, pure
localization, and offline replay.

## Run

```bash
# Online mapping in Gazebo (start pomona_gazebo first)
ros2 launch pomona_slam slam.launch.py use_sim_time:=true use_rviz:=true

# Online mapping on real robot (start pomona_bringup first)
ros2 launch pomona_slam slam.launch.py use_sim_time:=false

# Save the current map
ros2 launch pomona_slam save_map.launch.py map_name:=greenhouse_1

# Pure localization on a saved map
ros2 launch pomona_slam localization.launch.py map:=$PWD/greenhouse_1 use_sim_time:=true
```

## Frames

SLAM Toolbox expects Pomona's default TF tree:

```
  map ─┬─→ odom ──→ base_footprint ──→ base_link ──→ rslidar
       │                                          ├──→ link_base (xArm6)
       │                                          ├──→ imu_link
       │                                          └──→ ...
       └─ (published by slam_toolbox as map→odom correction)
```

`scan_topic: /scan` — same topic whether sim (`gazebo_ros_ray_sensor`) or
real (`pointcloud_to_laserscan` after Robosense LiDAR).
