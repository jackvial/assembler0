import { GamepadControlMessage } from '../types/gamepad';
import { getWebSocketConnection } from './websocket';

let messageQueue: GamepadControlMessage[] = [];
let isProcessingQueue = false;

export const sendGamepadControl = (message: GamepadControlMessage) => {
  const ws = getWebSocketConnection();

  if (!ws || ws.readyState !== WebSocket.OPEN) {
    console.warn('WebSocket not connected, queuing gamepad control message');
    messageQueue.push(message);
    return;
  }

  // Process any queued messages first
  if (messageQueue.length > 0 && !isProcessingQueue) {
    processMessageQueue();
  }

  try {
    ws.send(JSON.stringify(message));
  } catch (error) {
    console.error('Failed to send gamepad control message:', error);
    messageQueue.push(message);
  }
};

const processMessageQueue = () => {
  if (isProcessingQueue || messageQueue.length === 0) {
    return;
  }

  isProcessingQueue = true;
  const ws = getWebSocketConnection();

  if (!ws || ws.readyState !== WebSocket.OPEN) {
    isProcessingQueue = false;
    return;
  }

  while (messageQueue.length > 0) {
    const message = messageQueue.shift();
    if (message) {
      try {
        ws.send(JSON.stringify(message));
      } catch (error) {
        console.error('Failed to send queued message:', error);
        messageQueue.unshift(message);
        break;
      }
    }
  }

  isProcessingQueue = false;
};

export const calculateJointDeltas = (
  currentJoints: number[],
  deltas: { x: number; y: number; z: number }
): number[] => {
  // This is a simplified calculation
  // In a real implementation, you'd use proper kinematics
  const newJoints = [...currentJoints];

  // Map X delta to base rotation (joint 0)
  if (newJoints.length > 0) {
    newJoints[0] += deltas.x * 5; // Scale factor for rotation
  }

  // Map Y delta to arm extension (joint 1 or 2)
  if (newJoints.length > 1) {
    newJoints[1] += deltas.y * 5;
  }

  // Map Z delta to vertical movement (joint 2 or 3)
  if (newJoints.length > 2) {
    newJoints[2] += deltas.z * 5;
  }

  return newJoints;
};

export const mapGamepadToJointVelocities = (
  deltas: { x: number; y: number; z: number },
  numJoints: number
): number[] => {
  const velocities = new Array(numJoints).fill(0);

  // Map gamepad inputs to joint velocities
  if (numJoints > 0) velocities[0] = deltas.x * 1.0; // Base rotation
  if (numJoints > 1) velocities[1] = deltas.y * 1.0; // Arm extension
  if (numJoints > 2) velocities[2] = deltas.z * 1.0; // Vertical movement

  return velocities;
};

// Utility to check if gamepad API is supported
export const isGamepadSupported = (): boolean => {
  return 'getGamepads' in navigator;
};

// Get list of connected gamepads
export const getConnectedGamepads = (): (Gamepad | null)[] => {
  if (!isGamepadSupported()) {
    return [];
  }
  return Array.from(navigator.getGamepads());
};
