#!/usr/bin/env python

from dataclasses import dataclass, field

from lerobot.cameras import CameraConfig
from lerobot.robots.config import RobotConfig


@RobotConfig.register_subclass("bi_koch_screwdriver_follower")
@dataclass
class BiKochScrewdriverFollowerConfig(RobotConfig):
    # Port configurations for each arm
    left_arm_port: str  # Screwdriver arm port
    right_arm_port: str  # Regular Koch arm port

    # Individual arm IDs for using existing calibrations
    left_arm_id: str | None = None  # If None, uses "{bimanual_id}_left"
    right_arm_id: str | None = None  # If None, uses "{bimanual_id}_right"

    # Left arm (screwdriver) specific options
    left_arm_disable_torque_on_disconnect: bool = True
    left_arm_max_relative_target: int | None = None
    left_arm_use_degrees: bool = False
    left_arm_screwdriver_current_limit: int = 300
    left_arm_clutch_ratio: float = 0.5
    left_arm_clutch_cooldown_s: float = 1.0

    # Right arm (regular Koch) specific options  
    right_arm_disable_torque_on_disconnect: bool = True
    right_arm_max_relative_target: int | None = None
    right_arm_use_degrees: bool = False

    # Shared cameras
    cameras: dict[str, CameraConfig] = field(default_factory=dict) 