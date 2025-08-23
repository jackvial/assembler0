#!/usr/bin/env python

from dataclasses import dataclass
from lerobot.teleoperators.config import TeleoperatorConfig

@TeleoperatorConfig.register_subclass("my_koch_leader")
@dataclass
class KochLeaderConfig(TeleoperatorConfig):
    # Port to connect to the arm
    port: str

    # Sets the arm in torque mode with the gripper motor set to this value. This makes it possible to squeeze
    # the gripper and have it spring back to an open position on its own.
    gripper_open_pos: float = 50.0 