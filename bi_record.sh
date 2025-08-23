#!/bin/bash

TEST_NUMBER=$1
EPISODES=$2

if [ -z "$TEST_NUMBER" ] || [ -z "$EPISODES" ]; then
    echo "Usage: $0 <test_number> <episodes>"
    exit 1
fi

# Bimanual Screwdriver Robot Recording
# Left arm: Screwdriver follower + leader
# Right arm: Regular Koch follower + leader

python -m assembler0.scripts.bi_record \
    --left_robot_port=/dev/servo_5837053138 \
    --right_robot_port=/dev/ttyACM3 \
    --robot_id=bi_koch_screwdriver_follower_testing \
    --left_robot_id=koch_screwdriver_follower_testing \
    --right_robot_id=koch_magnetic_follower_testing \
    --left_leader_port=/dev/servo_585A007782 \
    --right_leader_port=/dev/ttyACM2 \
    --leader_id=bi_koch_screwdriver_leader_testing \
    --left_leader_id=koch_screwdriver_leader_testing \
    --right_leader_id=koch_magnetic_leader_testing \
    --screwdriver_camera=/dev/video0 \
    --side_camera=/dev/video2 \
    --top_camera=/dev/video6 \
    --camera_width=800 \
    --camera_height=600 \
    --camera_fps=30 \
    --fps=30 \
    --left_screwdriver_current_limit=300 \
    --left_clutch_ratio=0.5 \
    --left_clutch_cooldown_s=1.0 \
    --left_gripper_open_pos=50.0 \
    --left_haptic_range=4.0 \
    --right_gripper_open_pos=50.0 \
    --dataset_repo_id=jackvial/screwdriver_bi_manual_test_${TEST_NUMBER}_e${EPISODES} \
    --num_episodes=${EPISODES} \
    --episode_time_s=12 \
    --reset_time_s=5 \
    --encode_videos_after=true \
    --push_to_hub=false \
    --single_task="Left arm: Move towards the silver screw in the orange panel. Then place the screwdriver bit on the screw, and turn the screwdriver bit clockwise until the screw is has been fully screwed in. Right arm: Assist and stabilize the workpiece during the screwing task." \
    --display_data=false \
    --play_sounds=false \
    --log_level=INFO 