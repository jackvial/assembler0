#!/bin/bash

# echo "Calibrating so101 follower robot..."
python -m assembler0_robot.scripts.calibrate \
    --device_type=robot \
    --port=/dev/ttyACM0 \
    --device_id=so101_follower


# Calibrate the so101 leader teleoperator
# echo "Calibrating screwdriver leader teleoperator..."
python -m assembler0_robot.scripts.calibrate \
    --device_type=leader \
    --port=/dev/ttyACM1 \
    --device_id=so101_leader


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
