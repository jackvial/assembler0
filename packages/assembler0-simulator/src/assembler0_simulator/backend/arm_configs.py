"""Arm configuration definitions for different robot types."""

from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path


@dataclass
class JointMapping:
    """Mapping configuration for a single joint."""
    name: str
    control_axis: str  # 'left_x', 'left_y', 'right_x', 'right_y', 'triggers', 'bumpers', 'dpad_x', 'dpad_y'
    speed_multiplier: float = 1.0
    inverted: bool = False
    description: str = ""


@dataclass
class ArmConfig:
    """Configuration for a specific arm type."""
    id: str
    name: str
    description: str
    model_path: str  # Relative to simulator package
    joints: List[JointMapping]
    gripper_joint: Optional[str] = None
    gripper_open_position: float = 0.032
    gripper_close_position: float = -2.45
    default_camera: Dict = None
    
    def __post_init__(self):
        if self.default_camera is None:
            self.default_camera = {
                'lookat': [0.0, 0.07, 0.08],
                'distance': 0.8,
                'elevation': -30,
                'azimuth': 135
            }


# Define available arm configurations
ARM_CONFIGS = {
    'low_cost_5dof': ArmConfig(
        id='low_cost_5dof',
        name='Low Cost Robot (5DOF)',
        description='5 degree-of-freedom low cost robot arm',
        model_path='low_cost_robot/scene.xml',
        joints=[
            JointMapping(
                name='joint1',
                control_axis='left_x',
                speed_multiplier=1.0,
                description='Base rotation'
            ),
            JointMapping(
                name='joint2',
                control_axis='left_y',
                speed_multiplier=1.0,
                description='Shoulder pitch'
            ),
            JointMapping(
                name='joint3',
                control_axis='right_y',
                speed_multiplier=1.0,
                inverted=True,
                description='Elbow'
            ),
            JointMapping(
                name='joint4',
                control_axis='right_x',
                speed_multiplier=1.0,
                description='Wrist rotation'
            ),
        ],
        gripper_joint='joint5',
        gripper_open_position=0.032,
        gripper_close_position=-2.45,
    ),
    
    'low_cost_6dof': ArmConfig(
        id='low_cost_6dof',
        name='Low Cost Robot (6DOF)',
        description='6 degree-of-freedom low cost robot arm with extra wrist joint',
        model_path='low_cost_robot_6dof/scene.xml',
        joints=[
            JointMapping(
                name='joint1',
                control_axis='left_x',
                speed_multiplier=1.0,
                description='Base rotation'
            ),
            JointMapping(
                name='joint2',
                control_axis='left_y',
                speed_multiplier=1.0,
                description='Shoulder pitch'
            ),
            JointMapping(
                name='joint3',
                control_axis='right_y',
                speed_multiplier=1.0,
                inverted=True,
                description='Elbow'
            ),
            JointMapping(
                name='joint4',
                control_axis='right_x',
                speed_multiplier=1.0,
                description='Wrist pitch'
            ),
            JointMapping(
                name='joint5',
                control_axis='dpad_x',  # D-pad left/right for wrist roll
                speed_multiplier=0.5,
                description='Wrist roll'
            ),
        ],
        gripper_joint='joint6',
        gripper_open_position=0.032,
        gripper_close_position=-2.45,
        default_camera={
            'lookat': [0.0, 0.07, 0.08],
            'distance': 0.9,
            'elevation': -25,
            'azimuth': 135
        }
    ),
    
    'low_cost_6dof_screwdriver': ArmConfig(
        id='low_cost_6dof_screwdriver',
        name='Low Cost Robot 6DOF Screwdriver',
        description='6 degree-of-freedom low cost robot arm with screwdriver and camera mount',
        model_path='low_cost_robot_6dof_screwdriver/scene.xml',
        joints=[
            JointMapping(
                name='joint1',
                control_axis='left_x',
                speed_multiplier=1.0,
                description='Base rotation'
            ),
            JointMapping(
                name='joint2',
                control_axis='left_y',
                speed_multiplier=1.0,
                description='Shoulder pitch'
            ),
            JointMapping(
                name='joint3',
                control_axis='right_y',
                speed_multiplier=1.0,
                inverted=True,
                description='Elbow'
            ),
            JointMapping(
                name='joint4',
                control_axis='right_x',
                speed_multiplier=1.0,
                description='Wrist pitch'
            ),
            JointMapping(
                name='joint5',
                control_axis='dpad_x',
                speed_multiplier=0.5,
                description='Wrist roll'
            ),
            JointMapping(
                name='joint6',
                control_axis='triggers',  # L2/R2 for CCW/CW rotation
                speed_multiplier=2.0,  # Higher speed for drill rotation
                description='Screwdriver rotation'
            ),
        ],
        gripper_joint='joint6',  # Treat joint6 as special control for triggers
        default_camera={
            'lookat': [0.0, 0.07, 0.08],
            'distance': 0.9,
            'elevation': -25,
            'azimuth': 135
        }
    ),
    
    'assembler0_dual_arm': ArmConfig(
        id='assembler0_dual_arm',
        name='Assembler0 Dual Arm',
        description='Dual-arm configuration with screwdriver (left) and gripper (right) arms',
        model_path='assembler0/scene.xml',
        joints=[
            # Screwdriver arm joints (left side, controlled by default)
            JointMapping(
                name='s_joint1',
                control_axis='left_x',
                speed_multiplier=1.0,
                description='Screwdriver base rotation'
            ),
            JointMapping(
                name='s_joint2',
                control_axis='left_y',
                speed_multiplier=1.0,
                description='Screwdriver shoulder pitch'
            ),
            JointMapping(
                name='s_joint3',
                control_axis='right_y',
                speed_multiplier=1.0,
                inverted=True,
                description='Screwdriver elbow'
            ),
            JointMapping(
                name='s_joint4',
                control_axis='right_x',
                speed_multiplier=1.0,
                description='Screwdriver wrist pitch'
            ),
            JointMapping(
                name='s_joint5',
                control_axis='dpad_x',
                speed_multiplier=0.5,
                description='Screwdriver wrist roll'
            ),
            JointMapping(
                name='s_joint6',
                control_axis='triggers',
                speed_multiplier=2.0,
                description='Screwdriver rotation'
            ),
        ],
        gripper_joint='s_joint6',  # Treat screwdriver joint6 as special control
        default_camera={
            'lookat': [0.0, 0.0, 0.15],
            'distance': 1.2,
            'elevation': -20,
            'azimuth': 140
        }
    ),
}


def get_arm_config(config_id: str) -> Optional[ArmConfig]:
    """Get arm configuration by ID."""
    return ARM_CONFIGS.get(config_id)


def get_available_arms() -> List[Dict]:
    """Get list of available arm configurations for frontend."""
    return [
        {
            'id': config.id,
            'name': config.name,
            'description': config.description,
            'dof': len(config.joints) + (1 if config.gripper_joint else 0)
        }
        for config in ARM_CONFIGS.values()
    ]