# Cartesian Straight-Line Motion for SO101 Robot

## Overview

The SO101 robot now supports **Cartesian straight-line interpolation** using inverse kinematics. This ensures the end-effector moves in true straight lines in 3D space, which is essential for 3D printing applications.

## What's New

### Phase 1: Cartesian IK (✅ Implemented)

- **Straight-line motion**: End-effector follows linear paths in Cartesian space
- **Inverse kinematics**: Automatic joint angle solving using `ikpy` library
- **S-curve velocity profiles**: Smooth acceleration/deceleration in Cartesian space
- **Orientation control**: Fixed or interpolated tool orientation
- **Fallback handling**: Graceful handling of IK failures

## Usage

### Basic Usage

```bash
# Cartesian mode with straight lines (recommended for 3D printing)
python demo_so101_follower.py \
  --port /dev/ttyACM0 \
  --robot_id assembler0_so101_follower \
  --waypoints_file waypoints.json \
  --fps 50 \
  --cartesian_mode \
  --speed_mm_s 20 \
  --accel_mm_s2 100

# Joint-space mode (curved paths, faster)
python demo_so101_follower.py \
  --port /dev/ttyACM0 \
  --robot_id assembler0_so101_follower \
  --waypoints_file waypoints.json \
  --fps 50 \
  --speed_deg_s 5 \
  --accel_deg_s2 25
```

### Recording Waypoints

Use the updated `find_home_position.py` to record waypoints:

```bash
# Record waypoints by pressing SPACE BAR
python find_home_position.py --port /dev/ttyACM0 --output my_path.json

# Then use them with Cartesian mode
python demo_so101_follower.py \
  --port /dev/ttyACM0 \
  --waypoints_file my_path.json \
  --cartesian_mode
```

## Command-Line Arguments

### Cartesian Mode

- `--cartesian_mode`: Enable Cartesian straight-line interpolation
- `--speed_mm_s <float>`: Cartesian speed in mm/s (default: 20.0)
- `--accel_mm_s2 <float>`: Cartesian acceleration in mm/s² (default: 100.0)
- `--orientation_mode {fixed,interpolate}`: 
  - `fixed`: Maintain initial tool orientation (recommended for printing)
  - `interpolate`: Blend orientations between waypoints

### Joint-Space Mode (Original)

- `--speed_deg_s <float>`: Joint-space speed in °/s (default: 5.0)
- `--accel_deg_s2 <float>`: Joint-space acceleration in °/s² (default: 25.0)
- `--blend_ms <int>`: Corner blending in milliseconds (default: 80)

### Common Parameters

- `--fps <int>`: Control loop frequency in Hz (default: 30, recommend 50 for smooth motion)
- `--waypoints_file <path>`: JSON file with waypoints
- `--port <device>`: Serial port (e.g., /dev/ttyACM0)
- `--robot_id <id>`: Robot ID matching calibration file

## How It Works

### Joint-Space Mode (Original)

1. Interpolates linearly between joint angles
2. All joints reach targets simultaneously
3. **Result**: Curved paths in 3D space (faster, simpler)

### Cartesian Mode (New)

1. Converts joint waypoints to Cartesian poses using Forward Kinematics (FK)
2. Interpolates linearly in Cartesian space (X, Y, Z positions)
3. Samples points along straight lines
4. Solves Inverse Kinematics (IK) for each sample point
5. Applies S-curve velocity profile
6. **Result**: Straight lines in 3D space (precise, for printing)

## Files Created

- `kinematics_so101.py`: FK/IK solver using ikpy
- `urdf/so101_follower.urdf`: Robot description for kinematics
- `CARTESIAN_MODE.md`: This documentation

## Requirements

Added dependencies (already in `pyproject.toml`):
- `ikpy>=3.3`: Inverse kinematics library
- `scipy>=1.10`: Numerical optimization

Install with:
```bash
uv sync
```

## Testing

