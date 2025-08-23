export interface JointInfo {
  name: string;
  current_value: number;
  min: number;
  max: number;
  has_limits: boolean;
}

export interface SimulationState {
  time: number;
  qpos: number[];
  qvel: number[];
  joints: Record<string, number>;
}

export interface CameraParams {
  lookat?: number[];
  distance?: number;
  elevation?: number;
  azimuth?: number;
}

export interface WebSocketMessage {
  type: 'frame' | 'control' | 'camera' | 'gamepad_control';
  image?: string;
  state?: SimulationState;
  data?: Record<string, any>;
  deltas?: {
    x: number;
    y: number;
    z: number;
    wrist: number;
  };
  gripper?: 'open' | 'close' | 'stay';
  buttons?: Record<string, boolean>;
}
