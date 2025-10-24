#!/usr/bin/env python

# Copyright 2025 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Demo script for SO101Follower robot that moves through predefined waypoints.

Example usage:
    python demo_so101_follower.py --port /dev/ttyACM0 --robot_id assembler0_so101_follower

    # With custom waypoints file:
    python demo_so101_follower.py --port /dev/ttyACM0 --robot_id assembler0_so101_follower --waypoints_file waypoints.json
"""

import argparse
import json
import logging
import time
from pathlib import Path

from lerobot.utils.robot_utils import busy_wait

from assembler0_robot.robots.so101_follower import SO101Follower, SO101FollowerConfig

logger = logging.getLogger(__name__)


# Define default waypoints for demonstration
# Each waypoint is a dictionary of motor positions
DEFAULT_WAYPOINTS = [
    # Home position (neutral/rest)
    {
        "shoulder_pan.pos": 10.0,
        "shoulder_lift.pos": 0.0,
        "elbow_flex.pos": 0.0,
        "wrist_flex.pos": 0.0,
        "wrist_roll.pos": 0.0,
        "gripper.pos": 50.0,
    },
    # Wave position 1 - raise arm
    # {
    #     "shoulder_pan.pos": 30.0,
    #     "shoulder_lift.pos": -30.0,
    #     "elbow_flex.pos": 30.0,
    #     "wrist_flex.pos": 0.0,
    #     "wrist_roll.pos": 0.0,
    #     "gripper.pos": 50.0,
    # },
    # # Wave position 2 - move arm right
    # {
    #     "shoulder_pan.pos": 50.0,
    #     "shoulder_lift.pos": -30.0,
    #     "elbow_flex.pos": 30.0,
    #     "wrist_flex.pos": 0.0,
    #     "wrist_roll.pos": 30.0,
    #     "gripper.pos": 50.0,
    # },
    # # Wave position 3 - move arm left
    # {
    #     "shoulder_pan.pos": -50.0,
    #     "shoulder_lift.pos": -30.0,
    #     "elbow_flex.pos": 30.0,
    #     "wrist_flex.pos": 0.0,
    #     "wrist_roll.pos": -30.0,
    #     "gripper.pos": 50.0,
    # },
    # # Wave position 4 - back to center
    # {
    #     "shoulder_pan.pos": 0.0,
    #     "shoulder_lift.pos": -30.0,
    #     "elbow_flex.pos": 30.0,
    #     "wrist_flex.pos": 0.0,
    #     "wrist_roll.pos": 0.0,
    #     "gripper.pos": 50.0,
    # },
    # # Close gripper
    # {
    #     "shoulder_pan.pos": 0.0,
    #     "shoulder_lift.pos": -30.0,
    #     "elbow_flex.pos": 30.0,
    #     "wrist_flex.pos": 0.0,
    #     "wrist_roll.pos": 0.0,
    #     "gripper.pos": 100.0,
    # },
    # # Open gripper
    # {
    #     "shoulder_pan.pos": 0.0,
    #     "shoulder_lift.pos": -30.0,
    #     "elbow_flex.pos": 30.0,
    #     "wrist_flex.pos": 0.0,
    #     "wrist_roll.pos": 0.0,
    #     "gripper.pos": 0.0,
    # },
    # # Return to home position
    # {
    #     "shoulder_pan.pos": 0.0,
    #     "shoulder_lift.pos": 0.0,
    #     "elbow_flex.pos": 0.0,
    #     "wrist_flex.pos": 0.0,
    #     "wrist_roll.pos": 0.0,
    #     "gripper.pos": 50.0,
    # },
]


def load_waypoints_from_file(filepath: str) -> list[dict[str, float]]:
    """Load waypoints from a JSON file.
    
    Args:
        filepath: Path to JSON file containing waypoints
        
    Returns:
        List of waypoint dictionaries
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Waypoints file not found: {filepath}")
    
    with open(path, "r") as f:
        waypoints = json.load(f)
    
    if not isinstance(waypoints, list):
        raise ValueError("Waypoints file must contain a JSON array of waypoint objects")
    
    logger.info(f"Loaded {len(waypoints)} waypoints from {filepath}")
    return waypoints