Test the kinematics module independently:

```bash
python kinematics_so101.py
```

Expected output:
```
✓ Loaded kinematic chain from urdf/so101_follower.urdf
✓ Forward Kinematics (neutral pose)
✓ Inverse Kinematics (position-only)
✓ IK for position offset
✓ All tests completed!
```

## Troubleshooting

### IK Failures

If you see "IK failed" warnings during trajectory execution:

1. **Check reachability**: Target positions may be outside robot workspace
2. **Reduce speed**: Lower `--speed_mm_s` to give IK solver more samples
3. **Increase FPS**: Higher `--fps` provides denser sampling
4. **Check joint limits**: Verify waypoints are within joint ranges

### Slow Execution

If the control loop runs slow (warnings about >XX ms):

1. **Lower FPS**: Reduce `--fps` to 30 or 20
2. **Simplify path**: Use fewer waypoints
3. **Check CPU load**: IK solving is computationally intensive

### Jerky Motion

If motion is not smooth:

1. **Increase FPS**: Use `--fps 50` or higher
2. **Adjust acceleration**: Reduce `--accel_mm_s2`
3. **Check speed**: Verify `--speed_mm_s` is reasonable for your setup

## Performance Tips

### For 3D Printing

```bash
--cartesian_mode \
--fps 50 \
--speed_mm_s 15 \
--accel_mm_s2 75 \
--orientation_mode fixed
```

### For Fast Motion (Non-Printing)

```bash
--speed_deg_s 10 \
--accel_deg_s2 50 \
--fps 30
```

## Phase 2: G-code Support (Planned)

Future enhancement will add:
- G-code parser (`gcode_to_waypoints.py`)
- Workspace calibration tool (`calibrate_print_workspace.py`)
- Direct printing from slicer output

Workflow:
```
STL → Slicer → G-code → Parser → Cartesian waypoints → IK → Robot motion
```

## Examples

### Example 1: Simple Straight Line

Create `line_test.json`:
```json
[
  {
    "shoulder_pan.pos": 30.0,
    "shoulder_lift.pos": 20.0,
    "elbow_flex.pos": 35.0,
    "wrist_flex.pos": 55.0,
    "wrist_roll.pos": 0.0,
    "gripper.pos": 0.0
  },
  {
    "shoulder_pan.pos": 35.0,
    "shoulder_lift.pos": 20.0,
    "elbow_flex.pos": 35.0,
    "wrist_flex.pos": 55.0,
    "wrist_roll.pos": 0.0,
    "gripper.pos": 0.0
  }
]
```

Run:
```bash
python demo_so101_follower.py \
  --port /dev/ttyACM0 \
  --waypoints_file line_test.json \
  --cartesian_mode \
  --speed_mm_s 10
```

### Example 2: Square Path

Record 4 corners of a square using `find_home_position.py`, then execute with Cartesian mode for precise straight edges.

## Technical Details

### Kinematics Chain

- **DOF**: 5 active joints (shoulder_pan, shoulder_lift, elbow_flex, wrist_flex, wrist_roll)
- **Gripper**: Passive (passes through unchanged)
- **End-effector**: Gripper frame origin
- **IK Method**: Numerical (Jacobian pseudo-inverse)
- **Solver**: ikpy with position-only or full-pose targets

### Coordinate Systems

- **Robot base frame**: Origin at robot base
- **Units**: Meters for positions, radians internally (degrees in API)
- **Orientation**: 3x3 rotation matrices

### Velocity Profile

S-curve (sine-based) for smooth jerk-limited motion:
- Acceleration phase: Smooth ramp-up
- Cruise phase: Constant velocity
- Deceleration phase: Smooth ramp-down

## Support

For issues or questions:
1. Check robot calibration is up-to-date
2. Verify URDF matches your hardware
3. Test kinematics module independently
4. Review log output for specific errors

## License

Same as parent project (Apache 2.0)

