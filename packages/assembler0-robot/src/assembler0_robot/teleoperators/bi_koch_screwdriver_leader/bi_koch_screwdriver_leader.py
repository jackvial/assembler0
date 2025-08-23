#!/usr/bin/env python

import logging
from functools import cached_property

from lerobot.teleoperators.teleoperator import Teleoperator

from ..koch_screwdriver_leader import KochScrewdriverLeader, KochScrewdriverLeaderConfig
from ..koch_leader import KochLeader, KochLeaderConfig
from .config_bi_koch_screwdriver_leader import BiKochScrewdriverLeaderConfig

logger = logging.getLogger(__name__)


class BiKochScrewdriverLeader(Teleoperator):
    """
    Bimanual Koch teleoperator with screwdriver left arm and regular Koch right arm.
    - Left arm: Koch screwdriver leader that maps gripper position to screwdriver velocity
    - Right arm: Regular Koch leader with gripper
    """

    config_class = BiKochScrewdriverLeaderConfig
    name = "bi_koch_screwdriver_leader"

    def __init__(self, config: BiKochScrewdriverLeaderConfig):
        super().__init__(config)
        self.config = config

        # Configure left arm (screwdriver leader)
        left_arm_id = config.left_arm_id or (f"{config.id}_left" if config.id else None)
        left_arm_config = KochScrewdriverLeaderConfig(
            id=left_arm_id,
            calibration_dir=config.calibration_dir,
            port=config.left_arm_port,
            gripper_open_pos=config.left_arm_gripper_open_pos,
            haptic_range=config.left_arm_haptic_range,
        )

        # Configure right arm (regular Koch leader)
        right_arm_id = config.right_arm_id or (f"{config.id}_right" if config.id else None)
        right_arm_config = KochLeaderConfig(
            id=right_arm_id,
            calibration_dir=config.calibration_dir,
            port=config.right_arm_port,
            gripper_open_pos=config.right_arm_gripper_open_pos,
        )

        self.left_arm = KochScrewdriverLeader(left_arm_config)
        self.right_arm = KochLeader(right_arm_config)

    @cached_property
    def action_features(self) -> dict[str, type]:
        # Left arm has .vel for screwdriver, .pos for others
        left_features = {f"left_{motor}.vel" if motor == "screwdriver" else f"left_{motor}.pos": float 
                        for motor in self.left_arm.bus.motors}
        # Right arm has .pos for all motors
        right_features = {f"right_{motor}.pos": float for motor in self.right_arm.bus.motors}
        return {**left_features, **right_features}

    @cached_property
    def feedback_features(self) -> dict[str, type]:
        # Only left arm (screwdriver) supports haptic feedback
        return {"left_haptic": float}

    @property
    def is_connected(self) -> bool:
        return self.left_arm.is_connected and self.right_arm.is_connected

    def connect(self, calibrate: bool = True) -> None:
        # If using existing individual calibrations, skip calibration during connect
        skip_calibration = (self.config.left_arm_id is not None and self.config.right_arm_id is not None)
        connect_calibrate = calibrate and not skip_calibration
        
        self.left_arm.connect(connect_calibrate)
        self.right_arm.connect(connect_calibrate)

    @property
    def is_calibrated(self) -> bool:
        return self.left_arm.is_calibrated and self.right_arm.is_calibrated

    def calibrate(self) -> None:
        self.left_arm.calibrate()
        self.right_arm.calibrate()

    def configure(self) -> None:
        self.left_arm.configure()
        self.right_arm.configure()

    def setup_motors(self) -> None:
        self.left_arm.setup_motors()
        self.right_arm.setup_motors()

    def get_action(self) -> dict[str, float]:
        action_dict = {}

        # Add "left_" prefix to left arm actions
        left_action = self.left_arm.get_action()
        action_dict.update({f"left_{key}": value for key, value in left_action.items()})

        # Add "right_" prefix to right arm actions
        right_action = self.right_arm.get_action()
        action_dict.update({f"right_{key}": value for key, value in right_action.items()})

        return action_dict

    def send_feedback(self, feedback: dict[str, float]) -> None:
        # Remove "left_" prefix for left arm feedback
        left_feedback = {
            key.removeprefix("left_"): value for key, value in feedback.items() if key.startswith("left_")
        }
        # Remove "right_" prefix for right arm feedback (though right arm doesn't support feedback)
        right_feedback = {
            key.removeprefix("right_"): value for key, value in feedback.items() if key.startswith("right_")
        }

        if left_feedback:
            self.left_arm.send_feedback(left_feedback)
        # Note: Regular Koch leader doesn't implement send_feedback, so we skip right_feedback

    def disconnect(self) -> None:
        self.left_arm.disconnect()
        self.right_arm.disconnect() 