import { useEffect, useRef } from 'react';
import {
  GamepadState,
  GamepadConfig,
  GamepadControlMessage,
} from '../types/gamepad';
import { sendGamepadControl } from '../services/gamepadService';

const CONTROL_UPDATE_RATE = 60; // Hz
const CONTROL_UPDATE_INTERVAL = 1000 / CONTROL_UPDATE_RATE;

export const useGamepadControl = (
  gamepadState: GamepadState,
  config: GamepadConfig
) => {
  const lastUpdateTime = useRef<number>(0);
  const previousState = useRef<GamepadState | null>(null);

  useEffect(() => {
    if (!gamepadState.connected) {
      return;
    }

    const now = Date.now();
    if (now - lastUpdateTime.current < CONTROL_UPDATE_INTERVAL) {
      return;
    }

    // Check if there's meaningful input
    const hasMovement =
      Math.abs(gamepadState.leftStick.x) > 0.01 ||
      Math.abs(gamepadState.leftStick.y) > 0.01 ||
      Math.abs(gamepadState.rightStick.x) > 0.01 ||
      Math.abs(gamepadState.rightStick.y) > 0.01;

    const hasGripperInput =
      gamepadState.buttons.lt > 0.1 || gamepadState.buttons.rt > 0.1;

    if (!hasMovement && !hasGripperInput && previousState.current) {
      // Check if any important buttons changed
      const buttonChanged =
        gamepadState.buttons.a !== previousState.current.buttons.a ||
        gamepadState.buttons.x !== previousState.current.buttons.x ||
        gamepadState.buttons.y !== previousState.current.buttons.y ||
        gamepadState.buttons.rb !== previousState.current.buttons.rb;

      if (!buttonChanged) {
        return;
      }
    }

    // Calculate speed multiplier based on button state
    // Hold RB for precision mode (slower), normal speed otherwise
    // Note: RB is still sent as a button so backend configs can use it differently
    const speedMultiplier = gamepadState.buttons.rb ? 0.03 : 0.15;

    // Calculate deltas for end-effector control
    // Left stick X/Y for horizontal movement
    // Right stick Y for vertical movement, X for wrist rotation
    const controlMessage: GamepadControlMessage = {
      type: 'gamepad_control',
      deltas: {
        x: gamepadState.leftStick.x * speedMultiplier,
        y: -gamepadState.leftStick.y * speedMultiplier, // Invert Y for intuitive control
        z: -gamepadState.rightStick.y * speedMultiplier, // Right stick Y for vertical
        wrist: gamepadState.rightStick.x * speedMultiplier, // Right stick X for wrist rotation
      },
      gripper: undefined,
      buttons: {
        a: gamepadState.buttons.a,
        x: gamepadState.buttons.x,
        y: gamepadState.buttons.y,
        lb: gamepadState.buttons.lb,
        rb: gamepadState.buttons.rb,
        dpadUp: gamepadState.buttons.dpadUp,
        dpadDown: gamepadState.buttons.dpadDown,
        dpadLeft: gamepadState.buttons.dpadLeft,
        dpadRight: gamepadState.buttons.dpadRight,
      },
    };

    // Handle gripper control
    if (gamepadState.buttons.rt > 0.5) {
      controlMessage.gripper = 'open';
    } else if (gamepadState.buttons.lt > 0.5) {
      controlMessage.gripper = 'close';
    } else {
      controlMessage.gripper = 'stay';
    }

    // Send control message
    sendGamepadControl(controlMessage);

    lastUpdateTime.current = now;
    previousState.current = { ...gamepadState };
  }, [gamepadState, config]);
};
