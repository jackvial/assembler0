# Based on LeRobot https://github.com/huggingface/lerobot/blob/main/src/lerobot/teleoperate.py
"""
See scripts/bi_teleoperate.py for example usage
"""

import logging
import time
import argparse

from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig  # noqa: F401
from lerobot.cameras.realsense.configuration_realsense import RealSenseCameraConfig  # noqa: F401

from assembler0_robot.robots.bi_koch_screwdriver_follower import BiKochScrewdriverFollower
from assembler0_robot.robots.bi_koch_screwdriver_follower import BiKochScrewdriverFollowerConfig
from assembler0_robot.teleoperators.bi_koch_screwdriver_leader import BiKochScrewdriverLeader
from assembler0_robot.teleoperators.bi_koch_screwdriver_leader import BiKochScrewdriverLeaderConfig

from lerobot.utils.robot_utils import busy_wait


def main():
    parser = argparse.ArgumentParser(description="Teleoperate the bimanual screwdriver robot")
    
    # Robot configuration
    parser.add_argument("--left_robot_port", type=str, default="/dev/servo_5837053138",
                       help="Serial port for the left arm (screwdriver) follower robot")
    parser.add_argument("--right_robot_port", type=str, default="/dev/servo_5837053139",
                       help="Serial port for the right arm (gripper) follower robot")
    parser.add_argument("--robot_id", type=str, default="bi_koch_screwdriver_follower_testing",
                       help="ID for the bimanual follower robot")
    parser.add_argument("--left_robot_id", type=str, default=None,
                       help="ID for left arm robot (uses existing calibration if provided)")
    parser.add_argument("--right_robot_id", type=str, default=None,
                       help="ID for right arm robot (uses existing calibration if provided)")
    
    # Left arm (screwdriver) specific parameters
    parser.add_argument("--left_screwdriver_current_limit", type=int, default=300,
                       help="Current limit for screwdriver motor")
    parser.add_argument("--left_clutch_ratio", type=float, default=0.5,
                       help="Clutch engagement ratio")
    parser.add_argument("--left_clutch_cooldown_s", type=float, default=1.0,
                       help="Clutch cooldown duration in seconds")
    
    # Leader configuration
    parser.add_argument("--left_leader_port", type=str, default="/dev/servo_585A007782",
                       help="Serial port for the left arm (screwdriver) leader teleoperator")
    parser.add_argument("--right_leader_port", type=str, default="/dev/servo_585A007783",
                       help="Serial port for the right arm (gripper) leader teleoperator")
    parser.add_argument("--leader_id", type=str, default="bi_koch_screwdriver_leader_testing",
                       help="ID for the bimanual leader teleoperator")
    parser.add_argument("--left_leader_id", type=str, default=None,
                       help="ID for left arm leader (uses existing calibration if provided)")
    parser.add_argument("--right_leader_id", type=str, default=None,
                       help="ID for right arm leader (uses existing calibration if provided)")
    
    # Left arm (screwdriver leader) specific parameters
    parser.add_argument("--left_gripper_open_pos", type=float, default=50.0,
                       help="Gripper open position for the left leader")
    parser.add_argument("--left_haptic_range", type=float, default=4.0,
                       help="Haptic feedback range for left leader")
    
    # Right arm (regular leader) specific parameters
    parser.add_argument("--right_gripper_open_pos", type=float, default=50.0,
                       help="Gripper open position for the right leader")
    
    # Camera configuration
    parser.add_argument("--screwdriver_camera", type=str, default="/dev/video0",
                       help="Path or index for screwdriver camera")
    parser.add_argument("--side_camera", type=str, default="/dev/video2",
                       help="Path or index for side camera")  
    parser.add_argument("--top_camera", type=str, default="/dev/video4",
                       help="Path or index for top camera")
    parser.add_argument("--left_camera", type=str, default=None,
                       help="Path or index for left camera")
    parser.add_argument("--right_camera", type=str, default=None,
                       help="Path or index for right camera")
    parser.add_argument("--camera_width", type=int, default=800,
                       help="Camera width")
    parser.add_argument("--camera_height", type=int, default=600,
                       help="Camera height") 
    parser.add_argument("--camera_fps", type=int, default=30,
                       help="Camera FPS")
    
    # Control parameters
    parser.add_argument("--fps", type=int, default=30,
                       help="Control loop frequency")
    parser.add_argument("--duration", type=int, default=None,
                       help="Duration in seconds (None for infinite)")
    
    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Create camera configurations
    cameras = {}
    if args.screwdriver_camera:
        cameras["screwdriver"] = OpenCVCameraConfig(
            index_or_path=args.screwdriver_camera, 
            width=args.camera_width, 
            height=args.camera_height, 
            fps=args.camera_fps
        )
    if args.side_camera:
        cameras["side"] = OpenCVCameraConfig(
            index_or_path=args.side_camera, 
            width=args.camera_width, 
            height=args.camera_height, 
            fps=args.camera_fps
        )
    if args.top_camera:
        cameras["top"] = OpenCVCameraConfig(
            index_or_path=args.top_camera, 
            width=args.camera_width, 
            height=args.camera_height, 
            fps=args.camera_fps
        )
    if args.left_camera:
        cameras["left"] = OpenCVCameraConfig(
            index_or_path=args.left_camera, 
            width=args.camera_width, 
            height=args.camera_height, 
            fps=args.camera_fps
        )
    if args.right_camera:
        cameras["right"] = OpenCVCameraConfig(
            index_or_path=args.right_camera, 
            width=args.camera_width, 
            height=args.camera_height, 
            fps=args.camera_fps
        )
    
    # Create bimanual robot config and instance
    robot_config = BiKochScrewdriverFollowerConfig(
        left_arm_port=args.left_robot_port,
        right_arm_port=args.right_robot_port,
        id=args.robot_id,
        left_arm_id=args.left_robot_id,
        right_arm_id=args.right_robot_id,
        cameras=cameras,
        left_arm_screwdriver_current_limit=args.left_screwdriver_current_limit,
        left_arm_clutch_ratio=args.left_clutch_ratio,
        left_arm_clutch_cooldown_s=args.left_clutch_cooldown_s,
    )
    robot = BiKochScrewdriverFollower(robot_config)
    
    # Create bimanual teleop config and instance
    teleop_config = BiKochScrewdriverLeaderConfig(
        left_arm_port=args.left_leader_port,
        right_arm_port=args.right_leader_port,
        id=args.leader_id,
        left_arm_id=args.left_leader_id,
        right_arm_id=args.right_leader_id,
        left_arm_gripper_open_pos=args.left_gripper_open_pos,
        left_arm_haptic_range=args.left_haptic_range,
        right_arm_gripper_open_pos=args.right_gripper_open_pos,
    )
    teleop = BiKochScrewdriverLeader(teleop_config)
    
    try:
        # Connect devices
        logger.info("Connecting bimanual robot...")
        robot.connect()
        logger.info("Connecting bimanual teleoperator...")
        teleop.connect()

        logger.info("Starting bimanual teleoperation. Press Ctrl+C to stop.")
        
        start_time = time.time()
        step_count = 0
        
        while True:
            loop_start = time.perf_counter()
            
            # Check duration limit
            if args.duration is not None:
                elapsed = time.time() - start_time
                if elapsed >= args.duration:
                    logger.info(f"Duration limit reached ({args.duration}s)")
                    break
            
            # Get action from leader
            action = teleop.get_action()
            
            # Send action to follower
            robot.send_action(action)
            
            # Handle haptic feedback (only from left arm screwdriver)
            try:
                feedback = robot.get_feedback()
                if feedback:
                    teleop.send_feedback(feedback)
            except Exception as e:
                logger.debug(f"Feedback warning: {e}")
            
            step_count += 1
            
            # Log progress every second
            if step_count % args.fps == 0:
                elapsed = time.time() - start_time
                logger.info(f"Step: {step_count}, Time: {elapsed:.1f}s")
            
            # Maintain loop timing
            dt_s = time.perf_counter() - loop_start
            busy_wait(1/args.fps - dt_s)
            
    except KeyboardInterrupt:
        logger.info("\nStopping bimanual teleoperation...")
    except Exception as e:
        logger.error(f"Error during teleoperation: {e}")
        raise
    finally:
        logger.info("Disconnecting devices...")
        try:
            robot.disconnect()
        except Exception as e:
            logger.error(f"Error disconnecting robot: {e}")
        try:
            teleop.disconnect()
        except Exception as e:
            logger.error(f"Error disconnecting teleoperator: {e}")
        logger.info("Done.")


if __name__ == "__main__":
    main() 