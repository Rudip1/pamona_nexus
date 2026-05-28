#!/usr/bin/env python3
# Copyright 2026 Pravin Oli  <pravin.oli.08@gmail.com, olipravin18@gmail.com>
# Licensed under the Apache License, Version 2.0.
#
# Waypoint follower for Nav2 — STUB.
# TODO  Add nav2_waypoint_follower Node + waypoint plugin config when needed.

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument


def generate_launch_description():
    return LaunchDescription([DeclareLaunchArgument("use_sim_time", default_value="false")])
