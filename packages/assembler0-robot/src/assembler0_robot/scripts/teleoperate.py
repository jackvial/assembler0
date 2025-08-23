# Based on LeRobot https://github.com/huggingface/lerobot/blob/main/src/lerobot/teleoperate.py
# Modified to be specific to the Assembler 0 robot and require less configuration.

"""
See scripts/teleoperate.py for example usage
"""

import logging
import time
from dataclasses import dataclass
import argparse

from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig  # noqa: F401
from lerobot.cameras.realsense.configuration_realsense import RealSenseCameraConfig  # noqa: F401
from lerobot.robots import (  # noqa: F401
    Robot,
    RobotConfig,
    bi_so100_follower,
    hope_jr,
    koch_follower,
    make_robot_from_config,
    so100_follower,
    so101_follower,
)

from lerobot.teleoperators import (  # noqa: F401
    Teleoperator,
    TeleoperatorConfig,
    bi_so100_leader,
    gamepad,
    homunculus,
    koch_leader,
    make_teleoperator_from_config,
    so100_leader,
    so101_leader,
)

from assembler0_robot.robots.koch_screwdriver_follower import KochScrewdriverFollower
from assembler0_robot.robots.koch_screwdriver_follower import KochScrewdriverFollowerConfig
from assembler0_robot.teleoperators.koch_screwdriver_leader import KochScrewdriverLeader
from assembler0_robot.teleoperators.koch_screwdriver_leader import KochScrewdriverLeaderConfig

from lerobot.utils.robot_utils import busy_wait
from lerobot.utils.utils import init_logging, move_cursor_up
from lerobot.utils.visualization_utils import _init_rerun, log_rerun_data


@dataclass
class TeleoperateConfig:
    # TODO: pepijn, steven: if more robots require multiple teleoperators (like lekiwi) its good to make this possibele in teleop.py and record.py with List[Teleoperator]
    teleop: TeleoperatorConfig
    robot: RobotConfig
    # Limit the maximum frames per second.
    fps: int = 60
    teleop_time_s: float | None = None
    # Display all cameras on screen
    display_data: bool = False


def teleop_loop(
    teleop: Teleoperator, robot: Robot, fps: int, display_data: bool = False, duration: float | None = None
):
    display_len = max(len(key) for key in robot.action_features)
    start = time.perf_counter()
    while True:
        loop_start = time.perf_counter()
        action = teleop.get_action()
        if display_data:
            observation = robot.get_observation()
            log_rerun_data(observation, action)

        robot.send_action(action)
        dt_s = time.perf_counter() - loop_start
        busy_wait(1 / fps - dt_s)

        loop_s = time.perf_counter() - loop_start

        print("\n" + "-" * (display_len + 10))
        print(f"{'NAME':<{display_len}} | {'NORM':>7}")
        for motor, value in action.items():
            print(f"{motor:<{display_len}} | {value:>7.2f}")
        print(f"\ntime: {loop_s * 1e3:.2f}ms ({1 / loop_s:.0f} Hz)")

        if duration is not None and time.perf_counter() - start >= duration:
            return

        move_cursor_up(len(action) + 5)

def main():
    parser = argparse.ArgumentParser(description="Teleoperate the screwdriver robot")
    
    # Robot configuration
    parser.add_argument("--robot_port", type=str, default="/dev/servo_5837053138",
                       help="Serial port for the follower robot")
    parser.add_argument("--robot_id", type=str, default="koch_screwdriver_follower_testing",
                       help="ID for the follower robot")
    parser.add_argument("--screwdriver_current_limit", type=int, default=300,
                       help="Current limit for screwdriver motor")
    parser.add_argument("--clutch_ratio", type=float, default=0.5,
                       help="Clutch engagement ratio")
    parser.add_argument("--clutch_cooldown_s", type=float, default=1.0,
                       help="Clutch cooldown duration in seconds")
    
    # Leader configuration
    parser.add_argument("--leader_port", type=str, default="/dev/servo_585A007782",
                       help="Serial port for the leader teleoperator")
    parser.add_argument("--leader_id", type=str, default="koch_screwdriver_leader_testing",
                       help="ID for the leader teleoperator")
    parser.add_argument("--gripper_open_pos", type=float, default=50.0,
                       help="Gripper open position for the leader")
    parser.add_argument("--haptic_range", type=float, default=4.0,
                       help="Haptic feedback range")
    
    # Camera configuration
    parser.add_argument("--screwdriver_camera", type=str, default="/dev/video0",
                       help="Path or index for screwdriver camera")
    parser.add_argument("--side_camera", type=str, default="/dev/video2",
                       help="Path or index for side camera")  
    parser.add_argument("--top_camera", type=str, default=None,
                       help="Path or index for top camera")
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

    # Create robot config and instance
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
    
    robot_config = KochScrewdriverFollowerConfig(
        port=args.robot_port,
        id=args.robot_id,
        cameras=cameras,
        screwdriver_current_limit=args.screwdriver_current_limit,
        clutch_ratio=args.clutch_ratio,
        clutch_cooldown_s=args.clutch_cooldown_s,
    )
    robot = KochScrewdriverFollower(robot_config)
    
    # Create teleop config and instance
    teleop_config = KochScrewdriverLeaderConfig(
        port=args.leader_port,
        id=args.leader_id,
        gripper_open_pos=args.gripper_open_pos,
        haptic_range=args.haptic_range,
    )
    teleop = KochScrewdriverLeader(teleop_config)
    
    try:
        # Connect devices
        logger.info("Connecting robot...")
        robot.connect()
        logger.info("Connecting teleoperator...")
        teleop.connect()

        logger.info("Starting teleoperation. Press Ctrl+C to stop.")
        
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
            
            # Handle haptic feedback
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
        logger.info("\nStopping teleoperation...")
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
