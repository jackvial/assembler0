#!/bin/bash

# echo "Calibrating screwdriver follower robot..."
python -m assembler0_robot.scripts.calibrate \
    --device_type=robot \
    --port=/dev/servo_5837053138 \
    --device_id=koch_screwdriver_follower_20250814 \
    --screwdriver_current_limit=300 \
    --clutch_ratio=0.5 \
    --clutch_cooldown_s=1.0

# Calibrate the screwdriver leader teleoperator
# echo "Calibrating screwdriver leader teleoperator..."
python -m assembler0_robot.scripts.calibrate \
    --device_type=leader \
    --port=/dev/servo_585A007782 \
    --device_id=koch_screwdriver_leader_20250814 \
    --gripper_open_pos=50.0 \
    --haptic_range=4.0


######### Regular Koch Follower Robot #########
# echo "Calibrating Koch follower robot..."
# python -m assembler0.scripts.calibrate \
#     --device_type=robot \
#     --robot_variant=koch \
#     --port=/dev/ttyACM2 \
#     --device_id=koch_magnetic_follower_testing

# # Regular Koch Leader Teleoperator
# echo "Calibrating Koch leader teleoperator..."
# python -m assembler0.scripts.calibrate \
#     --device_type=leader \
#     --robot_variant=koch \
#     --port=/dev/ttyACM3 \
#     --device_id=koch_magnetic_leader_testing
