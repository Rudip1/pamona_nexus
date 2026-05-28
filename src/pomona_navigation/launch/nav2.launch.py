#!/usr/bin/env python3
# Copyright 2026 Pravin Oli  <pravin.oli.08@gmail.com, olipravin18@gmail.com>
# Licensed under the Apache License, Version 2.0.
#
# Pomona Nav2 stack — planner, controller, behavior, smoother, BT servers.
# Wraps nav2_bringup/launch/navigation_launch.py with Pomona's params.

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg_share = get_package_share_directory("pomona_navigation")
    nav2_bringup = get_package_share_directory("nav2_bringup")

    declare_use_sim_time = DeclareLaunchArgument(
        "use_sim_time", default_value="false",
        description="True for sim, false for real robot",
    )
    declare_params = DeclareLaunchArgument(
        "params_file",
        default_value=os.path.join(pkg_share, "config", "nav2_params.yaml"),
    )
    declare_autostart = DeclareLaunchArgument("autostart", default_value="true")

    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup, "launch", "navigation_launch.py")
        ),
        launch_arguments={
            "use_sim_time": LaunchConfiguration("use_sim_time"),
            "params_file":  LaunchConfiguration("params_file"),
            "autostart":    LaunchConfiguration("autostart"),
        }.items(),
    )

    return LaunchDescription(
        [declare_use_sim_time, declare_params, declare_autostart, nav2]
    )
