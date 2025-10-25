# Finding Home and Waypoint Positions

This guide explains how to use the position finder tool to determine good positions for your SO101Follower robot.

## What Does This Tool Do?

The `find_home_position.py` script:
1. Connects to your SO101Follower robot
2. **Disables all motor torque** so you can freely move the arm
3. Continuously displays the current joint positions as you move it
4. When you press Ctrl+C, it saves and displays the position in formats ready to use

## Quick Start

```bash
# Run the position finder
./find_home_position.sh
```

## Step-by-Step Process

### 1. Start the Tool
```bash
./find_home_position.sh
```

You'll see:
```
MANUAL POSITIONING MODE
================================================================================

The robot torque is now DISABLED. You can manually move the arm.
Move the arm to your desired home position.

Press Ctrl+C when you've found the position you want to save.
================================================================================

Current Joint Positions:
--------------------------------------------------------------------------------
  shoulder_pan        :    10.23
  shoulder_lift       :    -5.67
  elbow_flex          :    15.42
  wrist_flex          :     0.00
  wrist_roll          :     2.34
  gripper             :    50.00
--------------------------------------------------------------------------------
```

### 2. Move the Arm

- The robot is now "limp" - torque is disabled
- Physically move each joint to your desired position
- Watch the position values update in real-time
- Take your time to find the perfect position

### 3. Save the Position

When you're happy with the position, press **Ctrl+C**

The tool will display the position in two formats:

**Python Dictionary Format:**
```python
{
    "shoulder_pan.pos": 10.23,
    "shoulder_lift.pos": -5.67,
    "elbow_flex.pos": 15.42,
    "wrist_flex.pos": 0.00,
    "wrist_roll.pos": 2.34,
    "gripper.pos": 50.00,
}
```

**JSON Waypoint Format:**
```json
{
  "shoulder_pan.pos": 10.23,
  "shoulder_lift.pos": -5.67,
  "elbow_flex.pos": 15.42,
  "wrist_flex.pos": 0.00,
  "wrist_roll.pos": 2.34,
  "gripper.pos": 50.00
}
```

### 4. Use the Position

Copy the position values and:
- **Update the demo script:** Edit `demo_so101_follower.py` and replace the home position in `DEFAULT_WAYPOINTS`
- **Create a custom waypoints file:** Add the position to a JSON file like `example_waypoints.json`

## Use Cases

### Finding a Safe Home Position

1. Run `./find_home_position.sh`
2. Move the arm to a safe, neutral position
3. Press Ctrl+C and copy the values
4. Update the first waypoint in `DEFAULT_WAYPOINTS` in `demo_so101_follower.py`

### Creating a Sequence of Waypoints

1. Run `./find_home_position.sh`
2. Move to position 1, press Ctrl+C, copy values
3. Run again for position 2, press Ctrl+C, copy values
4. Repeat for all desired positions
5. Create a JSON file with all positions:

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
    "shoulder_pan.pos": 30.0,
    "shoulder_lift.pos": -20.0,
    "elbow_flex.pos": 45.0,
    "wrist_flex.pos": -10.0,
    "wrist_roll.pos": 0.0,
    "gripper.pos": 50.0
  }
]
```

6. Test with: `python demo_so101_follower.py --port /dev/ttyACM0 --waypoints_file my_waypoints.json`

### Finding Joint Limits

1. Run `./find_home_position.sh`
2. Slowly move each joint to its maximum extent
3. Note the maximum and minimum values for each joint
4. Use these limits when creating waypoints to avoid exceeding them

## Command-Line Options

```bash
# Use a different port
PORT=/dev/ttyACM1 ./find_home_position.sh

# Faster position updates (every 0.2 seconds)
UPDATE_RATE=0.2 ./find_home_position.sh

# Or use Python directly with custom robot ID
python find_home_position.py \
    --port /dev/ttyACM0 \
    --robot_id my_custom_robot \
    --update_rate 0.3
```

### Available Arguments:
- `--port` - Serial port for the robot (e.g., `/dev/ttyACM0`)
- `--robot_id` - Robot identifier (default: `assembler0_so101_follower`)
- `--update_rate` - How often to update position display in seconds (default: `0.5`)

## Tips

1. **Support the arm** when torque is disabled to prevent it from falling
2. **Move slowly** when finding positions to avoid damaging the robot
3. **Test one joint at a time** to see how each affects the position
4. **Round values** if needed for cleaner waypoint files (e.g., `10.23` → `10.0`)
5. **Start with home position** then branch out to other waypoints
6. **Keep the gripper at 50.0** for a neutral position (0=fully open, 100=fully closed)

## Safety Notes

⚠️ **Important Safety Considerations:**
- The robot will be limp when torque is disabled
- Support the arm to prevent it from falling
- Ensure clear workspace before starting
- Don't force joints beyond their natural limits
- The robot will re-enable torque when you disconnect (unless you used `--disable_torque_on_disconnect`)

## Troubleshooting

### Robot falls when torque is disabled
- This is normal! Support the arm when moving it
- The robot has no motor resistance when torque is off

### Position values not updating
- Check that the robot is connected and calibrated
- Try a slower `--update_rate` (e.g., `1.0`)
- Ensure the calibration file matches the robot ID

### Error connecting to robot
- Check the port: `ls /dev/tty*`
- Verify robot is powered on
- Ensure you have permission to access the port

### Values seem wrong
- Make sure robot is calibrated: `./so101_follower_calibrate.sh`
- Check that `--robot_id` matches your calibration file

## Next Steps

After finding your positions:
1. Create or update a waypoints file
2. Test with the demo script
3. Adjust timing with `--wait_time` and `--fps` if needed
4. Fine-tune positions by running the position finder again

For more information, see `SO101_FOLLOWER_INTEGRATION.md`.

