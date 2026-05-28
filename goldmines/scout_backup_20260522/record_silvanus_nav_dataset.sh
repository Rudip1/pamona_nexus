#!/usr/bin/env bash

###############################################
#   SILVANUS NAVIGATION + SLIP DATASET RECORDER
###############################################

# Bag prefix + output directory (can be overridden from CLI)
BAG_PREFIX=${1:-silvanus_nav_run}
OUTPUT_DIR=${2:-$HOME/rosbags}

# Frequencies (Hz)
IMU_HZ=200.0
GNSS_HZ=10.0
ODOM_HZ=50.0
LIDAR_HZ=10.0
RGB_HZ=10.0
DEPTH_HZ=10.0
CAMINFO_HZ=10.0

###############################################
#  Create output folder
###############################################
mkdir -p "$OUTPUT_DIR"

echo "---------------------------------------------"
echo " SILVANUS Navigation + Slip Dataset Recorder"
echo " Bag prefix : $BAG_PREFIX"
echo " Output dir : $OUTPUT_DIR"
echo "---------------------------------------------"
echo " Press CTRL+C to stop recording."
echo "---------------------------------------------"

###############################################
#  Start throttlers (background)
###############################################

# IMU
rosrun topic_tools throttle messages /imu/data $IMU_HZ &
PID_IMU=$!

# GNSS
rosrun topic_tools throttle messages /gnss $GNSS_HZ &
PID_GNSS=$!

# Odom
rosrun topic_tools throttle messages /odom $ODOM_HZ &
PID_ODOM=$!

# LiDAR
rosrun topic_tools throttle messages /rslidar_points $LIDAR_HZ &
PID_LIDAR=$!

# RGB
rosrun topic_tools throttle messages /camera/color/image_raw $RGB_HZ &
PID_RGB_IMG=$!

rosrun topic_tools throttle messages /camera/color/camera_info $CAMINFO_HZ &
PID_RGB_INFO=$!

# Depth
rosrun topic_tools throttle messages /camera/depth/image_rect_raw $DEPTH_HZ &
PID_DEPTH_IMG=$!

rosrun topic_tools throttle messages /camera/depth/camera_info $CAMINFO_HZ &
PID_DEPTH_INFO=$!

###############################################
#  rosbag record (foreground)
###############################################
rosbag record -o "$OUTPUT_DIR/$BAG_PREFIX" \
    /tf \
    /tf_static \
    /cmd_vel \
    /imu/data_throttle \
    /gnss_throttle \
    /odom_throttle \
    /filter/quaternion \
    /filter/positionlla \
    /filter/twist \
    /scout_status \
    /BMS_status \
    /diagnostics \
    /rslidar_points_throttle \
    /camera/color/image_raw_throttle \
    /camera/color/camera_info_throttle \
    /camera/depth/image_rect_raw_throttle \
    /camera/depth/camera_info_throttle \
    /camera/depth_registered/points


###############################################
#  Cleanup on exit
###############################################
echo "Stopping throttlers..."
kill $PID_IMU $PID_GNSS $PID_ODOM \
     $PID_LIDAR $PID_RGB_IMG $PID_RGB_INFO \
     $PID_DEPTH_IMG $PID_DEPTH_INFO \
     2>/dev/null

wait 2>/dev/null

echo "Done. Dataset saved to $OUTPUT_DIR"

