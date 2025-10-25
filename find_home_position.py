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
Script to record waypoints for SO101Follower robot.

This script disables torque and allows manual positioning of the robot arm
while continuously displaying the current joint positions. Press the SPACE BAR
to capture each waypoint position, then press Ctrl+C to save all waypoints to
a JSON file that can be used with demo_so101_follower.py.

Example usage:
    python find_home_position.py --port /dev/ttyACM0
    
    # Save to custom file:
    python find_home_position.py --port /dev/ttyACM0 --output my_waypoints.json
"""

import argparse
import json
import logging
import select
import sys
import termios
import time
import tty
from pathlib import Path

from assembler0_robot.robots.so101_follower import SO101Follower, SO101FollowerConfig

logger = logging.getLogger(__name__)


def is_key_pressed():
    """Check if a key has been pressed (non-blocking)."""
    return select.select([sys.stdin], [], [], 0)[0] != []


def get_key():
    """Get a single keypress (non-blocking if key is available)."""
    if is_key_pressed():
        return sys.stdin.read(1)
    return None


def save_waypoints_to_file(waypoints: list[dict[str, float]], filepath: str) -> None:
    """Save waypoints to a JSON file.
    
    Args:
        waypoints: List of waypoint dictionaries
        filepath: Path to save the JSON file
    """
    path = Path(filepath)
    with open(path, "w") as f:
        json.dump(waypoints, f, indent=2)
    logger.info(f"Saved {len(waypoints)} waypoints to {filepath}")


def main():
    parser = argparse.ArgumentParser(
        description="Record waypoints for SO101Follower robot by manually positioning it"
    )
    
    # Robot configuration
    parser.add_argument(
        "--port",
        type=str,
        required=True,
        help="Serial port for the SO101Follower robot (e.g., /dev/ttyACM0)",
    )
    parser.add_argument(
        "--robot_id",
        type=str,
        default="assembler0_so101_follower",
        help="ID for the robot (should match calibration file ID)",
    )
    parser.add_argument(
        "--update_rate",
        type=float,
        default=0.5,
        help="Update rate in seconds for position display (default: 0.5)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="waypoints.json",
        help="Output JSON file for saved waypoints (default: waypoints.json)",
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create robot configuration
    robot_config = SO101FollowerConfig(
        port=args.port,
        id=args.robot_id,
        cameras={},  # No cameras needed
        disable_torque_on_disconnect=True,
    )
    
    # Create robot instance
    robot = SO101Follower(robot_config)
    
    try:
        # Connect to robot
        logger.info("Connecting to SO101Follower robot...")
        robot.connect()
        logger.info("Robot connected successfully!")
        
        # Disable torque so arm can be moved manually
        logger.info("Disabling torque - you can now move the arm manually")
        robot.bus.disable_torque()
        
        print("\n" + "=" * 80)
        print("MANUAL POSITIONING MODE - WAYPOINT RECORDER")
        print("=" * 80)
        print("\nThe robot torque is now DISABLED. You can manually move the arm.")
        print("Move the arm to each desired waypoint position.")
        print("\nControls:")
        print("  SPACE BAR - Capture current position as a waypoint")
        print("  Ctrl+C    - Finish and save all waypoints to file")
        print("=" * 80 + "\n")
        
        # Set terminal to raw mode for immediate key capture
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setcbreak(sys.stdin.fileno())
            
            # Continuously read and display positions
            logger.info("Reading current positions (updating every {:.1f}s)...".format(args.update_rate))
            print("\nCurrent Joint Positions:")
            print("-" * 80)
            
            last_positions = {}
            waypoints = []
            
            while True:
                try:
                    # Check for spacebar press
                    key = get_key()
                    if key == ' ':
                        # Capture current position as waypoint
                        current_positions = robot.bus.sync_read("Present_Position")
                        waypoint = {}
                        for motor_name in robot.bus.motors:
                            pos = current_positions.get(motor_name, 0.0)
                            waypoint[f"{motor_name}.pos"] = round(pos, 2)
                        
                        waypoints.append(waypoint)
                        print(f"\n✓ Waypoint {len(waypoints)} captured!")
                        time.sleep(0.3)  # Brief pause to prevent double-capture
                    
                    # Read current positions from motors
                    current_positions = robot.bus.sync_read("Present_Position")
                    
                    # Clear previous lines (move cursor up)
                    if last_positions:
                        print("\033[F" * (len(robot.bus.motors) + 4))
                    
                    # Display current positions
                    print(f"\nCurrent Joint Positions (Waypoints captured: {len(waypoints)}):")
                    print("-" * 80)
                    
                    for motor_name in robot.bus.motors:
                        pos = current_positions.get(motor_name, 0.0)
                        print(f"  {motor_name:20s}: {pos:8.2f}")
                    
                    print("-" * 80)
                    
                    last_positions = current_positions.copy()
                    
                    # Wait before next update
                    time.sleep(args.update_rate)
                    
                except Exception as e:
                    logger.error(f"Error reading positions: {e}")
                    time.sleep(1)
        
        finally:
            # Restore terminal settings
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        
    except KeyboardInterrupt:
        # Restore terminal settings first
        try:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        except Exception:
            pass
        
        print("\n\n" + "=" * 80)
        print("SAVING WAYPOINTS")
        print("=" * 80)
        
        try:
            if len(waypoints) > 0:
                # Save waypoints to JSON file
                save_waypoints_to_file(waypoints, args.output)
                
                print(f"\n✓ Saved {len(waypoints)} waypoint(s) to {args.output}")
                print("\nWaypoints:")
                print("-" * 80)
                
                for i, wp in enumerate(waypoints):
                    print(f"\nWaypoint {i + 1}:")
                    for key, value in wp.items():
                        print(f"  {key:25s}: {value:8.2f}")
                
                print("\n" + "=" * 80)
                print("You can now use these waypoints with:")
                print(f"  python demo_so101_follower.py --port {args.port} --waypoints_file {args.output}")
                print("=" * 80 + "\n")
            else:
                print("\nNo waypoints were captured.")
                print("Run the script again and press SPACE BAR to capture waypoints.")
                print("=" * 80)
                print()
            
        except Exception as e:
            logger.error(f"Error saving waypoints: {e}")
        
    except Exception as e:
        logger.error(f"Error during position finding: {e}")
        raise
    finally:
        # Disconnect robot
        logger.info("Disconnecting robot...")
        try:
            robot.disconnect()
            logger.info("Robot disconnected successfully!")
        except Exception as e:
            logger.error(f"Error disconnecting robot: {e}")
    
    return 0


if __name__ == "__main__":
    exit(main())

