# SO101 Follower Integration

This document describes the integration of the SO101Follower robot into the codebase and provides usage instructions.

## What Was Added

### 1. Calibration Support
The SO101Follower robot can now be calibrated using the existing calibration script.

**Modified File:**
- `packages/assembler0-robot/src/assembler0_robot/scripts/calibrate.py`
  - Added `"so101_follower"` variant option
  - Added calibration logic for SO101Follower (without screwdriver-specific parameters)

**Usage:**
```bash
# Using the helper script (easiest)
./so101_follower_calibrate.sh

# Or using Python directly
python -m assembler0_robot.scripts.calibrate \
    --device_type=robot \
    --robot_variant=so101_follower \
    --port=/dev/ttyACM0 \
    --device_id=assembler0_so101_follower
```

### 2. Demo Script with Waypoint Control
A standalone demo script that moves the SO101Follower through preprogrammed waypoints.

**New Files:**
- `demo_so101_follower.py` - Main demo script
- `demo_so101_follower.sh` - Helper shell script for easy execution
- `example_waypoints.json` - Example custom waypoints file
- `so101_follower_calibrate.sh` - Helper script for calibration

**Features:**
- Connects to SO101Follower robot
- Moves through a sequence of waypoints
- Built-in demo waypoints (wave motion, gripper open/close)
- Support for loading custom waypoints from JSON file
- Configurable control loop frequency (FPS)
- Configurable wait time at each waypoint
- Graceful shutdown on Ctrl+C

## Usage Examples

### Basic Demo with Built-in Waypoints
```bash
# Using the shell script (easiest)
./demo_so101_follower.sh

# Or with custom port
PORT=/dev/ttyACM1 ./demo_so101_follower.sh

# Or using Python directly
python demo_so101_follower.py --port /dev/ttyACM0 --robot_id assembler0_so101_follower
```

### Demo with Custom Waypoints
```bash
# Create your own waypoints file (see example_waypoints.json)
python demo_so101_follower.py \
    --port /dev/ttyACM0 \
    --waypoints_file my_custom_waypoints.json \
    --wait_time 3.0 \
    --fps 30
```

### Custom Waypoints Format
Waypoints are defined as a JSON array of motor position dictionaries:

```json
[
  {
    "shoulder_pan.pos": 0.0,
    "shoulder_lift.pos": 0.0,
    "elbow_flex.pos": 0.0,
    "wrist_flex.pos": 0.0,
    "wrist_roll.pos": 0.0,
    "gripper.pos": 50.0
  },
  {
    "shoulder_pan.pos": 45.0,
    "shoulder_lift.pos": -20.0,
    "elbow_flex.pos": 45.0,
    "wrist_flex.pos": -25.0,
    "wrist_roll.pos": 0.0,
    "gripper.pos": 100.0
  }
]
```

## Command-Line Arguments

### demo_so101_follower.py

**Required:**
- `--port` - Serial port for the robot (e.g., `/dev/ttyACM0`)

**Optional:**
- `--robot_id` - Robot identifier (default: `assembler0_so101_follower`, should match calibration file)
- `--waypoints_file` - Path to custom waypoints JSON file (default: uses built-in demo waypoints)
- `--wait_time` - Time to wait at each waypoint in seconds (default: `2.0`)
- `--fps` - Control loop frequency in Hz (default: `30`)
- `--disable_torque_on_disconnect` - Disable motor torque when disconnecting (robot will go limp)

### Environment Variables for Shell Script

- `PORT` - Serial port (default: `/dev/ttyACM0`)
- `ROBOT_ID` - Robot ID (default: `assembler0_so101_follower`)
- `FPS` - Control loop frequency (default: `30`)
- `WAIT_TIME` - Wait time at waypoints (default: `2.0`)

## Motor Names and Position Ranges

The SO101Follower has the following motors:

