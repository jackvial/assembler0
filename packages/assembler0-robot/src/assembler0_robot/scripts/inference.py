# Based on LeRobot https://github.com/huggingface/lerobot/blob/main/src/lerobot/scripts/eval.py
# Modified to be specific to the Assembler 0 robot and require less configuration.

"""
See scripts/inference.py for example usage
"""

import time
import logging
import argparse

import torch

from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.policies.act.modeling_act import ACTPolicy
from lerobot.policies.diffusion.modeling_diffusion import DiffusionPolicy
from lerobot.policies.smolvla.modeling_smolvla import SmolVLAPolicy
from lerobot.utils.robot_utils import busy_wait

from assembler0_robot.robots.koch_screwdriver_follower import KochScrewdriverFollower
from assembler0_robot.robots.koch_screwdriver_follower import KochScrewdriverFollowerConfig


def main():
    parser = argparse.ArgumentParser(description="Run inference with screwdriver robot")
    
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
    
    # Camera configuration
    parser.add_argument("--screwdriver_camera", type=str, default="/dev/video0",
                       help="Path or index for screwdriver camera")
    parser.add_argument("--side_camera", type=str, default="/dev/video2",
                       help="Path or index for side camera")  
    parser.add_argument("--top_camera", type=str, default="/dev/video6",
                       help="Path or index for top camera")
    parser.add_argument("--camera_width", type=int, default=800,
                       help="Camera width")
    parser.add_argument("--camera_height", type=int, default=600,
                       help="Camera height") 
    parser.add_argument("--camera_fps", type=int, default=30,
                       help="Camera FPS")
    
    # Inference parameters
    parser.add_argument("--model_path", type=str, required=True,
                       help="Path to the trained model checkpoint")
    parser.add_argument("--duration", type=int, default=20,
                       help="Inference duration in seconds")
    parser.add_argument("--fps", type=int, default=30,
                       help="Control loop frequency")
    parser.add_argument("--device", type=str, default="cuda",
                       help="Device to run inference on (cuda, mps, cpu)")
    
    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        # Load the policy
        logger.info(f"Loading policy from {args.model_path}")
        policy = ACTPolicy.from_pretrained(args.model_path)
        # policy = DiffusionPolicy.from_pretrained(args.model_path)
        # policy = SmolVLAPolicy.from_pretrained(args.model_path)
        policy.to(args.device)
        
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
        
        # Connect robot
        logger.info("Connecting robot...")
        robot.connect()
        
        logger.info(f"Starting inference for {args.duration} seconds at {args.fps} FPS")
        
        total_steps = args.duration * args.fps
        
        for t in range(total_steps):
            start_time = time.perf_counter()

            # Read the follower state and access the frames from the cameras
            observation = robot.get_observation()

            # Convert to pytorch format: channel first and float32 in [0,1]
            # with batch dimension
            processed_observation = {}

            # Collect motor states in the correct order
            # Based on koch_screwdriver_follower, we have 5 position states + 1 velocity state
            state_values = []
            state_values.append(observation["shoulder_pan.pos"])
            state_values.append(observation["shoulder_lift.pos"])
            state_values.append(observation["elbow_flex.pos"])
            state_values.append(observation["wrist_flex.pos"])
            state_values.append(observation["wrist_roll.pos"])
            state_values.append(observation["screwdriver.vel"])

            # Combine into a single state tensor
            state_tensor = torch.tensor(state_values, dtype=torch.float32).unsqueeze(0)
            processed_observation["observation.state"] = state_tensor.to(args.device)

            # Process images
            for cam_name in ["screwdriver", "side", "top"]:
                if cam_name in observation:
                    # Convert numpy image to tensor: HWC -> CHW, normalize to [0,1]
                    image = torch.from_numpy(observation[cam_name]).float() / 255.0
                    image = image.permute(2, 0, 1).contiguous()
                    image = image.unsqueeze(0)  # Add batch dimension
                    processed_observation[f"observation.images.{cam_name}"] = image.to(args.device)
                    
            processed_observation["task"] = "Move towards the orange panel positioned on the left side of the black rectangular base. Align with the silver screw in the center hole of the orange panel. Place the screwdriver bit on the screw, and turn clockwise until the screw has been fully tightened into the pinewood block below. Once the screw has been tightened, report to the start position."

            # Compute the next action with the policy
            # based on the current observation
            action = policy.select_action(processed_observation)
            # Remove batch dimension
            action = action.squeeze(0)
            # Move to cpu, if not already the case
            action = action.to("cpu")

            # Convert action tensor to dictionary format expected by robot
            action_dict = {
                "shoulder_pan.pos": action[0].item(),
                "shoulder_lift.pos": action[1].item(),
                "elbow_flex.pos": action[2].item(),
                "wrist_flex.pos": action[3].item(),
                "wrist_roll.pos": action[4].item(),
                "screwdriver.vel": action[5].item(),
            }

            robot.send_action(action_dict)

            # Print progress every second
            if t % args.fps == 0:
                elapsed = t // args.fps
                logger.info(f"Step: {t}, Time: {elapsed}s / {args.duration}s")

            dt_s = time.perf_counter() - start_time
            busy_wait(1 / args.fps - dt_s)
            
        logger.info("Inference completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during inference: {e}")
        raise
    finally:
        logger.info("Disconnecting robot...")
        try:
            robot.disconnect()
        except Exception as e:
            logger.error(f"Error disconnecting robot: {e}")
        logger.info("Done.")


if __name__ == "__main__":
    main()