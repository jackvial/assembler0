# Based on LeRobot https://github.com/huggingface/lerobot/blob/main/src/lerobot/record.py
# Modified to be specific to the Assembler 0 robot and require less configuration.

"""
See scripts/record.py for example usage
"""

import logging
import time
import argparse
from pathlib import Path

logger = logging.getLogger(__name__)

from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.datasets.utils import build_dataset_frame, hw_to_dataset_features
from lerobot.datasets.image_writer import safe_stop_image_writer
from lerobot.utils.control_utils import (
    sanity_check_dataset_name,
    sanity_check_dataset_robot_compatibility,
)
from lerobot.utils.robot_utils import busy_wait
from lerobot.utils.utils import (
    init_logging,
    log_say,
)
from lerobot.utils.visualization_utils import _init_rerun, log_rerun_data

from assembler0_robot.robots.koch_screwdriver_follower import KochScrewdriverFollower
from assembler0_robot.robots.koch_screwdriver_follower import KochScrewdriverFollowerConfig
from assembler0_robot.teleoperators.koch_screwdriver_leader import KochScrewdriverLeader
from assembler0_robot.teleoperators.koch_screwdriver_leader import KochScrewdriverLeaderConfig


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
    parser = argparse.ArgumentParser(description="Record dataset with the screwdriver robot")
    
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
    parser.add_argument("--batch_encoding_size", type=int, default=1,
                       help="Number of episodes to accumulate before batch encoding videos. Set to 1 for immediate encoding (default), or higher for batched encoding")
    
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

    # Create robot config and instance
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
            batch_encoding_size=args.batch_encoding_size,
        )

    try:
        # Connect devices
        logger.info("Connecting robot...")
        robot.connect()
        logger.info("Connecting teleoperator...")
        teleop.connect()

        # try:
        #     listener, events = init_keyboard_listener()
        # except Exception as e:
            # logger.warning(f"Failed to initialize keyboard listener: {e}")
            # logger.warning("Recording will continue without keyboard shortcuts")
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

        # Handle any pending episodes that haven't been batch encoded yet
        if args.batch_encoding_size > 1 and hasattr(dataset, 'episodes_since_last_encoding') and dataset.episodes_since_last_encoding > 0:
            logger.info(f"Encoding remaining {dataset.episodes_since_last_encoding} episodes...")
            start_ep = dataset.num_episodes - dataset.episodes_since_last_encoding
            end_ep = dataset.num_episodes
            dataset.batch_encode_videos(start_ep, end_ep)
            dataset.episodes_since_last_encoding = 0

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
        
        # if not is_headless() and listener is not None:
        #     try:
        #         listener.stop()
        #     except Exception as e:
        #         logger.warning(f"Error stopping keyboard listener: {e}")

        logger.info("Done.")


if __name__ == "__main__":
    main() 