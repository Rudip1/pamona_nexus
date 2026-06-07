#!/usr/bin/env python3
# Copyright 2026 Pravin Oli  <pravin.oli.08@gmail.com, olipravin18@gmail.com>
# Licensed under the Apache License, Version 2.0.
#
# 10-row strawberry farm world (plastic-mulch beds + strawberry plants with
# ripe/unripe/flowering berries) with the pomona_uvc robot spawned in a furrow
# and driveable via rqt_robot_steering. The UV-C boom treats the adjacent beds
# as the base drives down the lane.
#
# The bed + plant + dirt models are reused in place from
#   goldmines/harvester-sim-master/harvester_gazebo/models   (jsather, BSD)
# via GAZEBO_MODEL_PATH, so nothing large is copied into the repo.
#
# Launch graph (mirrors empty_world_pomona_uvc_xacro.launch.py):
#   gzserver / gzclient        → Gazebo physics + GUI (farm world)
#   robot_state_publisher      → pomona_state_publisher_uvc (use_sim:=true)
#   spawn_entity               → reads /robot_description (delayed 5 s)
#   rqt_robot_steering         → /cmd_vel teleop
# (pomona_uvc has no arm → no ros2_control / controller spawners / go-home.)
#
# Spawn defaults drop the robot into the first drive furrow (between bed
# columns 0 and 1, centre x≈1.6 m) just ahead of the beds in the headland,
# facing +Y down the lane.
#
# Run:  ros2 launch pomona_gazebo strawberry_farm.launch.py

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    SetEnvironmentVariable,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_pomona_gazebo = get_package_share_directory("pomona_gazebo")
    pkg_gazebo_ros    = get_package_share_directory("gazebo_ros")
    pkg_pomona_desc   = get_package_share_directory("pomona_description")
    launch_dir        = os.path.join(pkg_pomona_gazebo, "launch")

    declare_use_sim_time = DeclareLaunchArgument(
        "use_sim_time", default_value="true", description="Use Gazebo clock"
    )
    # Furrow between bed columns 0 and 1 is centred at x≈1.6 m; start in the
    # headland (y=1.0) ahead of the beds, facing +Y down the lane.
    declare_x_pose = DeclareLaunchArgument("x_pose", default_value="1.6")
    declare_y_pose = DeclareLaunchArgument("y_pose", default_value="1.0")
    declare_theta  = DeclareLaunchArgument("theta",  default_value="1.5708")
    declare_use_teleop = DeclareLaunchArgument(
        "use_teleop", default_value="true",
        description="Start rqt_robot_steering for /cmd_vel",
    )

    use_sim_time = LaunchConfiguration("use_sim_time")
    x_pose       = LaunchConfiguration("x_pose")
    y_pose       = LaunchConfiguration("y_pose")
    theta        = LaunchConfiguration("theta")

    world_file = os.path.join(pkg_pomona_gazebo, "worlds", "strawberry_farm.world")

    # reused strawberry assets (bed / plant / dirt_plane) live in goldmines
    harvester_models = os.path.expanduser(
        "~/pomona_nexus/goldmines/harvester-sim-master/harvester_gazebo/models")

    gazebo_resource_path = SetEnvironmentVariable(
        name="GAZEBO_RESOURCE_PATH",
        value=os.pathsep.join(
            [os.path.dirname(pkg_pomona_desc), "/usr/share/gazebo-11",
             "/opt/ros/humble/share"]
        ),
    )
    gazebo_model_path = SetEnvironmentVariable(
        name="GAZEBO_MODEL_PATH",
        value=os.pathsep.join(
            [harvester_models,
             os.path.join(pkg_pomona_gazebo, "models"),
             os.path.dirname(pkg_pomona_desc), "/usr/share/gazebo-11/models"]
        ),
    )
    gazebo_plugin_path = SetEnvironmentVariable(
        name="GAZEBO_PLUGIN_PATH",
        value=os.pathsep.join(
            ["/opt/ros/humble/lib", "/usr/lib/x86_64-linux-gnu/gazebo-11/plugins"]
        ),
    )

    gzserver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, "launch", "gzserver.launch.py")
        ),
        launch_arguments={"world": world_file, "verbose": "true"}.items(),
    )
    gzclient = TimerAction(
        period=3.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg_gazebo_ros, "launch", "gzclient.launch.py")
                )
            )
        ],
    )

    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(launch_dir, "pomona_state_publisher_uvc.launch.py")
        ),
        launch_arguments={"use_sim_time": use_sim_time}.items(),
    )

    spawn = TimerAction(
        period=5.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(launch_dir, "spawn_xacro.launch.py")
                ),
                launch_arguments={"x_pose": x_pose, "y_pose": y_pose,
                                  "theta": theta,
                                  # spawn above ground so the robot drops onto
                                  # its wheels (URDF spawn doesn't resolve an
                                  # initial ground penetration cleanly).
                                  "z_pose": "0.30"}.items(),
            )
        ],
    )

    teleop = Node(
        package="rqt_robot_steering",
        executable="rqt_robot_steering",
        name="rqt_robot_steering",
        output="screen",
        parameters=[{"use_sim_time": use_sim_time}],
        condition=IfCondition(LaunchConfiguration("use_teleop")),
    )

    return LaunchDescription(
        [
            declare_use_sim_time,
            declare_x_pose,
            declare_y_pose,
            declare_theta,
            declare_use_teleop,
            gazebo_resource_path,
            gazebo_model_path,
            gazebo_plugin_path,
            gzserver,
            gzclient,
            rsp,
            spawn,
            teleop,
        ]
    )