def move_through_waypoints(
    robot: SO101Follower,
    waypoints: list[dict[str, float]],
    fps: int = 30,
    wait_time_s: float = 2.0,
) -> None:
    """Move robot through a sequence of waypoints.
    
    Args:
        robot: Connected SO101Follower instance
        waypoints: List of waypoint dictionaries with motor positions
        fps: Control loop frequency in Hz
        wait_time_s: Time to wait at each waypoint before moving to next
    """
    logger.info(f"Starting waypoint sequence with {len(waypoints)} waypoints")
    
    for i, waypoint in enumerate(waypoints):
        logger.info(f"Moving to waypoint {i + 1}/{len(waypoints)}")
        logger.debug(f"Target positions: {waypoint}")
        
        # Calculate how many steps to wait at this waypoint
        wait_steps = int(wait_time_s * fps)
        
        # Send the same action repeatedly for smooth motion and waiting
        for step in range(wait_steps):
            loop_start = time.perf_counter()
            
            # Send action to robot
            robot.send_action(waypoint)
            
            # Maintain control loop timing
            dt_s = time.perf_counter() - loop_start
            busy_wait(1 / fps - dt_s)
        
        logger.info(f"Reached waypoint {i + 1}/{len(waypoints)}")
    
    logger.info("Waypoint sequence completed!")


def main():
    parser = argparse.ArgumentParser(
        description="Demo script to move SO101Follower robot through preprogrammed waypoints"
    )
    
    # Robot configuration
    parser.add_argument(
        "--port",
        type=str,
        required=True,
        help="Serial port for the SO101Follower robot (e.g., /dev/ttyUSB0)",
    )
    parser.add_argument(
        "--robot_id",
        type=str,
        default="assembler0_so101_follower",
        help="ID for the robot (should match the calibration file ID)",
    )
    
    # Waypoint configuration
    parser.add_argument(
        "--waypoints_file",
        type=str,
        default=None,
        help="Optional JSON file with custom waypoints. If not provided, uses built-in demo waypoints.",
    )
    parser.add_argument(
        "--wait_time",
        type=float,
        default=2.0,
        help="Time to wait at each waypoint in seconds (default: 2.0)",
    )
    
    # Control parameters
    parser.add_argument(
        "--fps",
        type=int,
        default=30,
        help="Control loop frequency in Hz (default: 30)",
    )
    
    # Other options
    parser.add_argument(
        "--disable_torque_on_disconnect",
        action="store_true",
        help="Disable motor torque when disconnecting (robot will go limp)",
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Load waypoints
    if args.waypoints_file:
        try:
            waypoints = load_waypoints_from_file(args.waypoints_file)
        except Exception as e:
            logger.error(f"Failed to load waypoints from file: {e}")
            return 1
    else:
        logger.info("Using default demo waypoints")
        waypoints = DEFAULT_WAYPOINTS
    
    # Create robot configuration
    robot_config = SO101FollowerConfig(
        port=args.port,
        id=args.robot_id,
        cameras={},  # No cameras needed for this demo
        disable_torque_on_disconnect=args.disable_torque_on_disconnect,
    )
    
    # Create robot instance
    robot = SO101Follower(robot_config)
    
    try:
        # Connect to robot
        logger.info("Connecting to SO101Follower robot...")
        robot.connect()
        logger.info("Robot connected successfully!")
        
        # Small delay to ensure robot is ready
        time.sleep(0.5)
        
        # Move through waypoints
        move_through_waypoints(
            robot=robot,
            waypoints=waypoints,
            fps=args.fps,
            wait_time_s=args.wait_time,
        )
        
    except KeyboardInterrupt:
        logger.info("\nDemo interrupted by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Error during demo: {e}")
        raise
    finally:
        # Always disconnect robot
        logger.info("Disconnecting robot...")
        try:
            robot.disconnect()
            logger.info("Robot disconnected successfully!")
        except Exception as e:
            logger.error(f"Error disconnecting robot: {e}")
    
    return 0


if __name__ == "__main__":
    exit(main())

