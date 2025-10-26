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
import math
import time
from pathlib import Path

import numpy as np
from lerobot.utils.robot_utils import busy_wait

from assembler0_robot.robots.so101_follower import SO101Follower, SO101FollowerConfig
from kinematics_so101 import SO101Kinematics

logger = logging.getLogger(__name__)


# Define default waypoints for demonstration
# Each waypoint is a dictionary of motor positions
DEFAULT_WAYPOINTS = [
    # Home position
    {
        "shoulder_pan.pos": 32.07,
        "shoulder_lift.pos": 15.80,
        "elbow_flex.pos": 36.56,
        "wrist_flex.pos": 58.13,
        "wrist_roll.pos": -12.93,
        "gripper.pos": 3.88,
    },
    {
        "shoulder_pan.pos": 59.54,
        "shoulder_lift.pos": 23.21,
        "elbow_flex.pos": 27.68,
        "wrist_flex.pos": 58.38,
        "wrist_roll.pos": 4.90,
        "gripper.pos": 3.88,
    },
    {
        "shoulder_pan.pos": 55.89,
        "shoulder_lift.pos": -2.72,
        "elbow_flex.pos": 56.02,
        "wrist_flex.pos": 57.46,
        "wrist_roll.pos": 1.58,
        "gripper.pos": 3.88,
    },
    
    # Back to home position
    {
        "shoulder_pan.pos": 32.07,
        "shoulder_lift.pos": 15.80,
        "elbow_flex.pos": 36.56,
        "wrist_flex.pos": 58.13,
        "wrist_roll.pos": -12.93,
        "gripper.pos": 3.88,
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


def generate_constant_speed_trajectory(
    waypoints: list[dict[str, float]],
    fps: int,
    speed_deg_s: float,
    accel_deg_s2: float,
    blend_ms: int,
) -> list[dict[str, float]]:
    """Generate a smooth constant-speed trajectory through waypoints.
    
    Uses joint-space constant speed with S-curve ramps at start/end and
    corner blending around intermediate waypoints for smooth motion suitable
    for 3D printing applications.
    
    Args:
        waypoints: List of waypoint dictionaries with motor positions
        fps: Control loop frequency in Hz
        speed_deg_s: Target joint-space speed in degrees/second
        accel_deg_s2: Max joint-space acceleration for ramps in degrees/second^2
        blend_ms: Corner blending horizon around waypoints in milliseconds
        
    Returns:
        List of interpolated waypoint dictionaries at fps frequency
    """
    if len(waypoints) == 0:
        return []
    
    if len(waypoints) == 1:
        # Single waypoint - just hold position for 2 seconds
        return [waypoints[0].copy() for _ in range(int(2 * fps))]
    
    # Validate parameters
    if fps <= 0:
        raise ValueError(f"fps must be positive, got {fps}")
    if speed_deg_s <= 0:
        raise ValueError(f"speed_deg_s must be positive, got {speed_deg_s}")
    if accel_deg_s2 <= 0:
        raise ValueError(f"accel_deg_s2 must be positive, got {accel_deg_s2}")
    
    dt = 1.0 / fps
    blend_time = blend_ms / 1000.0  # Convert to seconds
    
    # Step 1: Normalize waypoints - get all joint names and ensure all waypoints have them
    all_joint_names = set()
    for wp in waypoints:
        all_joint_names.update(wp.keys())
    joint_names = sorted(all_joint_names)
    
    # Convert waypoints to numpy arrays, carrying forward missing values
    waypoint_arrays = []
    for i, wp in enumerate(waypoints):
        if i == 0:
            # First waypoint must have all joints
            arr = np.array([wp.get(name, 0.0) for name in joint_names])
        else:
            # Carry forward from previous waypoint if joint not specified
            arr = np.array([wp.get(name, waypoint_arrays[-1][j]) 
                          for j, name in enumerate(joint_names)])
        waypoint_arrays.append(arr)
    
    # Step 2: Compute segment distances and cumulative arc length
    segment_distances = []
    for i in range(len(waypoint_arrays) - 1):
        delta = waypoint_arrays[i + 1] - waypoint_arrays[i]
        distance = np.linalg.norm(delta)
        segment_distances.append(distance)
    
    total_distance = sum(segment_distances)
    
    if total_distance == 0:
        # All waypoints are identical - just hold position
        return [waypoints[0].copy() for _ in range(int(2 * fps))]
    
    # Step 3: Build time law with S-curve ramps
    # Calculate ramp parameters
    ramp_time = speed_deg_s / accel_deg_s2  # Time to reach target speed
    ramp_distance = 0.5 * accel_deg_s2 * ramp_time ** 2  # Distance covered during ramp
    
    # Ensure we have enough distance for both ramps
    if 2 * ramp_distance >= total_distance:
        # Path too short for full ramps - use triangular profile
        ramp_time = math.sqrt(total_distance / accel_deg_s2)
        ramp_distance = total_distance / 2
        cruise_distance = 0
        cruise_time = 0
    else:
        cruise_distance = total_distance - 2 * ramp_distance
        cruise_time = cruise_distance / speed_deg_s
    
    total_time = 2 * ramp_time + cruise_time
    num_samples = max(2, int(total_time * fps))
    
    logger.debug(f"Trajectory: distance={total_distance:.2f}°, time={total_time:.2f}s, "
                f"ramp_time={ramp_time:.2f}s, cruise_time={cruise_time:.2f}s")
    
    # Step 4: Generate trajectory samples
    trajectory = []
    
    for sample_idx in range(num_samples):
        t = sample_idx * dt
        
        # Compute current arc length position using S-curve profile
        if t <= ramp_time:
            # Acceleration phase (S-curve)
            s_normalized = t / ramp_time
            # Use sine-based S-curve for smooth acceleration
            s = ramp_distance * (s_normalized - math.sin(2 * math.pi * s_normalized) / (2 * math.pi))
        elif t <= ramp_time + cruise_time:
            # Cruise phase (constant speed)
            s = ramp_distance + speed_deg_s * (t - ramp_time)
        else:
            # Deceleration phase (S-curve)
            t_decel = t - ramp_time - cruise_time
            s_normalized = t_decel / ramp_time
            s = (ramp_distance + cruise_distance + 
                 ramp_distance * (s_normalized - math.sin(2 * math.pi * s_normalized) / (2 * math.pi)))
        
        # Clamp to total distance
        s = min(s, total_distance)
        
        # Find which segment we're in
        cumulative = 0
        segment_idx = 0
        for i, dist in enumerate(segment_distances):
            if cumulative + dist >= s:
                segment_idx = i
                break
            cumulative += dist
        else:
            # We're at or past the last waypoint
            segment_idx = len(segment_distances) - 1
            cumulative = sum(segment_distances[:-1])
        
        # Interpolate within segment
        segment_progress = (s - cumulative) / max(segment_distances[segment_idx], 1e-9)
        segment_progress = np.clip(segment_progress, 0.0, 1.0)
        
        start_pos = waypoint_arrays[segment_idx]
        end_pos = waypoint_arrays[segment_idx + 1]
        current_pos = start_pos + segment_progress * (end_pos - start_pos)
        
        # Step 5: Apply corner blending at waypoints (except first and last)
        # This smooths acceleration discontinuities
        if blend_time > 0 and len(waypoint_arrays) > 2:
            for wp_idx in range(1, len(waypoint_arrays) - 1):
                # Calculate time when we reach this waypoint
                wp_distance = sum(segment_distances[:wp_idx])
                
                if wp_distance <= ramp_distance:
                    wp_time = ramp_time * math.sqrt(wp_distance / ramp_distance) if ramp_distance > 0 else 0
                elif wp_distance <= ramp_distance + cruise_distance:
                    wp_time = ramp_time + (wp_distance - ramp_distance) / speed_deg_s
                else:
                    remaining = wp_distance - ramp_distance - cruise_distance
                    wp_time = ramp_time + cruise_time + ramp_time * math.sqrt(remaining / ramp_distance) if ramp_distance > 0 else ramp_time + cruise_time
                
                # Check if we're within blend window
                time_diff = abs(t - wp_time)
                if time_diff < blend_time:
                    # Apply cosine blending
                    blend_factor = 0.5 * (1 + math.cos(math.pi * time_diff / blend_time))
                    # Blend towards the waypoint position
                    wp_pos = waypoint_arrays[wp_idx]
                    current_pos = current_pos * (1 - 0.3 * blend_factor) + wp_pos * (0.3 * blend_factor)
        
        # Convert back to dictionary
        waypoint_dict = {name: float(current_pos[i]) for i, name in enumerate(joint_names)}
        trajectory.append(waypoint_dict)
    
    return trajectory


def generate_cartesian_trajectory(
    waypoints: list[dict[str, float]],
    fps: int,
    speed_mm_s: float,
    accel_mm_s2: float,
    blend_ms: int = 0,
    urdf_path: str = "urdf/so101_follower.urdf",
    orientation_mode: str = "fixed",
    lock_wrist: bool = True,
) -> list[dict[str, float]]:
    """Generate a Cartesian straight-line trajectory through waypoints using IK.
    
    This ensures the end-effector moves in true straight lines in 3D space,
    essential for 3D printing applications.
    
    Args:
        waypoints: List of waypoint dictionaries with joint positions (degrees)
        fps: Control loop frequency in Hz
        speed_mm_s: Target Cartesian speed in millimeters/second
        accel_mm_s2: Max Cartesian acceleration in mm/s²
        blend_ms: Corner blending (not yet implemented for Cartesian)
        urdf_path: Path to robot URDF file
        orientation_mode: "fixed" (maintain initial orientation) or "interpolate"
        lock_wrist: If True, lock wrist joints to keep gripper facing forward
        
    Returns:
        List of joint-space waypoint dictionaries at fps frequency
    """
    if len(waypoints) == 0:
        return []
    
    if len(waypoints) == 1:
        # Single waypoint - just hold position for 2 seconds
        return [waypoints[0].copy() for _ in range(int(2 * fps))]
    
    # Validate parameters
    if fps <= 0:
        raise ValueError(f"fps must be positive, got {fps}")
    if speed_mm_s <= 0:
        raise ValueError(f"speed_mm_s must be positive, got {speed_mm_s}")
    if accel_mm_s2 <= 0:
        raise ValueError(f"accel_mm_s2 must be positive, got {accel_mm_s2}")
    
    # Initialize kinematics
    kin = SO101Kinematics(Path(urdf_path))
    
    # Convert waypoints to Cartesian poses using FK
    # First, strip .pos suffix from waypoint keys
    cartesian_waypoints = []
    joint_waypoints = []
    for wp in waypoints:
        # Convert "joint.pos": value to "joint": value for FK
        joint_dict = {}
        for key, value in wp.items():
            joint_name = key.replace(".pos", "")
            joint_dict[joint_name] = value
        joint_waypoints.append(joint_dict)
        
        pos, ori = kin.forward_kinematics(joint_dict)
        cartesian_waypoints.append({"position": pos, "orientation": ori})
    
    logger.info(f"Converted {len(waypoints)} joint waypoints to Cartesian poses")
    
    # Compute segment distances in Cartesian space (meters)
    segment_distances = []
    for i in range(len(cartesian_waypoints) - 1):
        pos1 = cartesian_waypoints[i]["position"]
        pos2 = cartesian_waypoints[i + 1]["position"]
        distance = np.linalg.norm(pos2 - pos1)
        segment_distances.append(distance)
    
    total_distance = sum(segment_distances)  # meters
    
    if total_distance < 1e-6:
        # All waypoints are at same position
        return [waypoints[0].copy() for _ in range(int(2 * fps))]
    
    logger.debug(f"Total Cartesian distance: {total_distance*1000:.1f}mm")
    
    # Convert speed from mm/s to m/s
    speed_m_s = speed_mm_s / 1000.0
    accel_m_s2 = accel_mm_s2 / 1000.0
    
    # Calculate S-curve velocity profile parameters
    ramp_time = speed_m_s / accel_m_s2
    ramp_distance = 0.5 * accel_m_s2 * ramp_time ** 2
    
    # Adjust if path too short for full ramps
    if 2 * ramp_distance >= total_distance:
        # Triangular profile
        ramp_time = math.sqrt(total_distance / accel_m_s2)
        ramp_distance = total_distance / 2
        cruise_distance = 0
        cruise_time = 0
    else:
        cruise_distance = total_distance - 2 * ramp_distance
        cruise_time = cruise_distance / speed_m_s
    
    total_time = 2 * ramp_time + cruise_time
    num_samples = max(2, int(total_time * fps))
    dt = 1.0 / fps
    
    logger.info(f"Cartesian trajectory: {total_distance*1000:.1f}mm in {total_time:.2f}s "
                f"(ramp: {ramp_time:.2f}s, cruise: {cruise_time:.2f}s)")
    
    # Generate Cartesian trajectory samples
    trajectory = []
    previous_joint_solution = joint_waypoints[0]  # Warm start IK (without .pos suffix)
    
    # Store initial wrist angles to keep gripper facing forward
    initial_wrist_flex = joint_waypoints[0].get("wrist_flex", 0)
    initial_wrist_roll = joint_waypoints[0].get("wrist_roll", 0)
    
    for sample_idx in range(num_samples):
        t = sample_idx * dt
        
        # Compute arc length using S-curve profile
        if t <= ramp_time:
            # Acceleration phase
            s_normalized = t / ramp_time
            s = ramp_distance * (s_normalized - math.sin(2 * math.pi * s_normalized) / (2 * math.pi))
        elif t <= ramp_time + cruise_time:
            # Cruise phase
            s = ramp_distance + speed_m_s * (t - ramp_time)
        else:
            # Deceleration phase
            t_decel = t - ramp_time - cruise_time
            s_normalized = t_decel / ramp_time
            s = (ramp_distance + cruise_distance + 
                 ramp_distance * (s_normalized - math.sin(2 * math.pi * s_normalized) / (2 * math.pi)))
        
        s = min(s, total_distance)
        
        # Find which segment we're in
        cumulative = 0
        segment_idx = 0
        for i, dist in enumerate(segment_distances):
            if cumulative + dist >= s:
                segment_idx = i
                break
            cumulative += dist
        else:
            segment_idx = len(segment_distances) - 1
            cumulative = sum(segment_distances[:-1])
        
        # Interpolate Cartesian position within segment
        segment_progress = (s - cumulative) / max(segment_distances[segment_idx], 1e-9)
        segment_progress = np.clip(segment_progress, 0.0, 1.0)
        
        start_cart = cartesian_waypoints[segment_idx]
        end_cart = cartesian_waypoints[segment_idx + 1]
        
        # Linear interpolation in Cartesian space
        current_pos = start_cart["position"] + segment_progress * (end_cart["position"] - start_cart["position"])
        
        # Handle orientation based on mode
        # NOTE: Orientation-constrained IK with ikpy is unreliable, so we use position-only
        # The warm-start (previous solution) helps reduce oscillation
        target_orientation = None  # Position-only IK
        
        # Solve IK for current Cartesian target
        joint_solution = kin.inverse_kinematics(
            current_pos,
            target_orientation=target_orientation,
            initial_joint_angles_deg=previous_joint_solution
        )
        
        if joint_solution is None:
            logger.warning(f"IK failed at sample {sample_idx}/{num_samples}, using previous solution")
            joint_solution = previous_joint_solution
        else:
            # Override wrist joints if lock_wrist is enabled
            if lock_wrist:
                # Keep gripper facing forward by locking wrist joints
                joint_solution["wrist_flex"] = initial_wrist_flex
                joint_solution["wrist_roll"] = initial_wrist_roll
            previous_joint_solution = joint_solution
        
        # Add gripper value from waypoints (pass through unchanged)
        if "gripper" in joint_waypoints[0] and "gripper" not in joint_solution:
            # Interpolate gripper based on segment
            gripper_start = joint_waypoints[segment_idx].get("gripper", 0)
            gripper_end = joint_waypoints[segment_idx + 1].get("gripper", 0)
            joint_solution["gripper"] = gripper_start + segment_progress * (gripper_end - gripper_start)
        
        # Convert to action format (add .pos suffix back)
        # Ensure all values are plain Python floats
        action = {f"{joint}.pos": float(joint_solution[joint]) for joint in joint_solution}
        trajectory.append(action)
    
    logger.info(f"Generated {len(trajectory)} Cartesian trajectory samples")
    return trajectory


def move_through_waypoints(
    robot: SO101Follower,
    waypoints: list[dict[str, float]],
    fps: int = 30,
    wait_time_s: float = 2.0,
    speed_deg_s: float = 5.0,
    accel_deg_s2: float = 25.0,
    blend_ms: int = 80,
    use_smooth_trajectory: bool = True,
    cartesian_mode: bool = False,
    speed_mm_s: float = 20.0,
    accel_mm_s2: float = 100.0,
    orientation_mode: str = "fixed",
) -> None:
    """Move robot through a sequence of waypoints.
    
    Args:
        robot: Connected SO101Follower instance
        waypoints: List of waypoint dictionaries with motor positions
        fps: Control loop frequency in Hz
        wait_time_s: Time to wait at each waypoint before moving to next (legacy mode only)
        speed_deg_s: Target joint-space speed in degrees/second (joint-space mode)
        accel_deg_s2: Max joint-space acceleration for ramps (joint-space mode)
        blend_ms: Corner blending horizon around waypoints in milliseconds
        use_smooth_trajectory: If True, use smooth trajectory; if False, use legacy mode
        cartesian_mode: If True, use Cartesian straight-line interpolation with IK
        speed_mm_s: Target Cartesian speed in mm/s (Cartesian mode only)
        accel_mm_s2: Max Cartesian acceleration in mm/s² (Cartesian mode only)
        orientation_mode: "fixed" or "interpolate" (Cartesian mode only)
    """
    logger.info(f"Starting waypoint sequence with {len(waypoints)} waypoints")
    
    if cartesian_mode and len(waypoints) > 1:
        # Cartesian mode: straight lines in 3D space
        logger.info(f"Generating Cartesian trajectory (speed={speed_mm_s}mm/s, accel={accel_mm_s2}mm/s², lock_wrist=True)")
        trajectory = generate_cartesian_trajectory(
            waypoints=waypoints,
            fps=fps,
            speed_mm_s=speed_mm_s,
            accel_mm_s2=accel_mm_s2,
            blend_ms=blend_ms,
            orientation_mode=orientation_mode,
            lock_wrist=False,  # Keep gripper facing forward
        )
        
        logger.info(f"Trajectory generated: {len(trajectory)} steps ({len(trajectory)/fps:.2f}s)")
        
        # Stream trajectory
        for i, action in enumerate(trajectory):
            loop_start = time.perf_counter()
            
            # Send action to robot
            robot.send_action(action)
            
            # Maintain control loop timing with safety guard
            dt_s = time.perf_counter() - loop_start
            wait_time = 1 / fps - dt_s
            if wait_time > 0:
                busy_wait(wait_time)
            else:
                logger.warning(f"Control loop running slow: {dt_s*1000:.1f}ms > {1000/fps:.1f}ms target")
            
            # Progress logging every second
            if i % fps == 0:
                logger.debug(f"Progress: {i}/{len(trajectory)} ({100*i/len(trajectory):.1f}%)")
        
        logger.info("Cartesian trajectory completed!")
    elif use_smooth_trajectory and len(waypoints) > 1:
        # Generate smooth trajectory
        logger.info(f"Generating smooth trajectory (speed={speed_deg_s}°/s, accel={accel_deg_s2}°/s², blend={blend_ms}ms)")
        trajectory = generate_constant_speed_trajectory(
            waypoints=waypoints,
            fps=fps,
            speed_deg_s=speed_deg_s,
            accel_deg_s2=accel_deg_s2,
            blend_ms=blend_ms,
        )
        
        logger.info(f"Trajectory generated: {len(trajectory)} steps ({len(trajectory)/fps:.2f}s)")
        
        # Stream trajectory
        for i, action in enumerate(trajectory):
            loop_start = time.perf_counter()
            
            # Send action to robot
            robot.send_action(action)
            
            # Maintain control loop timing with safety guard
            dt_s = time.perf_counter() - loop_start
            wait_time = 1 / fps - dt_s
            if wait_time > 0:
                busy_wait(wait_time)
            else:
                logger.warning(f"Control loop running slow: {dt_s*1000:.1f}ms > {1000/fps:.1f}ms target")
            
            # Progress logging every second
            if i % fps == 0:
                logger.debug(f"Progress: {i}/{len(trajectory)} ({100*i/len(trajectory):.1f}%)")
        
        logger.info("Smooth trajectory completed!")
    else:
        # Legacy mode: stop at each waypoint
        logger.info("Using legacy mode (stop at each waypoint)")
        
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
                
                # Maintain control loop timing with safety guard
                dt_s = time.perf_counter() - loop_start
                wait_time = 1 / fps - dt_s
                if wait_time > 0:
                    busy_wait(wait_time)
            
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
        help="Control loop frequency in Hz (default: 30, recommend 50 for smooth trajectory)",
    )
    parser.add_argument(
        "--speed_deg_s",
        type=float,
        default=5.0,
        help="Target joint-space speed in degrees/second (default: 5.0)",
    )
    parser.add_argument(
        "--accel_deg_s2",
        type=float,
        default=25.0,
        help="Max joint-space acceleration for ramps in degrees/second^2 (default: 25.0)",
    )
    parser.add_argument(
        "--blend_ms",
        type=int,
        default=80,
        help="Corner blending horizon around waypoints in milliseconds (default: 80)",
    )
    
    # Cartesian mode parameters
    parser.add_argument(
        "--cartesian_mode",
        action="store_true",
        help="Use Cartesian straight-line interpolation (straight lines in 3D space)",
    )
    parser.add_argument(
        "--speed_mm_s",
        type=float,
        default=20.0,
        help="Cartesian speed in mm/s (default: 20.0, for --cartesian_mode)",
    )
    parser.add_argument(
        "--accel_mm_s2",
        type=float,
        default=100.0,
        help="Cartesian acceleration in mm/s² (default: 100.0, for --cartesian_mode)",
    )
    parser.add_argument(
        "--orientation_mode",
        type=str,
        choices=["fixed", "interpolate"],
        default="fixed",
        help="Orientation handling: 'fixed' (maintain initial) or 'interpolate' (for --cartesian_mode)",
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
            speed_deg_s=args.speed_deg_s,
            accel_deg_s2=args.accel_deg_s2,
            blend_ms=args.blend_ms,
            use_smooth_trajectory=True,
            cartesian_mode=args.cartesian_mode,
            speed_mm_s=args.speed_mm_s,
            accel_mm_s2=args.accel_mm_s2,
            orientation_mode=args.orientation_mode,
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

