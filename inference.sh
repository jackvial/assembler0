#!/bin/bash

# TODO - Push model to hub and use as example home/jack/code/lerobot/outputs/screwdriver_attach_orange_panel_cleaned_t90_v10_clean_5/checkpoints/060000/pretrained_model

# Screwdriver Robot Inference
python -m assembler0_robot.scripts.inference \
    --robot_port=/dev/servo_5837053138 \
    --robot_id=koch_screwdriver_follower_20250814 \
    --model_path=/home/jack/code/assembler0/wandb_downloads/panel_labels_clean_per_variation_val_20250729_193732/6000/pretrained_model \
    --screwdriver_camera=/dev/video0 \
    --side_camera=/dev/video2 \
    --top_camera=/dev/video6 \
    --camera_width=800 \
    --camera_height=600 \
    --camera_fps=30 \
    --duration=1200 \
    --fps=30 \
    --device=cuda \
    --screwdriver_current_limit=300 \
    --clutch_ratio=0.5 \
    --clutch_cooldown_s=1.0