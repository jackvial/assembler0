#!/usr/bin/env python

"""
Kinematics module for SO101 robot arm.

Provides forward and inverse kinematics using the SO101 URDF file and ikpy library.
"""

import logging
from pathlib import Path
from typing import Optional

import ikpy.chain
import ikpy.link
import numpy as np

logger = logging.getLogger(__name__)

# Joint names in order (matching SO101Follower motor order)
JOINT_NAMES = [
    "shoulder_pan",
    "shoulder_lift",
    "elbow_flex",
    "wrist_flex",
    "wrist_roll",
    "gripper",
]

# URDF path relative to this file
URDF_PATH = Path(__file__).parent / "urdf" / "so101_follower.urdf"


class SO101Kinematics:
    """Kinematics solver for SO101 robot arm using ikpy."""
    
    def __init__(self, urdf_path: Optional[Path] = None):
        """Initialize kinematics chain from URDF.
        
        Args:
            urdf_path: Path to URDF file. If None, uses default SO101 URDF.
        """
        self.urdf_path = urdf_path or URDF_PATH
        
        if not self.urdf_path.exists():
            raise FileNotFoundError(f"URDF file not found: {self.urdf_path}")
        
        # Load kinematic chain from URDF
        # Let ikpy auto-detect the chain structure
        self.chain = ikpy.chain.Chain.from_urdf_file(
            str(self.urdf_path),
            base_elements=["base_link"],
        )
        
        logger.info(f"Loaded kinematic chain with {len(self.chain.links)} links")
        logger.debug(f"Active joints: {[link.name for link in self.chain.links if link.name]}")
    
    def forward_kinematics(
        self, 
        joint_angles_deg: dict[str, float],
        return_matrix: bool = False,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Compute forward kinematics: joint angles → end-effector pose.
        
        Args:
            joint_angles_deg: Dictionary mapping joint names to angles in degrees
            return_matrix: If True, return 4x4 transformation matrix instead of pos/ori
            
        Returns:
            If return_matrix=False: (position, orientation_matrix)
                position: [x, y, z] in meters
                orientation_matrix: 3x3 rotation matrix
            If return_matrix=True: 4x4 transformation matrix
        """
        # Convert to radians and ordered array
        joint_angles_rad = np.zeros(len(self.chain.links))
        for i, link in enumerate(self.chain.links):
            if link.name in joint_angles_deg:
                joint_angles_rad[i] = np.deg2rad(joint_angles_deg[link.name])
        
        # Compute forward kinematics
        transformation_matrix = self.chain.forward_kinematics(joint_angles_rad)
        
        if return_matrix:
            return transformation_matrix
        
        # Extract position and orientation
        position = transformation_matrix[:3, 3]
        orientation = transformation_matrix[:3, :3]
        
        return position, orientation
    
    def inverse_kinematics(
        self,
        target_position: np.ndarray,
        target_orientation: Optional[np.ndarray] = None,
        initial_joint_angles_deg: Optional[dict[str, float]] = None,
    ) -> Optional[dict[str, float]]:
        """Compute inverse kinematics: end-effector pose → joint angles.
        
        Args:
            target_position: Target [x, y, z] position in meters
            target_orientation: Optional 3x3 rotation matrix or None for position-only IK
            initial_joint_angles_deg: Initial guess for joint angles (warm start)
            
        Returns:
            Dictionary mapping joint names to angles in degrees, or None if IK fails
        """
        # Build target for IK solver
        if target_orientation is not None:
            # Full pose IK: use 4x4 transformation matrix
            target_matrix = np.eye(4)
            target_matrix[:3, :3] = target_orientation
            target_matrix[:3, 3] = target_position
            orientation_mode = "all"
        else:
            # Position-only IK: use position vector directly
            target_matrix = target_position
            orientation_mode = None
        
        # Get initial joint configuration
        if initial_joint_angles_deg:
            initial_joints_rad = np.zeros(len(self.chain.links))
            for i, link in enumerate(self.chain.links):
                if link.name in initial_joint_angles_deg:
                    initial_joints_rad[i] = np.deg2rad(initial_joint_angles_deg[link.name])
        else:
            initial_joints_rad = [0] * len(self.chain.links)
        
        # Solve IK
        try:
            joint_angles_rad = self.chain.inverse_kinematics(
                target_matrix,
                initial_position=initial_joints_rad,
                orientation_mode=orientation_mode,
            )
            
            # Convert back to degrees and dictionary format
            result = {}
            for i, link in enumerate(self.chain.links):
                if link.name in JOINT_NAMES:
                    result[link.name] = float(np.rad2deg(joint_angles_rad[i]))
            
            # Validate solution (check if FK matches target)
            if not self._validate_ik_solution(result, target_position, target_orientation):
                logger.warning("IK solution failed validation check")
                return None
            
            return result
            
        except Exception as e:
            logger.error(f"IK solver failed: {e}")
            return None
    
    def _validate_ik_solution(
        self,
        joint_angles_deg: dict[str, float],
        target_position: np.ndarray,
        target_orientation: Optional[np.ndarray] = None,
        position_tolerance: float = 0.005,  # 5mm
        orientation_tolerance: float = 0.1,  # ~5.7 degrees
    ) -> bool:
        """Validate IK solution by checking FK error.
        
        Args:
            joint_angles_deg: Proposed joint angles
            target_position: Desired position
            target_orientation: Desired orientation (optional)
            position_tolerance: Maximum position error in meters
            orientation_tolerance: Maximum orientation error in radians
            
        Returns:
            True if solution is valid, False otherwise
        """
        # Compute FK for proposed solution
        computed_pos, computed_ori = self.forward_kinematics(joint_angles_deg)
        
        # Check position error
        pos_error = np.linalg.norm(computed_pos - target_position)
        if pos_error > position_tolerance:
            logger.debug(f"Position error too large: {pos_error*1000:.2f}mm")
            return False
        
        # Check orientation error if provided
        if target_orientation is not None:
            # Compute orientation error using Frobenius norm
            ori_error = np.linalg.norm(computed_ori - target_orientation, 'fro')
            if ori_error > orientation_tolerance:
                logger.debug(f"Orientation error too large: {ori_error:.4f}")
                return False
        
        return True
    
    def get_joint_limits(self) -> dict[str, tuple[float, float]]:
        """Get joint limits in degrees.
        
        Returns:
            Dictionary mapping joint names to (min, max) tuples in degrees
        """
        limits = {}
        for link in self.chain.links:
            if link.name in JOINT_NAMES and hasattr(link, 'bounds'):
                min_rad, max_rad = link.bounds
                limits[link.name] = (np.rad2deg(min_rad), np.rad2deg(max_rad))
        return limits


def test_kinematics():
    """Simple test function for kinematics module."""
    print("Testing SO101 Kinematics...")
    
    # Initialize kinematics
    kin = SO101Kinematics()
    print(f"✓ Loaded kinematic chain from {kin.urdf_path}")
    
    # Test FK with neutral position
    neutral_joints = {
        "shoulder_pan": 0.0,
        "shoulder_lift": 0.0,
        "elbow_flex": 0.0,
        "wrist_flex": 0.0,
        "wrist_roll": 0.0,
        "gripper": 0.0,
    }
    
    pos, ori = kin.forward_kinematics(neutral_joints)
    print("\n✓ Forward Kinematics (neutral pose):")
    print(f"  Position: [{pos[0]:.4f}, {pos[1]:.4f}, {pos[2]:.4f}] meters")
    print(f"  Orientation:\n{ori}")
    
    # Test IK with same position (position-only, no orientation constraint)
    print("\n✓ Inverse Kinematics (target = FK result, position-only):")
    ik_result = kin.inverse_kinematics(pos, initial_joint_angles_deg=neutral_joints)
    if ik_result:
        print("  Solved successfully!")
        for joint_name, angle in ik_result.items():
            print(f"    {joint_name}: {angle:.2f}°")
        
        # Verify FK of IK solution
        pos_check, ori_check = kin.forward_kinematics(ik_result)
        pos_error = np.linalg.norm(pos_check - pos)
        print(f"\n  Position error: {pos_error*1000:.4f}mm")
    else:
        print("  ❌ IK failed!")
    
    # Test with real robot position
    print("\n✓ Testing with real robot position:")
    real_joints = {
        "shoulder_pan": 32.07,
        "shoulder_lift": 15.80,
        "elbow_flex": 36.56,
        "wrist_flex": 58.13,
        "wrist_roll": -12.93,
        "gripper": 3.88,
    }
    
    pos_real, ori_real = kin.forward_kinematics(real_joints)
    print(f"  FK Position: [{pos_real[0]:.4f}, {pos_real[1]:.4f}, {pos_real[2]:.4f}] meters")
    
    # Try to solve IK for slightly offset position
    target_pos = pos_real + np.array([0.01, 0.0, 0.0])  # 10mm in X
    print("\n✓ IK for position offset by 10mm in X:")
    ik_offset = kin.inverse_kinematics(target_pos, initial_joint_angles_deg=real_joints)
    if ik_offset:
        print("  Solved successfully!")
        for joint_name, angle in ik_offset.items():
            delta = angle - real_joints[joint_name]
            print(f"    {joint_name}: {angle:.2f}° (Δ{delta:+.2f}°)")
    else:
        print("  ❌ IK failed!")
    
    print("\n✓ All tests completed!")


if __name__ == "__main__":
    # Run tests when executed directly
    logging.basicConfig(level=logging.INFO)
    test_kinematics()