| Motor Name | Description | Position Range |
|------------|-------------|----------------|
| `shoulder_pan.pos` | Base rotation | -100 to 100 (or degrees if configured) |
| `shoulder_lift.pos` | Shoulder elevation | -100 to 100 (or degrees if configured) |
| `elbow_flex.pos` | Elbow joint | -100 to 100 (or degrees if configured) |
| `wrist_flex.pos` | Wrist pitch | -100 to 100 (or degrees if configured) |
| `wrist_roll.pos` | Wrist rotation | -100 to 100 (or degrees if configured) |
| `gripper.pos` | Gripper open/close | 0 (open) to 100 (closed) |

**Note:** The actual range depends on the `use_degrees` configuration parameter in `SO101FollowerConfig`. By default, it uses normalized range (-100 to 100).

## Workflow

### First Time Setup
1. **Connect the robot** to your computer via USB
2. **Identify the port** (e.g., `/dev/ttyACM0` or `/dev/ttyACM1`)
3. **Calibrate the robot:**
   ```bash
   ./so101_follower_calibrate.sh
   ```
   - Follow the on-screen instructions
   - Move the robot to the middle of its range when prompted
   - Move each joint through its full range when prompted
   - Calibration data will be saved for future use

### Running the Demo
1. **Ensure the robot is calibrated** (see above)
2. **Run the demo:**
   ```bash
   ./demo_so101_follower.sh
   ```
3. **Watch the robot move** through the preprogrammed waypoints
4. **Press Ctrl+C** to stop at any time

### Creating Custom Movements
1. **Create a waypoints file** based on `example_waypoints.json`
2. **Test your waypoints:**
   ```bash
   python demo_so101_follower.py \
       --port /dev/ttyACM0 \
       --waypoints_file my_waypoints.json
   ```
3. **Adjust timing** if needed with `--wait_time` and `--fps` parameters

## Safety Notes

- Always ensure the robot has clear space to move before running demos
- Start with slow movements (low FPS) when testing new waypoints
- Use `--disable_torque_on_disconnect` if you want the robot to go limp after the demo
- Press Ctrl+C at any time to stop the demo and disconnect safely
- Keep the emergency stop (if available) within reach

## Troubleshooting

### Robot won't connect
- Check that the correct port is specified
- Verify the robot is powered on
- Check USB cable connection
- Try listing available ports: `ls /dev/tty*`

### Robot moves erratically
- Ensure the robot is calibrated: `./so101_follower_calibrate.sh`
- Check that waypoint positions are within valid range
- Try reducing FPS for smoother motion

### Permission denied on port
```bash
sudo chmod 666 /dev/ttyACM0  # Or your specific port
# Or add your user to the dialout group:
sudo usermod -a -G dialout $USER
# Then log out and back in
```

## Integration Details

The SO101Follower robot class is located at:
- `packages/assembler0-robot/src/assembler0_robot/robots/so101_follower/so101_follower.py`
- `packages/assembler0-robot/src/assembler0_robot/robots/so101_follower/config_so101_follower.py`

It uses the FeetechMotorsBus with 6 STS3215 motors and supports camera integration (though cameras are not used in this demo).

### Import Paths
The SO101Follower can be imported using:
```python
from assembler0_robot.robots.so101_follower import SO101Follower, SO101FollowerConfig
```

### Fixed Import Issues
The SO101Follower code was originally copied from lerobot and had incorrect import paths. The following fixes were applied:
- Changed `from ..config import RobotConfig` to `from lerobot.robots.config import RobotConfig`
- Changed `from ..robot import Robot` to `from lerobot.robots.robot import Robot`
- Changed `from ..utils import ensure_safe_goal_position` to `from lerobot.robots.utils import ensure_safe_goal_position`
- Changed `from lerobot.utils.errors` to `from lerobot.errors`
- Added `from __future__ import annotations` for Python 3.10+ compatibility

## Future Enhancements

Potential improvements that could be made:
- Add teleoperation support with SO101Leader
- Add trajectory interpolation between waypoints
- Support for velocity control in addition to position control
- Real-time visualization of robot state
- Recording and playback of movement sequences
- Integration with the simulator

## Support

For issues or questions, refer to the main project README or open an issue in the repository.

