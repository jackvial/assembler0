#!/bin/bash

# Screwdriver Robot Teleoperation
python -m assembler0_robot.scripts.teleoperate \
    --robot_variant=so101 \
    --robot_port=/dev/ttyACM0 \
    --robot_id=assembler0_so101_follower \
    --leader_port=/dev/ttyACM1 \
    --leader_id=assembler0_so101_leader \
    --side_camera=/dev/video4 \
    --camera_width=800 \
    --camera_height=600 \
    --camera_fps=30 \
    --fps=30 \

