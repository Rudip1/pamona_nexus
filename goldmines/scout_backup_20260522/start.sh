#!/bin/bash

#setup can usb
echo "Running scout_base"
roslaunch scout_base scout_base.launch

rosrun scout_bringup bringup_can2usb.bash

echo "Running lidar"
roslaunch agilexpro open_lidar.launch

#Define static transform between base_link and rslidar
rosrun tf static_transform_publisher 0 0 0.138 0 0 0 base_link rslidar 100
echo "static link created"

rosrun rviz rviz




