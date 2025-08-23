import { useEffect, useRef, useState, useCallback } from 'react';
import {
  GamepadState,
  GamepadConfig,
  DEFAULT_GAMEPAD_CONFIG,
  GAMEPAD_BUTTON_MAPPING,
} from '../types/gamepad';

const applyDeadzone = (value: number, deadzone: number): number => {
  if (Math.abs(value) < deadzone) {
    return 0;
  }
  const sign = value > 0 ? 1 : -1;
  return sign * ((Math.abs(value) - deadzone) / (1 - deadzone));
};

export const useGamepad = (config: GamepadConfig = DEFAULT_GAMEPAD_CONFIG) => {
  const [gamepadState, setGamepadState] = useState<GamepadState>({
    connected: false,
    leftStick: { x: 0, y: 0 },
    rightStick: { x: 0, y: 0 },
    buttons: {
      a: false,
      b: false,
      x: false,
      y: false,
      lb: false,
      rb: false,
      lt: 0,
      rt: 0,
      back: false,
      start: false,
      leftStickButton: false,
      rightStickButton: false,
      dpadUp: false,
      dpadDown: false,
      dpadLeft: false,
      dpadRight: false,
      home: false,
    },
  });

  const animationFrameId = useRef<number | null>(null);
  const gamepadIndex = useRef<number | null>(null);

  const pollGamepad = useCallback(() => {
    const gamepads = navigator.getGamepads();

    if (gamepadIndex.current === null) {
      for (let i = 0; i < gamepads.length; i++) {
        const gamepad = gamepads[i];
        if (gamepad) {
          gamepadIndex.current = i;
          console.log(`Gamepad connected: ${gamepad.id}`);
          break;
        }
      }
    }

    if (gamepadIndex.current !== null) {
      const gamepad = gamepads[gamepadIndex.current];

      if (!gamepad) {
        gamepadIndex.current = null;
        setGamepadState((prev) => ({ ...prev, connected: false }));
        animationFrameId.current = requestAnimationFrame(pollGamepad);
        return;
      }

      const leftX =
        applyDeadzone(gamepad.axes[0], config.deadzone) *
        config.sensitivity.leftStick;
      const leftY =
        applyDeadzone(gamepad.axes[1], config.deadzone) *
        config.sensitivity.leftStick *
        (config.invertY ? -1 : 1);
      const rightX =
        applyDeadzone(gamepad.axes[2], config.deadzone) *
        config.sensitivity.rightStick;
      const rightY =
        applyDeadzone(gamepad.axes[3], config.deadzone) *
        config.sensitivity.rightStick *
        (config.invertY ? -1 : 1);

      const buttons: GamepadState['buttons'] = {
        a: false,
        b: false,
        x: false,
        y: false,
        lb: false,
        rb: false,
        lt: 0,
        rt: 0,
        back: false,
        start: false,
        leftStickButton: false,
        rightStickButton: false,
        dpadUp: false,
        dpadDown: false,
        dpadLeft: false,
        dpadRight: false,
        home: false,
      };

      gamepad.buttons.forEach((button, index) => {
        const buttonName =
          GAMEPAD_BUTTON_MAPPING[index as keyof typeof GAMEPAD_BUTTON_MAPPING];
        if (buttonName) {
          if (buttonName === 'lt' || buttonName === 'rt') {
            buttons[buttonName] = button.value * config.sensitivity.triggers;
          } else if (buttonName in buttons) {
            (buttons as any)[buttonName] = button.pressed;
          }
        }
      });

      setGamepadState({
        connected: true,
        leftStick: { x: leftX, y: leftY },
        rightStick: { x: rightX, y: rightY },
        buttons,
      });
    }

    animationFrameId.current = requestAnimationFrame(pollGamepad);
  }, [config]);

  useEffect(() => {
    const handleGamepadConnected = (e: GamepadEvent) => {
      console.log(`Gamepad connected: ${e.gamepad.id}`);
      gamepadIndex.current = e.gamepad.index;
      // Immediately update state to show connection
      setGamepadState((prev) => ({ ...prev, connected: true }));
    };

    const handleGamepadDisconnected = (e: GamepadEvent) => {
      console.log(`Gamepad disconnected: ${e.gamepad.id}`);
      if (gamepadIndex.current === e.gamepad.index) {
        gamepadIndex.current = null;
        setGamepadState((prev) => ({ ...prev, connected: false }));
      }
    };

    // Check for already connected gamepads on mount
    const checkInitialGamepads = () => {
      const gamepads = navigator.getGamepads();
      for (let i = 0; i < gamepads.length; i++) {
        const gamepad = gamepads[i];
        if (gamepad) {
          console.log(`Found existing gamepad: ${gamepad.id}`);
          gamepadIndex.current = i;
          setGamepadState((prev) => ({ ...prev, connected: true }));
          break;
        }
      }
    };

    checkInitialGamepads();

    window.addEventListener('gamepadconnected', handleGamepadConnected);
    window.addEventListener('gamepaddisconnected', handleGamepadDisconnected);

    animationFrameId.current = requestAnimationFrame(pollGamepad);

    return () => {
      window.removeEventListener('gamepadconnected', handleGamepadConnected);
      window.removeEventListener(
        'gamepaddisconnected',
        handleGamepadDisconnected
      );
      if (animationFrameId.current !== null) {
        cancelAnimationFrame(animationFrameId.current);
      }
    };
  }, [pollGamepad]);

  return gamepadState;
};
