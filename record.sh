#!/bin/bash

RUN_ID=$1
NUM_EPISODES=$2

if [ -z "$RUN_ID" ] || [ -z "$NUM_EPISODES" ]; then
    echo "Usage: $0 <runid> <num_episodes>"
    exit 1
fi

# Screwdriver Robot Recording
python -m assembler0_robot.scripts.record \
    --robot_port=/dev/servo_5837053138 \
    --robot_id=koch_screwdriver_follower_20250814 \
    --leader_port=/dev/servo_585A007782 \
    --leader_id=koch_screwdriver_leader_20250814 \
    --screwdriver_camera=/dev/video0 \
    --side_camera=/dev/video2 \
    --top_camera=/dev/video6 \
    --camera_width=800 \
    --camera_height=600 \
    --camera_fps=30 \
    --fps=30 \
    --screwdriver_current_limit=300 \
    --clutch_ratio=0.5 \
    --clutch_cooldown_s=1.0 \
    --gripper_open_pos=50.0 \
    --haptic_range=4.0 \
    --dataset_repo_id=jackvial/screwdriver_panel_ls_${RUN_ID}_e${EPISODES} \
    --num_episodes=${NUM_EPISODES} \
    --episode_time_s=15 \
    --reset_time_s=7 \
    --encode_videos_after=true \
    --push_to_hub=true \
    --single_task="Move towards the silver screw in the orange panel. Then place the screwdriver bit on the screw, and turn the screwdriver bit clockwise until the screw is has been fully screwed in." \
    --display_data=false \
    --play_sounds=false \
    --log_level=INFO \
    --batch_encoding_size=${NUM_EPISODES}