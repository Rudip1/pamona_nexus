#!/usr/bin/env python3
# Copyright 2026 Pravin Oli  <pravin.oli.08@gmail.com, olipravin18@gmail.com>
# Licensed under the Apache License, Version 2.0.
#
# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Empty world, xacro pipeline  (★ main day-1 launch)                 ║
# ╚══════════════════════════════════════════════════════════════════════╝
#
# Launch graph:
#   gzserver                  → Gazebo physics
#   gzclient                  → Gazebo GUI (delayed 3 s — avoid race)
#   robot_state_publisher     → processes pomona.xacro (use_sim:=true)
#   spawn_entity              → reads /robot_description (delayed 5 s)
#   rqt_robot_steering        → teleop GUI publishing /cmd_vel
#
# Run:  ros2 launch pomona_gazebo empty_world_xacro.launch.py
#       ros2 run rqt_robot_steering rqt_robot_steering   # if not auto-started

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
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

    # ── arguments ─────────────────────────────────────────────────────────
    declare_use_sim_time = DeclareLaunchArgument(
        "use_sim_time", default_value="true", description="Use Gazebo clock"
    )
    declare_x_pose = DeclareLaunchArgument("x_pose", default_value="0.0")
    declare_y_pose = DeclareLaunchArgument("y_pose", default_value="0.0")
    declare_theta  = DeclareLaunchArgument("theta",  default_value="0.0")
    declare_use_teleop = DeclareLaunchArgument(
        "use_teleop", default_value="true",
        description="Start rqt_robot_steering for /cmd_vel",
    )

    use_sim_time = LaunchConfiguration("use_sim_time")
    x_pose       = LaunchConfiguration("x_pose")
    y_pose       = LaunchConfiguration("y_pose")
    theta        = LaunchConfiguration("theta")

    world_file = os.path.join(pkg_pomona_gazebo, "worlds", "empty_world.world")

    # ── Gazebo env vars (prepend, never replace) ──────────────────────────
    gazebo_resource_path = SetEnvironmentVariable(
        name="GAZEBO_RESOURCE_PATH",
        value=os.pathsep.join(
            [
                os.path.dirname(pkg_pomona_desc),   # share/ parent — for package://
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

    # ── Gazebo server ─────────────────────────────────────────────────────
    gzserver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, "launch", "gzserver.launch.py")
        ),
        launch_arguments={"world": world_file}.items(),
    )

    # ── Gazebo client — delayed 3 s ───────────────────────────────────────
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

    # ── Robot state publisher (xacro → /robot_description) ───────────────
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(launch_dir, "pomona_state_publisher.launch.py")
        ),
        launch_arguments={"use_sim_time": use_sim_time}.items(),
    )

    # ── Spawn robot — delayed 5 s ─────────────────────────────────────────
    spawn = TimerAction(
        period=5.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(launch_dir, "spawn_xacro.launch.py")
                ),
                launch_arguments={
                    "x_pose": x_pose,
                    "y_pose": y_pose,
                    "theta":  theta,
                }.items(),
            )
        ],
    )

    # ── ros2_control controller spawners ─────────────────────────────────
    # The controller_manager runs INSIDE Gazebo (libgazebo_ros2_control.so),
    # so it only exists after the robot spawns. The spawners wait for it via
    # --controller-manager-timeout, hence the start delay just past spawn (5 s).
    def _spawner(name):
        return Node(
            package="controller_manager",
            executable="spawner",
            arguments=[name, "--controller-manager", "/controller_manager",
                       "--controller-manager-timeout", "60"],
            output="screen",
        )

    controller_spawners = TimerAction(
        period=8.0,
        actions=[
            _spawner("joint_state_broadcaster"),
            _spawner("xarm6_traj_controller"),
            _spawner("ag95_gripper_controller"),
        ],
    )

    # Once the trajectory controller is active, drive the arm to the home pose.
    # The controller otherwise just holds whatever (slightly drooped) pose it
    # finds at activation; this actively raises it to the intended fold. Home
    # values mirror the initial_value seeds in ros2_control.xacro.
    home_pose = ExecuteProcess(
        cmd=[
            "ros2", "topic", "pub", "--once",
            "/xarm6_traj_controller/joint_trajectory",
            "trajectory_msgs/msg/JointTrajectory",
            "{joint_names: [joint1, joint2, joint3, joint4, joint5, joint6], "
            "points: [{positions: [0.0, -0.5, -0.6, 0.0, 1.1, 0.0], "
            "time_from_start: {sec: 2}}]}",
        ],
        output="screen",
    )
    go_home = TimerAction(period=14.0, actions=[home_pose])

    # ── Teleop GUI ────────────────────────────────────────────────────────
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
            controller_spawners,
            go_home,
            teleop,
        ]
    )
