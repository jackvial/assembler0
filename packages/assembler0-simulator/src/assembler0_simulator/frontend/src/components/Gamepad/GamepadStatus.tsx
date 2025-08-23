import React from 'react';
import { GamepadState } from '../../types/gamepad';
import { THEME_COLORS } from '../../constants/theme';

interface GamepadStatusProps {
  gamepadState: GamepadState;
}

export const GamepadStatus: React.FC<GamepadStatusProps> = ({
  gamepadState,
}) => {
  return (
    <div
      style={{
        position: 'absolute',
        top: '10px',
        right: '10px',
        padding: '10px',
        backgroundColor: gamepadState.connected
          ? THEME_COLORS.BEAVER
          : THEME_COLORS.ROSEWOOD,
        color: 'white',
        borderRadius: '5px',
        fontFamily: 'monospace',
        fontSize: '14px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
        zIndex: 1000,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <div
          style={{
            width: '10px',
            height: '10px',
            borderRadius: '50%',
            backgroundColor: gamepadState.connected
              ? THEME_COLORS.BEAVER
              : THEME_COLORS.METALLIC_RED,
            animation: gamepadState.connected ? 'pulse 2s infinite' : 'none',
          }}
        />
        <span>
          Gamepad: {gamepadState.connected ? 'Connected' : 'Disconnected'}
        </span>
      </div>
      <style>{`
        @keyframes pulse {
          0% { opacity: 1; }
          50% { opacity: 0.5; }
          100% { opacity: 1; }
        }
      `}</style>
    </div>
  );
};
