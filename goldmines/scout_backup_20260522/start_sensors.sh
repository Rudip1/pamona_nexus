#!/usr/bin/env bash
set -e

###############################################
#  ROS ENVIRONMENT
###############################################
source /opt/ros/melodic/setup.bash
source /home/agilex/agilex_ws/devel/setup.bash

###############################################
#  ALL topics required for recording
###############################################
REQUIRED_TOPICS=(
  /tf
  /tf_static
  /cmd_vel

  /imu/data
  /gnss
  /odom

  /filter/quaternion
  /filter/positionlla
  /filter/twist

  /scout_status
  /BMS_status
  /diagnostics

  /rslidar_points

  /camera/color/image_raw
  /camera/color/camera_info
  /camera/depth/image_rect_raw
  /camera/depth/camera_info
)

###############################################
#  Verify ALL required ROS topics
###############################################
verify_topics() {
  echo "---------------------------------------------"
  echo " Verifying ALL ROS topics before recording"
  echo "---------------------------------------------"

  local timeout=60
  local interval=1
  local elapsed=0

  while [ $elapsed -lt $timeout ]; do
    missing=()

    for topic in "${REQUIRED_TOPICS[@]}"; do
      if ! rostopic list 2>/dev/null | grep -qx "$topic"; then
        missing+=("$topic")
      fi
    done

    if [ ${#missing[@]} -eq 0 ]; then
      echo "All required topics are available ✅"
      return 0
    fi

    sleep $interval
    elapsed=$((elapsed + interval))
  done

  echo "❌ ERROR: Missing required topics:"
  for t in "${missing[@]}"; do
    echo "   - $t"
  done
  echo "Aborting to protect dataset integrity."
  return 1
}

###############################################
#  Launch robot bringup
###############################################
echo "Starting robot bringup..."
roslaunch recycle bringup_minimal_1.launch &
PID_BRINGUP=$!

sleep 5

###############################################
#  Launch XSENS
###############################################
echo "Starting XSENS driver..."
roslaunch xsens_mti_driver xsens_mti_node.launch &
PID_XSENS=$!

###############################################
#  Wait for ROS master + nodes
###############################################
echo "Waiting for ROS nodes to initialize..."
sleep 10

###############################################
#  Verify topics
###############################################
verify_topics || {
  echo "Shutting down launched nodes..."
  kill $PID_BRINGUP $PID_XSENS 2>/dev/null
  exit 1
}

###############################################
#  Everything OK
###############################################
echo "---------------------------------------------"
echo " SYSTEM READY – all topics available"
echo " You can now start rosbag recording"
echo "---------------------------------------------"

wait

