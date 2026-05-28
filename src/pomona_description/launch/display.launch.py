#!/usr/bin/env python3
# Copyright 2026 Pravin Oli  <pravin.oli.08@gmail.com, olipravin18@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Project: Pomona Nexus
#
# Standalone URDF viewer — no Gazebo, no real robot.
# Loads pomona.xacro (use_sim:=false) through robot_state_publisher,
# starts joint_state_publisher_gui for interactive slider control,
# and opens RViz2 with the bundled model.rviz config.
#
# Run:  ros2 launch pomona_description display.launch.py
#       ros2 launch pomona_description display.launch.py use_gui:=false

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = get_package_share_directory("pomona_description")

    declare_use_gui = DeclareLaunchArgument(
        "use_gui",
        default_value="true",
        description="Launch joint_state_publisher_gui (sliders) instead of headless",
    )
    declare_use_rviz = DeclareLaunchArgument(
        "use_rviz",
        default_value="true",
        description="Launch RViz2",
    )
    declare_rviz_config = DeclareLaunchArgument(
        "rviz_config",
        default_value=os.path.join(pkg_share, "rviz", "model.rviz"),
        description="Path to RViz config file",
    )

    xacro_path = PathJoinSubstitution(
        [FindPackageShare("pomona_description"), "urdf", "xacro", "pomona.xacro"]
    )

    # Wrap in ParameterValue(value_type=str) — Humble parses YAML by default and
    # will crash on URDF XML otherwise.
    robot_description = ParameterValue(
        Command([FindExecutable(name="xacro"), " ", xacro_path, " use_sim:=false"]),
        value_type=str,
    )

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[{"robot_description": robot_description, "use_sim_time": False}],
    )

    jsp_gui_node = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        name="joint_state_publisher_gui",
        output="screen",
        condition=IfCondition(LaunchConfiguration("use_gui")),
    )

    jsp_node = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        name="joint_state_publisher",
        output="screen",
        condition=UnlessCondition(LaunchConfiguration("use_gui")),
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", LaunchConfiguration("rviz_config")],
        condition=IfCondition(LaunchConfiguration("use_rviz")),
    )

    return LaunchDescription(
        [
            declare_use_gui,
            declare_use_rviz,
            declare_rviz_config,
            robot_state_publisher_node,
            jsp_gui_node,
            jsp_node,
            rviz_node,
        ]
    )
