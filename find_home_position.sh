#!/bin/bash

# Find home position script for SO101Follower robot
# Usage: ./find_home_position.sh [options]

# Default values
PORT="${PORT:-/dev/ttyACM0}"
ROBOT_ID="${ROBOT_ID:-assembler0_so101_follower}"
UPDATE_RATE="${UPDATE_RATE:-0.5}"

# Show usage
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "Usage: ./find_home_position.sh [options]"
    echo ""
    echo "This script disables torque and lets you manually position the robot arm"
    echo "while displaying current joint positions. Use this to find good waypoint positions."
    echo ""
    echo "Environment variables:"
    echo "  PORT         - Serial port for the robot (default: /dev/ttyACM0)"
    echo "  ROBOT_ID     - Robot ID (default: assembler0_so101_follower)"
    echo "  UPDATE_RATE  - Position update rate in seconds (default: 0.5)"
    echo ""
    echo "Examples:"
    echo "  ./find_home_position.sh"
    echo "  PORT=/dev/ttyACM1 ./find_home_position.sh"
    exit 0
fi

# Run the script
python find_home_position.py \
    --port "$PORT" \
    --robot_id "$ROBOT_ID" \
    --update_rate "$UPDATE_RATE" \
    --output "waypoints.json" \
    "$@"

