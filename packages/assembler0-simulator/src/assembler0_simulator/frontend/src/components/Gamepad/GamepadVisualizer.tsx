import React from 'react';
import { Card } from 'antd';
import { GamepadState } from '../../types/gamepad';
import { THEME_COLORS } from '../../constants/theme';

interface GamepadVisualizerProps {
  gamepadState: GamepadState;
  show: boolean;
}

export const GamepadVisualizer: React.FC<GamepadVisualizerProps> = ({
  gamepadState,
  show,
}) => {
  if (!show || !gamepadState.connected) return null;

  const stickStyle = (x: number, y: number) => ({
    transform: `translate(${x * 20}px, ${y * 20}px)`,
    transition: 'transform 0.1s ease-out',
  });

  const buttonStyle = (pressed: boolean) => ({
    backgroundColor: pressed ? THEME_COLORS.BEAVER : THEME_COLORS.DARK_LIVER,
    transition: 'background-color 0.1s',
  });

  const triggerStyle = (value: number) => ({
    height: `${value * 100}%`,
    backgroundColor:
      value > 0 ? THEME_COLORS.METALLIC_RED : THEME_COLORS.DARK_CHARCOAL,
    transition: 'height 0.1s, background-color 0.1s',
  });

  return (
    <Card title='Gamepad Input' style={{ width: '100%' }}>
      <div
        style={{
          color: THEME_COLORS.TEXT_PRIMARY,
          fontFamily: 'monospace',
          fontSize: '12px',
        }}
      >
        <div
          style={{
            marginBottom: '15px',
            fontSize: '14px',
            fontWeight: 'bold',
            display: 'none',
          }}
        >
          Gamepad Input
          {gamepadState.buttons.rb && (
            <span
              style={{
                marginLeft: '10px',
                padding: '2px 8px',
                backgroundColor: THEME_COLORS.ROSEWOOD_30,
                border: `1px solid ${THEME_COLORS.ROSEWOOD}`,
                borderRadius: '3px',
                fontSize: '12px',
                fontWeight: 'normal',
              }}
            >
              PRECISION MODE
            </span>
          )}
        </div>

        <div style={{ display: 'flex', gap: '30px' }}>
          {/* Left Stick */}
          <div style={{ textAlign: 'center' }}>
            <div style={{ marginBottom: '5px' }}>Left Stick</div>
            <div
              style={{
                width: '60px',
                height: '60px',
                backgroundColor: THEME_COLORS.DARK_CHARCOAL,
                borderRadius: '50%',
                position: 'relative',
                border: '2px solid #555',
              }}
            >
              <div
                style={{
                  width: '20px',
                  height: '20px',
                  backgroundColor: THEME_COLORS.METALLIC_RED,
                  borderRadius: '50%',
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  marginLeft: '-10px',
                  marginTop: '-10px',
                  ...stickStyle(
                    gamepadState.leftStick.x,
                    gamepadState.leftStick.y
                  ),
                }}
              />
            </div>
            <div style={{ marginTop: '5px', fontSize: '10px' }}>
              X: {gamepadState.leftStick.x.toFixed(2)}
              <br />
              Y: {gamepadState.leftStick.y.toFixed(2)}
            </div>
          </div>

          {/* Right Stick */}
          <div style={{ textAlign: 'center' }}>
            <div style={{ marginBottom: '5px' }}>Right Stick</div>
            <div
              style={{
                width: '60px',
                height: '60px',
                backgroundColor: THEME_COLORS.DARK_CHARCOAL,
                borderRadius: '50%',
                position: 'relative',
                border: '2px solid #555',
              }}
            >
              <div
                style={{
                  width: '20px',
                  height: '20px',
                  backgroundColor: THEME_COLORS.METALLIC_RED,
                  borderRadius: '50%',
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  marginLeft: '-10px',
                  marginTop: '-10px',
                  ...stickStyle(
                    gamepadState.rightStick.x,
                    gamepadState.rightStick.y
                  ),
                }}
              />
            </div>
            <div style={{ marginTop: '5px', fontSize: '10px' }}>
              X: {gamepadState.rightStick.x.toFixed(2)}
              <br />
              Y: {gamepadState.rightStick.y.toFixed(2)}
            </div>
          </div>

          {/* Buttons */}
          <div>
            <div style={{ marginBottom: '5px' }}>Buttons</div>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(4, 25px)',
                gap: '5px',
              }}
            >
              <div
                style={{
                  width: '25px',
                  height: '25px',
                  borderRadius: '3px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  ...buttonStyle(gamepadState.buttons.y),
                }}
              >
                Y
              </div>
              <div
                style={{
                  width: '25px',
                  height: '25px',
                  borderRadius: '3px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  ...buttonStyle(gamepadState.buttons.b),
                }}
              >
                B
              </div>
              <div
                style={{
                  width: '25px',
                  height: '25px',
                  borderRadius: '3px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  ...buttonStyle(gamepadState.buttons.a),
                }}
              >
                A
              </div>
              <div
                style={{
                  width: '25px',
                  height: '25px',
                  borderRadius: '3px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  ...buttonStyle(gamepadState.buttons.x),
                }}
              >
                X
              </div>
            </div>

            <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
              <div
                style={{
                  padding: '2px 8px',
                  borderRadius: '3px',
                  ...buttonStyle(gamepadState.buttons.lb),
                }}
              >
                LB
              </div>
              <div
                style={{
                  padding: '2px 8px',
                  borderRadius: '3px',
                  ...buttonStyle(gamepadState.buttons.rb),
                }}
              >
                RB
              </div>
            </div>
          </div>

          {/* Triggers */}
          <div>
            <div style={{ marginBottom: '5px' }}>Triggers</div>
            <div style={{ display: 'flex', gap: '10px' }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '10px', marginBottom: '3px' }}>LT</div>
                <div
                  style={{
                    width: '30px',
                    height: '60px',
                    backgroundColor: THEME_COLORS.DARK_CHARCOAL,
                    borderRadius: '3px',
                    position: 'relative',
                    overflow: 'hidden',
                  }}
                >
                  <div
                    style={{
                      position: 'absolute',
                      bottom: 0,
                      width: '100%',
                      ...triggerStyle(gamepadState.buttons.lt),
                    }}
                  />
                </div>
                <div style={{ fontSize: '10px', marginTop: '3px' }}>
                  {gamepadState.buttons.lt.toFixed(2)}
                </div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '10px', marginBottom: '3px' }}>RT</div>
                <div
                  style={{
                    width: '30px',
                    height: '60px',
                    backgroundColor: THEME_COLORS.DARK_CHARCOAL,
                    borderRadius: '3px',
                    position: 'relative',
                    overflow: 'hidden',
                  }}
                >
                  <div
                    style={{
                      position: 'absolute',
                      bottom: 0,
                      width: '100%',
                      ...triggerStyle(gamepadState.buttons.rt),
                    }}
                  />
                </div>
                <div style={{ fontSize: '10px', marginTop: '3px' }}>
                  {gamepadState.buttons.rt.toFixed(2)}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Control Instructions */}
        <div
          style={{
            marginTop: '15px',
            padding: '10px',
            backgroundColor: THEME_COLORS.DARK_LIVER_20,
            border: `1px solid ${THEME_COLORS.DARK_LIVER_50}`,
            borderRadius: '5px',
            fontSize: '11px',
            lineHeight: '1.4',
          }}
        >
          <strong>Controls:</strong>
          <div style={{ marginTop: '5px' }}>
            • Left Stick: X/Y Movement
            <br />
            • Right Stick Y: Z Movement (Up/Down)
            <br />
            • Right Stick X: Wrist Rotation
            <br />
            • RT/LT: Open/Close Gripper
            <br />• RB: Hold for Precision Mode (Slow)
          </div>
        </div>

        {/* D-Pad */}
        <div style={{ marginTop: '15px' }}>
          <div style={{ marginBottom: '5px' }}>D-Pad</div>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(3, 25px)',
              gap: '2px',
            }}
          >
            <div />
            <div
              style={{
                width: '25px',
                height: '25px',
                borderRadius: '3px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                ...buttonStyle(gamepadState.buttons.dpadUp),
              }}
            >
              ↑
            </div>
            <div />
            <div
              style={{
                width: '25px',
                height: '25px',
                borderRadius: '3px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                ...buttonStyle(gamepadState.buttons.dpadLeft),
              }}
            >
              ←
            </div>
            <div
              style={{
                width: '25px',
                height: '25px',
                borderRadius: '3px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: THEME_COLORS.DARK_CHARCOAL,
              }}
            >
              ●
            </div>
            <div
              style={{
                width: '25px',
                height: '25px',
                borderRadius: '3px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                ...buttonStyle(gamepadState.buttons.dpadRight),
              }}
            >
              →
            </div>
            <div />
            <div
              style={{
                width: '25px',
                height: '25px',
                borderRadius: '3px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                ...buttonStyle(gamepadState.buttons.dpadDown),
              }}
            >
              ↓
            </div>
            <div />
          </div>
        </div>
      </div>
    </Card>
  );
};
