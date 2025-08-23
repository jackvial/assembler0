#!/usr/bin/env python

import logging
import time
from functools import cached_property
from typing import Any

from lerobot.cameras.utils import make_cameras_from_configs
from lerobot.robots.robot import Robot

from ..koch_screwdriver_follower import KochScrewdriverFollower, KochScrewdriverFollowerConfig
from ..koch_follower import KochFollower, KochFollowerConfig
from .config_bi_koch_screwdriver_follower import BiKochScrewdriverFollowerConfig

logger = logging.getLogger(__name__)


class BiKochScrewdriverFollower(Robot):
    """
    Bimanual Koch robot with screwdriver left arm and regular Koch right arm.
    - Left arm: Koch screwdriver follower with velocity-controlled screwdriver motor
    - Right arm: Regular Koch follower with gripper
    """

    config_class = BiKochScrewdriverFollowerConfig
    name = "bi_koch_screwdriver_follower"

    def __init__(self, config: BiKochScrewdriverFollowerConfig):
        super().__init__(config)
        self.config = config

        # Configure left arm (screwdriver)
        left_arm_id = config.left_arm_id or (f"{config.id}_left" if config.id else None)
        left_arm_config = KochScrewdriverFollowerConfig(
            id=left_arm_id,
            calibration_dir=config.calibration_dir,
            port=config.left_arm_port,
            disable_torque_on_disconnect=config.left_arm_disable_torque_on_disconnect,
            max_relative_target=config.left_arm_max_relative_target,
            use_degrees=config.left_arm_use_degrees,
            screwdriver_current_limit=config.left_arm_screwdriver_current_limit,
            clutch_ratio=config.left_arm_clutch_ratio,
            clutch_cooldown_s=config.left_arm_clutch_cooldown_s,
            cameras={},
        )

        # Configure right arm (regular Koch)
        right_arm_id = config.right_arm_id or (f"{config.id}_right" if config.id else None)
        right_arm_config = KochFollowerConfig(
            id=right_arm_id,
            calibration_dir=config.calibration_dir,
            port=config.right_arm_port,
            disable_torque_on_disconnect=config.right_arm_disable_torque_on_disconnect,
            max_relative_target=config.right_arm_max_relative_target,
            use_degrees=config.right_arm_use_degrees,
            cameras={},
        )

        self.left_arm = KochScrewdriverFollower(left_arm_config)
        self.right_arm = KochFollower(right_arm_config)
        self.cameras = make_cameras_from_configs(config.cameras)

    @property
    def _motors_ft(self) -> dict[str, type]:
        # Left arm has .vel for screwdriver, .pos for others
        left_features = {f"left_{motor}.vel" if motor == "screwdriver" else f"left_{motor}.pos": float 
                        for motor in self.left_arm.bus.motors}
        # Right arm has .pos for all motors
        right_features = {f"right_{motor}.pos": float for motor in self.right_arm.bus.motors}
        return {**left_features, **right_features}

    @property
    def _cameras_ft(self) -> dict[str, tuple]:
        return {
            cam: (self.config.cameras[cam].height, self.config.cameras[cam].width, 3) for cam in self.cameras
        }

    @cached_property
    def observation_features(self) -> dict[str, type | tuple]:
        return {**self._motors_ft, **self._cameras_ft}

    @cached_property
    def action_features(self) -> dict[str, type]:
        return self._motors_ft

    @property
    def is_connected(self) -> bool:
        return (
            self.left_arm.bus.is_connected
            and self.right_arm.bus.is_connected
            and all(cam.is_connected for cam in self.cameras.values())
        )

    def connect(self, calibrate: bool = True) -> None:
        # If using existing individual calibrations, skip calibration during connect
        skip_calibration = (self.config.left_arm_id is not None and self.config.right_arm_id is not None)
        connect_calibrate = calibrate and not skip_calibration
        
        self.left_arm.connect(connect_calibrate)
        self.right_arm.connect(connect_calibrate)

        for cam in self.cameras.values():
            cam.connect()

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

    def get_observation(self) -> dict[str, Any]:
        obs_dict = {}

        # Add "left_" prefix to left arm observations
        left_obs = self.left_arm.get_observation()
        obs_dict.update({f"left_{key}": value for key, value in left_obs.items()})

        # Add "right_" prefix to right arm observations
        right_obs = self.right_arm.get_observation()
        obs_dict.update({f"right_{key}": value for key, value in right_obs.items()})

        # Add camera observations
        for cam_key, cam in self.cameras.items():
            start = time.perf_counter()
            obs_dict[cam_key] = cam.async_read()
            dt_ms = (time.perf_counter() - start) * 1e3
            logger.debug(f"{self} read {cam_key}: {dt_ms:.1f}ms")

        return obs_dict

    def send_action(self, action: dict[str, Any]) -> dict[str, Any]:
        # Remove "left_" prefix for left arm actions
        left_action = {
            key.removeprefix("left_"): value for key, value in action.items() if key.startswith("left_")
        }
        # Remove "right_" prefix for right arm actions
        right_action = {
            key.removeprefix("right_"): value for key, value in action.items() if key.startswith("right_")
        }

        send_action_left = self.left_arm.send_action(left_action)
        send_action_right = self.right_arm.send_action(right_action)

        # Add prefixes back to returned actions
        prefixed_send_action_left = {f"left_{key}": value for key, value in send_action_left.items()}
        prefixed_send_action_right = {f"right_{key}": value for key, value in send_action_right.items()}

        return {**prefixed_send_action_left, **prefixed_send_action_right}

    def get_feedback(self) -> dict[str, float]:
        """Return haptic feedback from the left arm (screwdriver) for the leader."""
        left_feedback = self.left_arm.get_feedback()
        # Add left_ prefix to feedback
        return {f"left_{key}": value for key, value in left_feedback.items()}

    def disconnect(self):
        self.left_arm.disconnect()
        self.right_arm.disconnect()

        for cam in self.cameras.values():
            cam.disconnect() 