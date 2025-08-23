export interface GamepadState {
  connected: boolean;
  leftStick: { x: number; y: number };
  rightStick: { x: number; y: number };
  buttons: {
    a: boolean;
    b: boolean;
    x: boolean;
    y: boolean;
    lb: boolean;
    rb: boolean;
    lt: number;
    rt: number;
    back: boolean;
    start: boolean;
    leftStickButton: boolean;
    rightStickButton: boolean;
    dpadUp: boolean;
    dpadDown: boolean;
    dpadLeft: boolean;
    dpadRight: boolean;
    home: boolean;
  };
}

export interface GamepadConfig {
  deadzone: number;
  sensitivity: {
    leftStick: number;
    rightStick: number;
    triggers: number;
  };
  invertY: boolean;
}

export interface GamepadControlMessage {
  type: 'gamepad_control';
  deltas: {
    x: number;
    y: number;
    z: number;
    wrist: number;
  };
  gripper?: 'open' | 'close' | 'stay';
  buttons?: Record<string, boolean>;
}

export const DEFAULT_GAMEPAD_CONFIG: GamepadConfig = {
  deadzone: 0.1,
  sensitivity: {
    leftStick: 1.0,
    rightStick: 1.0,
    triggers: 1.0,
  },
  invertY: false,
};

export const GAMEPAD_BUTTON_MAPPING = {
  0: 'a',
  1: 'b',
  2: 'x',
  3: 'y',
  4: 'lb',
  5: 'rb',
  6: 'lt',
  7: 'rt',
  8: 'back',
  9: 'start',
  10: 'leftStickButton',
  11: 'rightStickButton',
  12: 'dpadUp',
  13: 'dpadDown',
  14: 'dpadLeft',
  15: 'dpadRight',
  16: 'home',
} as const;
