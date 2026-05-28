#!/bin/bash
echo "Waiting 15 seconds for bringup to fully start..."
sleep 15
source /home/agilex/agilex_ws/devel/setup.bash
roslaunch recycle nav_explore.launch
