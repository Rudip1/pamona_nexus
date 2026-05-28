#!/bin/bash
# Monitor navigation status in the background

while true; do
    clear
    echo "=========================================="
    echo "Navigation Monitor - $(date '+%H:%M:%S')"
    echo "=========================================="
    echo ""
    
    # Check test state
    echo "Test State:"
    rostopic echo /aruco_test/state -n 1 --noarr 2>&1 | grep data || echo "  Not available"
    echo ""
    
    # Check ArUco marker position
    echo "ArUco Marker Position:"
    rostopic echo /aruco_marker_pose -n 1 --noarr 2>&1 | grep -E "(frame_id|position)" | head -4 || echo "  Not available"
    echo ""
    
    # Check move_base status
    echo "Move Base Status:"
    rostopic echo /move_base/status -n 1 --noarr 2>&1 | grep -E "status:" | head -1 || echo "  Not available"
    echo ""
    
    # Check if nodes are running
    echo "Running Nodes:"
    rosnode list | grep -E "(aruco|navigation|move_base|gmapping)" | sed 's/^/  /'
    echo ""
    
    echo "Press Ctrl+C to stop monitoring"
    sleep 2
done


