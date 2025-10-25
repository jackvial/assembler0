#!/bin/bash

# Demo script runner for SO101Follower robot
# Usage: ./demo_so101_follower.sh [options]

# Default values
PORT="${PORT:-/dev/ttyACM0}"
ROBOT_ID="${ROBOT_ID:-assembler0_so101_follower}"
FPS="${FPS:-30}"
WAIT_TIME="${WAIT_TIME:-2.0}"
SPEED_DEG_S="${SPEED_DEG_S:-20.0}"
ACCEL_DEG_S2="${ACCEL_DEG_S2:-50.0}"
BLEND_MS="${BLEND_MS:-200}"

# Show usage
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "Usage: ./demo_so101_follower.sh [options]"
    echo ""
    echo "Environment variables:"
    echo "  PORT        - Serial port for the robot (default: /dev/ttyACM0)"
    echo "  ROBOT_ID    - Robot ID (default: assembler0_so101_follower)"
    echo "  FPS         - Control loop frequency (default: 30)"
    echo "  WAIT_TIME   - Wait time at each waypoint in seconds (default: 2.0)"
    echo ""
    echo "Examples:"
    echo "  ./demo_so101_follower.sh"
    echo "  PORT=/dev/ttyACM1 ./demo_so101_follower.sh"
    echo "  python demo_so101_follower.py --port /dev/ttyACM0 --waypoints_file custom_waypoints.json"
    exit 0
fi

# Run the demo
python demo_so101_follower.py \
    --port "$PORT" \
    --robot_id "$ROBOT_ID" \
    --fps "$FPS" \
    --speed_deg_s "$SPEED_DEG_S" \
    --accel_deg_s2 "$ACCEL_DEG_S2" \
    --blend_ms "$BLEND_MS" \
    --wait_time "$WAIT_TIME" \
    --waypoints_file "waypoints.json" \
    "$@"

