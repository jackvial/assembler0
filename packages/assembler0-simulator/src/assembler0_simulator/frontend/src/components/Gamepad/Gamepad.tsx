import React, { useState } from 'react';
import { useGamepad } from '../../hooks/useGamepad';
import { useGamepadControl } from '../../hooks/useGamepadControl';
import { GamepadStatus } from './GamepadStatus';
import { GamepadVisualizer } from './GamepadVisualizer';
import { DEFAULT_GAMEPAD_CONFIG } from '../../types/gamepad';

export const Gamepad: React.FC = () => {
  const [config] = useState(DEFAULT_GAMEPAD_CONFIG);

  const gamepadState = useGamepad(config);
  useGamepadControl(gamepadState, config);

  return (
    <>
      <GamepadStatus gamepadState={gamepadState} />
      <GamepadVisualizer gamepadState={gamepadState} show={true} />
    </>
  );
};
