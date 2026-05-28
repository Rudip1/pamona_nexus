#!/usr/bin/env python3
# Copyright 2026 Pravin Oli  <pravin.oli.08@gmail.com, olipravin18@gmail.com>
# Licensed under the Apache License, Version 2.0.
#
# Bundle: Pomona SLAM + Nav2 in one launch.
# Useful for "go to ros2 launch pomona_navigation nav2_bringup.launch.py"
# during exploration / mapping runs.

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg_nav = get_package_share_directory("pomona_navigation")
    pkg_slam = get_package_share_directory("pomona_slam")

    declare_use_sim_time = DeclareLaunchArgument("use_sim_time", default_value="false")

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_slam, "launch", "slam.launch.py")),
        launch_arguments={"use_sim_time": LaunchConfiguration("use_sim_time")}.items(),
    )
    nav = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_nav, "launch", "nav2.launch.py")),
        launch_arguments={"use_sim_time": LaunchConfiguration("use_sim_time")}.items(),
    )

    return LaunchDescription([declare_use_sim_time, slam, nav])
