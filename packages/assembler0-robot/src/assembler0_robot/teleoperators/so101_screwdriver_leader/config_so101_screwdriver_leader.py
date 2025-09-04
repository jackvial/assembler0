from dataclasses import dataclass

from lerobot.teleoperators.config import TeleoperatorConfig


@TeleoperatorConfig.register_subclass("assembler0_so101_screwdriver_leader")
@dataclass
class SO101ScrewdriverLeaderConfig(TeleoperatorConfig):
    # Port to connect to the arm
    port: str

    use_degrees: bool = False

    gripper_open_pos: float = 50.0
