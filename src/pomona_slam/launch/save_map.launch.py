#!/usr/bin/env python3
# Copyright 2026 Pravin Oli  <pravin.oli.08@gmail.com, olipravin18@gmail.com>
# Licensed under the Apache License, Version 2.0.
#
# Save the current SLAM Toolbox map to disk.
# Equivalent to:
#   ros2 run nav2_map_server map_saver_cli -f <name>

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    declare_name = DeclareLaunchArgument(
        "map_name", default_value="pomona_map",
        description="Output map basename (creates <name>.pgm + <name>.yaml)",
    )

    saver = ExecuteProcess(
        cmd=[
            "ros2", "run", "nav2_map_server", "map_saver_cli",
            "-f", LaunchConfiguration("map_name"),
        ],
        output="screen",
    )

    return LaunchDescription([declare_name, saver])
