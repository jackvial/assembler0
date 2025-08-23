# Based on LeRobot https://github.com/huggingface/lerobot/blob/main/src/lerobot/record.py
# Modified to support bimanual Assembler 0 robot.

"""
See scripts/bi_record.py for example usage
"""

import logging
import time
import argparse
from pathlib import Path

from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.datasets.utils import build_dataset_frame, hw_to_dataset_features
from lerobot.datasets.image_writer import safe_stop_image_writer
from lerobot.utils.control_utils import (
    init_keyboard_listener,
    is_headless,
    sanity_check_dataset_name,
    sanity_check_dataset_robot_compatibility,
)
from lerobot.utils.robot_utils import busy_wait
from lerobot.utils.utils import (
    init_logging,
    log_say,
)
from lerobot.utils.visualization_utils import _init_rerun, log_rerun_data

from assembler0_robot.robots.bi_koch_screwdriver_follower import BiKochScrewdriverFollower
from assembler0_robot.robots.bi_koch_screwdriver_follower import BiKochScrewdriverFollowerConfig
from assembler0_robot.teleoperators.bi_koch_screwdriver_leader import BiKochScrewdriverLeader
from assembler0_robot.teleoperators.bi_koch_screwdriver_leader import BiKochScrewdriverLeaderConfig


@safe_stop_image_writer
def record_loop(
    robot,
    teleop,
    events,
    fps: int,
    dataset=None,
    control_time_s=None,
    single_task=None,
    display_data: bool = False,
):
    logger = logging.getLogger(__name__)
    if dataset is not None and dataset.fps != fps:
        raise ValueError(f"The dataset fps should be equal to requested fps ({dataset.fps} != {fps}).")

    timestamp = 0
    start_episode_t = time.perf_counter()
    while timestamp < control_time_s:
        start_loop_t = time.perf_counter()

        if events["exit_early"]:
            events["exit_early"] = False
            break

        # Try to get observation with retry logic
        try:
            observation = robot.get_observation()
        except Exception as e:
            logger.warning(f"Failed to get observation, retrying... Error: {e}")
            time.sleep(0.1)
            try:
                observation = robot.get_observation()
            except Exception as e:
                logger.error(f"Failed to get observation after retry: {e}")
                events["exit_early"] = True
                continue

        if dataset is not None:
            observation_frame = build_dataset_frame(dataset.features, observation, prefix="observation")

        # Get action from teleoperator
        action = teleop.get_action()

        # Action can eventually be clipped using `max_relative_target`,
        # so action actually sent is saved in the dataset.
        sent_action = robot.send_action(action)

        if dataset is not None:
            action_frame = build_dataset_frame(dataset.features, sent_action, prefix="action")
            frame = {**observation_frame, **action_frame}
            dataset.add_frame(frame, task=single_task)

        if display_data:
            log_rerun_data(observation, action)

        dt_s = time.perf_counter() - start_loop_t
        busy_wait(1 / fps - dt_s)

        timestamp = time.perf_counter() - start_episode_t


