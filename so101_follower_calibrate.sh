#!/bin/bash

# Calibrate SO101 Follower (non-screwdriver version) robot
echo "Calibrating SO101 Follower robot..."
python -m assembler0_robot.scripts.calibrate \
    --device_type=robot \
    --robot_variant=so101_follower \
    --port=/dev/ttyACM0 \
    --device_id=assembler0_so101_follower

# Note: You can customize the port and device_id as needed:
# --port=/dev/ttyUSB0  (or whichever port your robot is connected to)
# --device_id=your_custom_id

