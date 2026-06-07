#!/usr/bin/env bash
# One-shot: regenerate pomona URDFs from xacro -> gz sdf -> re-inject blue lamp
# material into pomona_uvc/model.sdf -> colcon build.  Run after editing the
# pomona_uvc cantilever (or any) xacro.
#   bash cad_assets_studio/uvc_cantilever/tools/rebuild_uvc.sh
set -e
WS=~/pomona_nexus
source /opt/ros/humble/setup.bash 2>/dev/null || true
source "$WS/install/setup.bash" 2>/dev/null || true

cd "$WS/src/pomona_description"
echo "[1/4] xacro -> urdf"
bash scripts/xacro_to_urdf.sh >/tmp/uvc_rebuild.log 2>&1 || { echo "XACRO FAILED:"; tail -8 /tmp/uvc_rebuild.log; exit 1; }
U=urdf/pomona_uvc/urdf/pomona_uvc_sim.urdf
check_urdf "$U" >/dev/null 2>&1 && echo "      check_urdf OK" || { echo "check_urdf FAILED"; exit 1; }

echo "[2/4] urdf -> model.sdf (gz sdf)"
gz sdf -p "$U" > ../pomona_gazebo/models/pomona_uvc/model.sdf 2>/dev/null

echo "[3/4] re-inject blue lamp material (gz sdf drops gazebo refs)"
python3 - <<'PY'
import re
p="../pomona_gazebo/models/pomona_uvc/model.sdf"; s=open(p).read()
mat="<material><ambient>0 0 0.8 1</ambient><diffuse>0.1 0.2 1 1</diffuse><emissive>0 0 0.3 1</emissive></material>"
s=re.sub(r"<visual name='[^']*uvc_lamp[^']*'>.*?</visual>",
  lambda m: m.group(0).replace('</visual>',mat+'</visual>') if ('uvc_lamp' in m.group(0) and '<material>' not in m.group(0)) else m.group(0),
  s, flags=re.S)
open(p,"w").write(s); print("      blue lamp visuals:", s.count(mat))
PY

echo "[4/4] colcon build"
cd "$WS" && colcon build --packages-select pomona_description pomona_gazebo --symlink-install 2>&1 | tail -1
echo "DONE — relaunch:  ros2 launch pomona_gazebo strawberry_farm.launch.py"
