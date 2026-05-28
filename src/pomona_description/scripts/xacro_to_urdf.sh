#!/usr/bin/env bash
# Copyright 2026 Pravin Oli  <pravin.oli.08@gmail.com, olipravin18@gmail.com>
# Licensed under the Apache License, Version 2.0.
#
# Regenerate flat URDFs from the xacro single source of truth.
# Useful for the SDF pipeline (pomona_gazebo/models/pomona/model.sdf) and for
# offline inspection (urdf/urdf/pomona.urdf is gitignore-safe).
#
# Usage:  bash scripts/xacro_to_urdf.sh
#         (run from this package source dir, or anywhere if ROS env is sourced)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
XACRO_ROOT="$PKG_DIR/urdf/xacro/pomona.xacro"
OUT_DIR="$PKG_DIR/urdf/urdf"
mkdir -p "$OUT_DIR"

# Pomona "real-robot" URDF (no Gazebo plugins)
echo "[xacro] pomona.urdf  (use_sim:=false)"
xacro "$XACRO_ROOT" use_sim:=false  > "$OUT_DIR/pomona.urdf"

# Pomona simulation URDF (with Gazebo plugins)
echo "[xacro] pomona_sim.urdf  (use_sim:=true)"
xacro "$XACRO_ROOT" use_sim:=true   > "$OUT_DIR/pomona_sim.urdf"

echo "Generated:"
ls -la "$OUT_DIR"