def main():
    parser = argparse.ArgumentParser(description="Record dataset with the bimanual screwdriver robot")
    
    # Bimanual robot configuration
    parser.add_argument("--left_robot_port", type=str, default="/dev/servo_5837053138",
                       help="Serial port for the left follower robot")
    parser.add_argument("--right_robot_port", type=str, default="/dev/ttyACM2",
                       help="Serial port for the right follower robot")
    parser.add_argument("--robot_id", type=str, default="bi_koch_screwdriver_follower_testing",
                       help="ID for the bimanual follower robot")
    parser.add_argument("--left_robot_id", type=str, default="koch_screwdriver_follower_testing",
                       help="ID for the left follower robot")
    parser.add_argument("--right_robot_id", type=str, default="koch_magnetic_follower_testing",
                       help="ID for the right follower robot")
    parser.add_argument("--left_screwdriver_current_limit", type=int, default=300,
                       help="Current limit for left arm screwdriver motor")
    parser.add_argument("--left_clutch_ratio", type=float, default=0.5,
                       help="Clutch engagement ratio for left arm")
    parser.add_argument("--left_clutch_cooldown_s", type=float, default=1.0,
                       help="Clutch cooldown duration in seconds for left arm")
    
    # Bimanual leader configuration
    parser.add_argument("--left_leader_port", type=str, default="/dev/servo_585A007782",
                       help="Serial port for the left leader teleoperator")
    parser.add_argument("--right_leader_port", type=str, default="/dev/ttyACM3",
                       help="Serial port for the right leader teleoperator")
    parser.add_argument("--leader_id", type=str, default="bi_koch_screwdriver_leader_testing",
                       help="ID for the bimanual leader teleoperator")
    parser.add_argument("--left_leader_id", type=str, default="koch_screwdriver_leader_testing",
                       help="ID for the left leader teleoperator")
    parser.add_argument("--right_leader_id", type=str, default="koch_magnetic_leader_testing",
                       help="ID for the right leader teleoperator")
    parser.add_argument("--left_gripper_open_pos", type=float, default=50.0,
                       help="Gripper open position for the left leader")
    parser.add_argument("--left_haptic_range", type=float, default=4.0,
                       help="Haptic feedback range for left leader")
    parser.add_argument("--right_gripper_open_pos", type=float, default=50.0,
                       help="Gripper open position for the right leader")
    
    # Camera configuration
    parser.add_argument("--screwdriver_camera", type=str, default="/dev/video0",
                       help="Path or index for screwdriver camera")
    parser.add_argument("--side_camera", type=str, default="/dev/video2",
                       help="Path or index for side camera")  
    parser.add_argument("--top_camera", type=str, default="/dev/video6",
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
    
    # Dataset configuration
    parser.add_argument("--dataset_repo_id", type=str, required=True,
                       help="Dataset identifier (e.g. 'jackvial/my_dataset')")
    parser.add_argument("--single_task", type=str, required=True,
                       help="Task description for the dataset")
    parser.add_argument("--dataset_root", type=str, default=None,
                       help="Root directory for dataset storage")
    parser.add_argument("--num_episodes", type=int, default=50,
                       help="Number of episodes to record")
    parser.add_argument("--episode_time_s", type=int, default=60,
                       help="Duration of each episode in seconds")
    parser.add_argument("--reset_time_s", type=int, default=60,
                       help="Reset time between episodes in seconds")
    parser.add_argument("--encode_videos_after", type=lambda x: x.lower() in ['true', '1', 'yes'], default=True,
                       help="Encode frames into videos after recording")
    parser.add_argument("--push_to_hub", type=lambda x: x.lower() in ['true', '1', 'yes'], default=True,
                       help="Push dataset to Hugging Face hub")
    parser.add_argument("--private", type=lambda x: x.lower() in ['true', '1', 'yes'], default=False,
                       help="Make dataset private on hub")
    parser.add_argument("--num_image_writer_processes", type=int, default=0,
                       help="Number of image writer processes")
    parser.add_argument("--num_image_writer_threads_per_camera", type=int, default=4,
                       help="Number of image writer threads per camera")
    
    # Control parameters
    parser.add_argument("--fps", type=int, default=30,
                       help="Control loop frequency")
    parser.add_argument("--display_data", type=lambda x: x.lower() in ['true', '1', 'yes'], default=False,
                       help="Display camera feeds during recording")
    parser.add_argument("--play_sounds", type=lambda x: x.lower() in ['true', '1', 'yes'], default=True,
                       help="Play audio notifications")
    parser.add_argument("--resume", type=lambda x: x.lower() in ['true', '1', 'yes'], default=False,
                       help="Resume recording on existing dataset")
    parser.add_argument("--log_level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Logging level")
    
    args = parser.parse_args()

    # Setup logging
    init_logging()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=True
    )
    logger = logging.getLogger(__name__)

    if args.display_data:
        _init_rerun(session_name="recording")

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

    # Create dataset features
    action_features = hw_to_dataset_features(robot.action_features, "action", args.encode_videos_after)
    obs_features = hw_to_dataset_features(robot.observation_features, "observation", args.encode_videos_after)
    dataset_features = {**action_features, **obs_features}

    if args.resume:
        dataset = LeRobotDataset(
            args.dataset_repo_id,
            root=args.dataset_root,
        )

        if hasattr(robot, "cameras") and len(robot.cameras) > 0:
            dataset.start_image_writer(
                num_processes=args.num_image_writer_processes,
                num_threads=args.num_image_writer_threads_per_camera * len(robot.cameras),
            )
        sanity_check_dataset_robot_compatibility(dataset, robot, args.fps, dataset_features)
    else:
        # Create empty dataset or load existing saved episodes
        sanity_check_dataset_name(args.dataset_repo_id, None)
        dataset = LeRobotDataset.create(
            args.dataset_repo_id,
            args.fps,
            root=args.dataset_root,
            robot_type=robot.name,
            features=dataset_features,
            use_videos=args.encode_videos_after,
            image_writer_processes=args.num_image_writer_processes,
            image_writer_threads=args.num_image_writer_threads_per_camera * len(robot.cameras),
        )

    try:
        # Connect devices
        logger.info("Connecting bimanual robot...")
        robot.connect()
        logger.info("Connecting bimanual teleoperator...")
        teleop.connect()

        # try:
        #     listener, events = init_keyboard_listener()
        # except Exception as e:
        #     logger.warning(f"Failed to initialize keyboard listener: {e}")
        #     logger.warning("Recording will continue without keyboard shortcuts")
        listener = None
        events = {"stop_recording": False, "exit_early": False, "rerecord_episode": False}

        # Give the robot a moment to stabilize after connection
        logger.info("Waiting for robot to stabilize...")
        time.sleep(2.0)

        recorded_episodes = 0
        while recorded_episodes < args.num_episodes and not events["stop_recording"]:
            log_say(f"Recording episode {dataset.num_episodes}", args.play_sounds)
            record_loop(
                robot=robot,
                teleop=teleop,
                events=events,
                fps=args.fps,
                dataset=dataset,
                control_time_s=args.episode_time_s,
                single_task=args.single_task,
                display_data=args.display_data,
            )

            # Execute a few seconds without recording to give time to manually reset the environment
            # Skip reset for the last episode to be recorded
            if not events["stop_recording"] and (
                (recorded_episodes < args.num_episodes - 1) or events["rerecord_episode"]
            ):
                log_say("Reset the environment", args.play_sounds)
                record_loop(
                    robot=robot,
                    teleop=teleop,
                    events=events,
                    fps=args.fps,
                    control_time_s=args.reset_time_s,
                    single_task=args.single_task,
                    display_data=args.display_data,
                )

            if events["rerecord_episode"]:
                log_say("Re-record episode", args.play_sounds)
                events["rerecord_episode"] = False
                events["exit_early"] = False
                dataset.clear_episode_buffer()
                continue

            dataset.save_episode()
            recorded_episodes += 1

        log_say("Stop recording", args.play_sounds, blocking=True)

        if args.push_to_hub:
            dataset.push_to_hub(private=args.private)

        log_say("Exiting", args.play_sounds)

    except KeyboardInterrupt:
        logger.info("\nStopping recording...")
    except Exception as e:
        logger.error(f"Error during recording: {e}")
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
        
        if not is_headless() and listener is not None:
            try:
                listener.stop()
            except Exception as e:
                logger.warning(f"Error stopping keyboard listener: {e}")

        logger.info("Done.")


if __name__ == "__main__":
    main() 