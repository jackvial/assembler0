#!/bin/bash

# Screwdriver Robot Teleoperation
python -m assembler0_robot.scripts.teleoperate \
    --robot_port=/dev/servo_5837053138 \
    --robot_id=koch_screwdriver_follower_20250814 \
    --leader_port=/dev/servo_585A007782 \
    --leader_id=koch_screwdriver_leader_20250814 \
    --screwdriver_camera=/dev/video0 \
    --side_camera=/dev/video2 \
    --camera_width=800 \
    --camera_height=600 \
    --camera_fps=30 \
    --fps=30 \
    --screwdriver_current_limit=300 \
    --clutch_ratio=0.5 \
    --clutch_cooldown_s=1.0 \
    --gripper_open_pos=50.0 \
    --haptic_range=4.0
