#!/usr/bin/env python3
# Copyright 2026 Pravin Oli  <pravin.oli.08@gmail.com, olipravin18@gmail.com>
# Licensed under the Apache License, Version 2.0.
#
# Empty world, SDF pipeline.
# Spawns Pomona from models/pomona/model.sdf (pre-baked) instead of from
# /robot_description. RSP still runs so TF tree is published — Gazebo SDF
# only carries the diff_drive plugin and link geometry.
#
# Run:  ros2 launch pomona_gazebo empty_world_sdf.launch.py
#
# NOTE: models/pomona/model.sdf is a placeholder until you generate it from
# the xacro source. See pomona_description/scripts/xacro_to_urdf.sh and
# `gz sdf -p` for conversion.

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
    declare_x_pose = DeclareLaunchArgument("x_pose", default_value="0.0")
    declare_y_pose = DeclareLaunchArgument("y_pose", default_value="0.0")
    declare_theta  = DeclareLaunchArgument("theta",  default_value="0.0")
    declare_use_teleop = DeclareLaunchArgument(
        "use_teleop", default_value="true",
        description="Start rqt_robot_steering",
    )

    use_sim_time = LaunchConfiguration("use_sim_time")
    x_pose       = LaunchConfiguration("x_pose")
    y_pose       = LaunchConfiguration("y_pose")
    theta        = LaunchConfiguration("theta")

    world_file = os.path.join(pkg_pomona_gazebo, "worlds", "empty_world.world")

    gazebo_resource_path = SetEnvironmentVariable(
        name="GAZEBO_RESOURCE_PATH",
        value=os.pathsep.join(
            [
                os.path.dirname(pkg_pomona_desc),
                "/usr/share/gazebo-11",
                "/opt/ros/humble/share",
            ]
        ),
    )
    gazebo_model_path = SetEnvironmentVariable(
        name="GAZEBO_MODEL_PATH",
        value=os.pathsep.join(
            [
                os.path.join(pkg_pomona_gazebo, "models"),
                os.path.dirname(pkg_pomona_desc),
                "/usr/share/gazebo-11/models",
            ]
        ),
    )
    gazebo_plugin_path = SetEnvironmentVariable(
        name="GAZEBO_PLUGIN_PATH",
        value=os.pathsep.join(
            [
                "/opt/ros/humble/lib",
                "/usr/lib/x86_64-linux-gnu/gazebo-11/plugins",
            ]
        ),
    )

    gzserver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, "launch", "gzserver.launch.py")
        ),
        launch_arguments={"world": world_file}.items(),
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
            os.path.join(launch_dir, "pomona_state_publisher.launch.py")
        ),
        launch_arguments={"use_sim_time": use_sim_time}.items(),
    )

    spawn = TimerAction(
        period=5.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(launch_dir, "spawn_sdf.launch.py")
                ),
                launch_arguments={
                    "x_pose": x_pose,
                    "y_pose": y_pose,
                    "theta":  theta,
                }.items(),
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
