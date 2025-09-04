# SO101 Robot SimplerEnv Integration Plan

## Overview
Plan to integrate the SO101 robot arm with SimplerEnv validation framework for simulation-based policy evaluation.

## Prerequisites

### Hardware Requirements
- NVIDIA GPU (RTX recommended)
- CUDA ≥11.8
- Sufficient RAM for simulation environments

### Software Requirements
- Python 3.10 or 3.11
- SimplerEnv framework
- SAPIEN simulator
- ManiSkill2 benchmark

## Phase 1: Environment Setup

### 1.1 Install SimplerEnv
```bash
git clone https://github.com/simpler-env/SimplerEnv.git
cd SimplerEnv
pip install -e .
```

### 1.2 Download SO101 URDF Assets
```bash
# Clone SO-ARM100 repository
git clone https://github.com/TheRobotStudio/SO-ARM100.git
# Extract URDF and mesh files from Simulation/SO101/
```

### 1.3 Verify Dependencies
- Ensure CUDA toolkit is properly installed
- Test SAPIEN simulator functionality
- Validate ManiSkill2 environment

## Phase 2: Robot Configuration

### 2.1 URDF Analysis & Modification
**Key SO101 Specifications:**
- 6 DOF arm with gripper
- Joint limits: shoulder_pan (±1.92), shoulder_lift (±1.74), elbow_flex (±1.69), wrist_flex (±1.66), wrist_roll (±2.84), gripper (±0.17)
- Total mass: ~0.8kg distributed across links
- Uses position joint interfaces

**Required Modifications:**
- Update mesh file paths to match SimplerEnv directory structure
- Ensure material properties are compatible with SAPIEN
- Verify inertial properties for stable simulation
- Add collision geometries if missing

### 2.2 Create Robot Configuration Files
```python
# Create so101_config.py
SO101_CONFIG = {
    "urdf_path": "assets/so101/so101_new_calib.urdf",
    "joint_names": [
        "shoulder_pan_joint",
        "shoulder_lift_joint", 
        "elbow_flex_joint",
        "wrist_flex_joint",
        "wrist_roll_joint",
        "gripper_joint"
    ],
    "joint_limits": {
        "lower": [-1.92, -1.74, -1.69, -1.66, -2.84, -0.17],
        "upper": [1.92, 1.74, 1.69, 1.66, 2.84, 0.17]
    },
    "end_effector_link": "gripper_link"
}
```

## Phase 3: Environment Integration

### 3.1 Create SO101 Environment Class
Extend SimplerEnv's base robot environment:
```python
class SO101Env(BaseRobotEnv):
    def __init__(self, **kwargs):
        # Load SO101 URDF
        # Configure joint controllers
        # Set up end-effector
        # Initialize workspace bounds
```

### 3.2 Implement Required Methods
- `reset()` - Reset robot to home position
- `step()` - Execute action and return observation
- `get_observation()` - Return current robot state
- `calculate_reward()` - Task-specific reward function

### 3.3 Register Environment
Add SO101 to SimplerEnv's environment registry:
```python
# In environments/__init__.py
from .so101_env import SO101Env
register_env("SO101-v1", SO101Env)
```

## Phase 4: Validation Tasks

### 4.1 Basic Functionality Tests
- Joint movement validation
- Forward/inverse kinematics testing
- Collision detection verification
- Gripper operation testing

### 4.2 Manipulation Tasks
Implement standard manipulation benchmarks:
- **Pick and Place**: Basic object manipulation
- **Stack Blocks**: Multi-step coordination
- **Door Opening**: Contact-rich manipulation
- **Drawer Sliding**: Constrained movement

### 4.3 Policy Evaluation Framework
```python
# Create evaluation script
def evaluate_so101_policy(policy, num_episodes=100):
    env = make_env("SO101-v1")
    results = []
    
    for episode in range(num_episodes):
        obs = env.reset()
        done = False
        episode_reward = 0
        
        while not done:
            action = policy.predict(obs)
            obs, reward, done, info = env.step(action)
            episode_reward += reward
        
        results.append(episode_reward)
    
    return calculate_metrics(results)
```

## Phase 5: Advanced Features

### 5.1 Visual Matching Integration
- Implement real-world image overlay functionality
- Configure camera parameters to match real SO101 setup
- Create domain randomization for lighting and textures

### 5.2 Variant Aggregation
- Create multiple environment variants:
  - Different object properties (mass, friction)
  - Varied lighting conditions
  - Multiple starting configurations
  - Different surface materials

### 5.3 Metrics Implementation
- Mean Maximum Rank Violation (MMRV)
- Pearson Correlation with real-world performance
- Task completion rates
- Action smoothness metrics

## Phase 6: Validation and Testing

### 6.1 Unit Tests
- Individual component functionality
- Joint limit enforcement
- Collision detection accuracy
- Reward function correctness

### 6.2 Integration Tests
- End-to-end policy evaluation
- Multi-episode consistency
- Memory usage and performance
- Deterministic reproducibility

### 6.3 Benchmarking
- Compare against existing SimplerEnv robots
- Validate simulation-to-real transfer metrics
- Performance profiling and optimization

## Phase 7: Documentation and Deployment

### 7.1 Create Usage Documentation
- Setup instructions
- API reference
- Example scripts
- Troubleshooting guide

### 7.2 Example Policies
Provide sample policies for testing:
- Random policy baseline
- Pre-trained manipulation policies
- Custom SO101-specific behaviors

### 7.3 Contribution to SimplerEnv
- Submit pull request with SO101 integration
- Provide benchmark results
- Share evaluation datasets

## Timeline Estimation

- **Phase 1-2**: 1-2 weeks (Setup and robot configuration)
- **Phase 3-4**: 2-3 weeks (Environment integration and basic validation)
- **Phase 5**: 1-2 weeks (Advanced features)
- **Phase 6-7**: 1 week (Testing and documentation)

**Total Estimated Time**: 5-8 weeks

## Success Criteria

1. SO101 robot successfully loads and operates in SimplerEnv
2. Basic manipulation tasks execute without errors
3. Policy evaluation framework produces consistent results
4. Simulation performance meets real-time requirements
5. Integration passes all SimplerEnv compatibility tests

## Risk Mitigation

- **URDF Compatibility Issues**: Test with minimal URDF first, gradually add complexity
- **Performance Bottlenecks**: Profile early and optimize critical paths
- **Simulation Instability**: Validate inertial properties and joint limits
- **Integration Complexity**: Start with existing robot examples as templates

## Resources

- [SO101 URDF Source](https://github.com/TheRobotStudio/SO-ARM100/blob/main/Simulation/SO101/so101_new_calib.urdf)
- [SimplerEnv Documentation](https://github.com/simpler-env/SimplerEnv)
- [SAPIEN Documentation](https://sapien.ucsd.edu/)
- [ManiSkill2 Framework](https://github.com/haosulab/ManiSkill2)