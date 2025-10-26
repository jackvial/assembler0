## Smoother Cartesian and IK Motion Plan

### Quick observations (why it’s not smooth)
- **`lock_wrist` mismatch**: The log states `lock_wrist=True` but the function call uses `lock_wrist=False`, leading to wrist flips and visible jerks.
- **`orientation_mode` ignored**: IK is always position-only; orientation drift accumulates and later abrupt corrections cause discontinuities.
- **Per-sample IK without post-filtering**: Even with warm starts, IK can jump between local minima; there’s no joint-space smoothing, rate limiting, or jerk constraints.
- **No step-size control**: Large Cartesian steps relative to local conditioning cause joint discontinuities; no dynamic sub-stepping when deltas are large.

### Plan to make Cartesian/IK motion smooth

- **P0: Fix correctness and stability**
  - Make log reflect actual `lock_wrist` value and default it to `True` for tasks like printing/dispensing.
  - Implement `orientation_mode`:
    - `fixed`: capture the initial orientation via FK and maintain it, or equivalently lock wrist angles.
    - `interpolate`: slerp orientation per segment; pass to IK with graceful fallback to position-only.
  - Add robust fallback: if IK fails or joint delta exceeds thresholds, reduce step size (sub-sample) and retry; if still failing, hold last valid and warn.

- **P1: Constrain per-step motion (rate/accel/jerk)**
  - After IK, run a joint-space limiter:
    - Clamp max per-sample delta (deg/sample) per joint; if exceeded, insert intermediate samples (upsample) or time-scale.
    - Optional low-pass filter: moving average or Savitzky–Golay over a 3–7 sample window per joint to attenuate high-frequency noise.
  - Add a simple forward–backward velocity limiter (time-scaling) to enforce joint velocity and acceleration limits.

- **P2: Generate a better joint trajectory from an IK path**
  - Compute IK only at sparse Cartesian keyframes (e.g., every 10–20 mm or original waypoints).
  - Interpolate in joint space using cubic/quintic splines.
  - Apply jerk-limited S-curve time law over the joint path (reuse the existing joint-space S-curve machinery).

- **P3: Improve IK robustness**
  - Add an incremental IK routine with damped least-squares (DLS): small position steps, previous solution warm-start, step-size clamp, and retries.
  - Add joint-limit avoidance weights and soft-limit buffers; reject solutions that increase error or violate limit margins.
  - Normalize angle continuity (unwrap around ±180° for roll) to keep shortest rotation path.

- **P4: Sampling and timing**
  - Plan at a higher internal sampling rate (e.g., 100–200 Hz); downsample to the control `fps` after smoothing and rate limiting.
  - Ensure the streamed commands already obey per-sample limits; the loop shouldn’t have to correct spikes.

- **P5: Safety, limits, and tuning**
  - Read joint limits via `get_joint_limits()`; create soft-limit buffers and add cost/weights to avoid edges.
  - Expose tunables via CLI with sane defaults:
    - `max_joint_step_deg`, `max_joint_velocity_deg_s`, `max_joint_accel_deg_s2`, `smoothing_window`, `dls_lambda`, `orientation_mode`, `lock_wrist`.
  - Log per-second metrics: max per-joint delta, violations prevented, IK retries, sub-steps taken.

### Implementation outline by file

- **`demo_so101_follower.py`**
  - Fix `lock_wrist` pass-through and logging.
  - Honor `orientation_mode`:
    - `fixed`: maintain initial orientation or lock wrist joints by angle.
    - `interpolate`: slerp orientation per segment and pass to IK; fall back to position-only on degradation.
  - Add post-IK pipeline:
    - Continuity: unwrap rotational joints (especially `wrist_roll`).
    - Limiter: clamp per-sample deltas; if exceeded, sub-sample or time-scale; avoid re-solving IK when interpolation suffices.
    - Optional smoothing filter; then time-scale to respect velocity/accel limits.
  - Option: Compute IK for sparse keyframes, then run existing joint-space S-curve over those IK joints.

- **`kinematics_so101.py`**
  - Add `inverse_kinematics_incremental(target_position, target_orientation, prev_joints, max_step_deg, lambda_dls)`:
    - DLS iteration with step-size clamp, early stop on tolerance, retries, and joint-limit avoidance.
  - Helpers: `unwrap_angle_continuous(prev_angle, angle)` and `apply_joint_limits_soft(joints)`.

### Validation and tuning steps
- Dry-run in sim: log Cartesian deviation from straight line (mm), max joint jerk, IK retries.
- Bench on hardware at low speed; watch for wrist oscillation and singularities.
- Tune in order: `lock_wrist` → max step clamp → smoothing window → velocity/accel caps → DLS lambda.
- Target metrics:
  - < 0.5 mm RMS deviation from straight line at 20 mm/s
  - No joint delta spikes > 2 deg/sample at 50 Hz
  - Zero IK failures on nominal paths

### Immediate quick win
- Fix the `lock_wrist` mismatch and add per-sample joint delta clamps plus a small moving-average filter. This typically removes most visible jitter.

### Key issues to address (recap)
- `lock_wrist` mismatch in `demo_so101_follower.py`.
- `orientation_mode` is ignored; IK is always position-only.
- No post-IK joint-space smoothing, rate limiting, or jerk constraints.
- No step-size control or dynamic sub-stepping to prevent IK jumps.
