# Based on LeRobot https://github.com/huggingface/lerobot/blob/main/src/lerobot/scripts/calibrate.py
# Modified to be specific to the Assembler 0 robot and require less configuration.

"""
See scripts/calibrate.py for example usage
"""

import logging
import argparse

from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig  # noqa: F401
from lerobot.cameras.realsense.configuration_realsense import RealSenseCameraConfig  # noqa: F401

from assembler0_robot.robots.koch_screwdriver_follower import KochScrewdriverFollower
from assembler0_robot.robots.koch_screwdriver_follower import KochScrewdriverFollowerConfig
from assembler0_robot.robots.koch_follower import KochFollower, KochFollowerConfig
from assembler0_robot.teleoperators.koch_screwdriver_leader import KochScrewdriverLeader
from assembler0_robot.teleoperators.koch_screwdriver_leader import KochScrewdriverLeaderConfig
from assembler0_robot.teleoperators.koch_leader import KochLeader, KochLeaderConfig
from assembler0_robot.robots.so101_follower import So101Follower, So101FollowerConfig
from assembler0_robot.teleoperators.so101_leader import So101Leader, So101LeaderConfig


def main():
    parser = argparse.ArgumentParser(description="Calibrate screwdriver robot or teleoperator")
    
    # Device configuration
    parser.add_argument("--device_type", type=str, choices=["robot", "follower", "leader", "teleop"],
                       required=True, help="Type of device to calibrate")
    parser.add_argument("--robot_variant", type=str, choices=["screwdriver", "koch", "so101"], default="screwdriver",
                       help="Robot variant: 'screwdriver' for screwdriver arms, 'koch' for regular Koch arms, 'so101' for So101 arms")
    parser.add_argument("--port", type=str, required=True,
                       help="Serial port for the device")
    parser.add_argument("--device_id", type=str, required=True,
                       help="ID for the device")
    
    # Robot-specific parameters
    parser.add_argument("--screwdriver_current_limit", type=int, default=300,
                       help="Current limit for screwdriver motor (robot only)")
    parser.add_argument("--clutch_ratio", type=float, default=0.5,
                       help="Clutch engagement ratio (robot only)")
    parser.add_argument("--clutch_cooldown_s", type=float, default=1.0,
                       help="Clutch cooldown duration in seconds (robot only)")
    
    # Leader-specific parameters
    parser.add_argument("--gripper_open_pos", type=float, default=50.0,
                       help="Gripper open position for the leader (leader only)")
    parser.add_argument("--haptic_range", type=float, default=4.0,
                       help="Haptic feedback range (leader only)")
    
    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Determine device type
    is_robot = args.device_type in ["robot", "follower"]
    is_leader = args.device_type in ["leader", "teleop"]
    
    if not (is_robot or is_leader):
        raise ValueError("device_type must be one of: robot, follower, leader, teleop")

    try:
        if is_robot:
            if args.robot_variant == "screwdriver":
                logger.info("Calibrating screwdriver robot (follower)...")
                
                # Create robot config and instance (no cameras needed for calibration)
                robot_config = KochScrewdriverFollowerConfig(
                    port=args.port,
                    id=args.device_id,
                    cameras={},  # No cameras needed for calibration
                    screwdriver_current_limit=args.screwdriver_current_limit,
                    clutch_ratio=args.clutch_ratio,
                    clutch_cooldown_s=args.clutch_cooldown_s,
                )
                device = KochScrewdriverFollower(robot_config)
                
            elif args.robot_variant == "so101":
                logger.info("Calibrating so101 robot (follower)...")
                
                # Create robot config and instance (no cameras needed for calibration)
                robot_config = So101FollowerConfig(
                    port=args.port,
                    id=args.device_id,
                    cameras={},  # No cameras needed for calibration
                )
                device = So101Follower(robot_config)
                
            else:  # koch variant
                logger.info("Calibrating Koch robot (follower)...")
                
                # Create robot config and instance (no cameras needed for calibration)
                robot_config = KochFollowerConfig(
                    port=args.port,
                    id=args.device_id,
                    cameras={},  # No cameras needed for calibration
                )
                device = KochFollower(robot_config)
            
        else:  # is_leader
            if args.robot_variant == "screwdriver":
                logger.info("Calibrating screwdriver teleoperator (leader)...")
                
                # Create teleop config and instance
                teleop_config = KochScrewdriverLeaderConfig(
                    port=args.port,
                    id=args.device_id,
                    gripper_open_pos=args.gripper_open_pos,
                    haptic_range=args.haptic_range,
                )
                device = KochScrewdriverLeader(teleop_config)
            elif args.robot_variant == "so101":
                logger.info("Calibrating so101 teleoperator (leader)...")
                
                # Create teleop config and instance
                teleop_config = So101LeaderConfig(
                    port=args.port,
                    id=args.device_id,
                )
                device = So101Leader(teleop_config)
                
            else:  # koch variant
                logger.info("Calibrating Koch teleoperator (leader)...")
                
                # Create teleop config and instance
                teleop_config = KochLeaderConfig(
                    port=args.port,
                    id=args.device_id,
                    gripper_open_pos=args.gripper_open_pos,
                )
                device = KochLeader(teleop_config)
        # Perform calibration
        logger.info("Connecting device...")
        device.connect(calibrate=False)
        
        logger.info("Starting calibration...")
        device.calibrate()
        
        logger.info("Calibration completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during calibration: {e}")
        raise
    finally:
        logger.info("Disconnecting device...")
        try:
            device.disconnect()
        except Exception as e:
            logger.error(f"Error disconnecting device: {e}")
        logger.info("Done.")


if __name__ == "__main__":
    main()
