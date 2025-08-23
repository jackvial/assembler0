#!/usr/bin/env python

from dataclasses import dataclass
from lerobot.teleoperators.config import TeleoperatorConfig


@TeleoperatorConfig.register_subclass("bi_koch_screwdriver_leader")
@dataclass
class BiKochScrewdriverLeaderConfig(TeleoperatorConfig):
    # Port configurations for each arm
    left_arm_port: str  # Screwdriver leader arm port
    right_arm_port: str  # Regular Koch leader arm port

    # Individual arm IDs for using existing calibrations
    left_arm_id: str | None = None  # If None, uses "{bimanual_id}_left"
    right_arm_id: str | None = None  # If None, uses "{bimanual_id}_right"

    # Left arm (screwdriver leader) specific options
    left_arm_gripper_open_pos: float = 50.0
    left_arm_haptic_range: float = 4.0

    # Right arm (regular Koch leader) specific options
    right_arm_gripper_open_pos: float = 50.0 