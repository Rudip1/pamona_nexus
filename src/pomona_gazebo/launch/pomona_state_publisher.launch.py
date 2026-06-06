#!/usr/bin/env python3
# Copyright 2026 Pravin Oli  <pravin.oli.08@gmail.com, olipravin18@gmail.com>
# Licensed under the Apache License, Version 2.0.
#
# Robot state publisher for the Gazebo pipeline.
# Processes pomona.xacro with use_sim:=true (Gazebo plugins included)
# and publishes /robot_description + the TF tree under base_link.
#
# NOTE: XML comments are stripped from the generated URDF before it is
# published. gazebo_ros2_control (Humble, 0.4.x) re-passes robot_description
# to the controller_manager as a `--param` CLI override; rcl's argument
# parser rejects the non-ASCII box-drawing characters used in our xacro
# comment headers ("Couldn't parse parameter override rule"). Stripping
# comments keeps the source style intact while making the runtime URDF safe.

import re
import subprocess

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

import os


def _launch_setup(context, *args, **kwargs):
    xacro_path = os.path.join(
        get_package_share_directory("pomona_description"),
        "urdf", "xacro", "pomona.xacro",
    )
    use_sim_time = LaunchConfiguration("use_sim_time").perform(context)

    # Run xacro, then drop XML comments (see header note).
    urdf = subprocess.check_output(
        ["xacro", xacro_path, "use_sim:=true"], text=True
    )
    urdf = re.sub(r"<!--.*?-->", "", urdf, flags=re.DOTALL)

    return [
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[
                {
                    "robot_description": urdf,
                    "use_sim_time": use_sim_time == "true",
                }
            ],
        )
    ]


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_sim_time", default_value="true", description="Use Gazebo clock"
            ),
            OpaqueFunction(function=_launch_setup),
        ]
    )
