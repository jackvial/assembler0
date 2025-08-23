#!/usr/bin/env python3
"""Headless MuJoCo server with GPU rendering and web streaming."""

import asyncio
import base64
import json
import os
import cv2
from pathlib import Path
from typing import Optional

# Set up offscreen rendering before importing mujoco
# Use EGL for GPU-accelerated offscreen rendering
os.environ['MUJOCO_GL'] = 'egl'
# Try to use GPU 0 explicitly
os.environ['MUJOCO_EGL_DEVICE_ID'] = '0'

import mujoco
import numpy as np
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

from assembler0_simulator.backend.arm_configs import ArmConfig, get_arm_config, get_available_arms

class HeadlessMuJoCoServer:
    """MuJoCo simulation with headless GPU rendering."""
    
    def __init__(self, arm_config: ArmConfig, width: int = 640, height: int = 480):
        self.arm_config = arm_config
        model_path = Path(__file__).parent.parent / arm_config.model_path
        if not model_path.exists():
            # Fallback to default 6DOF if specified model doesn't exist
            print(f"Warning: Model path {model_path} not found, falling back to 6DOF")
            model_path = Path(__file__).parent.parent / "low_cost_robot_6dof" / "scene.xml"
        
        # Load model
        self.model = mujoco.MjModel.from_xml_path(str(model_path))
        self.data = mujoco.MjData(self.model)
        
        # Reset to home position if keyframe exists
        if self.model.nkey > 0:
            # Find 'home' keyframe or use first keyframe
            home_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_KEY, "home")
            if home_id < 0:
                home_id = 0  # Use first keyframe if 'home' not found
            mujoco.mj_resetDataKeyframe(self.model, self.data, home_id)
        
        self.width = width
        self.height = height
        
        # Create MuJoCo renderer - this should work with EGL backend
        try:
            self.renderer = mujoco.Renderer(self.model, height=height, width=width)
            print(f"Successfully created MuJoCo renderer with backend: {os.environ.get('MUJOCO_GL', 'default')}")
        except Exception as e:
            print(f"Failed to create renderer: {e}")
            raise
        
        # Set up camera from arm config
        self.cam = mujoco.MjvCamera()
        cam_config = arm_config.default_camera
        self.cam.lookat = np.array(cam_config['lookat'])
        self.cam.distance = cam_config['distance']
        self.cam.elevation = cam_config['elevation']
        self.cam.azimuth = cam_config['azimuth']
        
        self.control_values = {}
        
    def step(self):
        """Advance simulation by one timestep."""
        # Apply controls
        for name, value in self.control_values.items():
            actuator_id = mujoco.mj_name2id(
                self.model, mujoco.mjtObj.mjOBJ_ACTUATOR, name
            )
            if actuator_id >= 0:
                self.data.ctrl[actuator_id] = value
        
        # Step physics
        mujoco.mj_step(self.model, self.data)
        
    def render(self) -> bytes:
        """Render current state and return image as JPEG bytes."""
        # Update renderer with current simulation state
        self.renderer.update_scene(self.data, self.cam)
        
        # Render to numpy array
        pixels = self.renderer.render()
        
        # Convert RGB to JPEG bytes
        
        _, jpeg_bytes = cv2.imencode('.jpg', cv2.cvtColor(pixels, cv2.COLOR_RGB2BGR))
        return jpeg_bytes.tobytes()
    
    def get_state(self) -> dict:
        """Get current simulation state."""
        state = {
            'time': self.data.time,
            'qpos': self.data.qpos.tolist(),
            'qvel': self.data.qvel.tolist(),
        }
        
        # Add joint information
        joints = {}
        for i in range(self.model.njnt):
            name = mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_JOINT, i)
            if name:
                qpos_addr = self.model.jnt_qposadr[i]
                joints[name] = float(self.data.qpos[qpos_addr])
        state['joints'] = joints
        
        return state
    
    def set_control(self, control: dict):
        """Set control values."""
        self.control_values.update(control)
    
    def handle_gamepad_control(self, deltas: dict, gripper: Optional[str] = None, buttons: dict = None):
        """Handle gamepad control input using arm configuration mappings."""
        # Get all available joint names
        joint_names = self.get_joint_names()
        
        # Initialize control values if empty
        if not self.control_values:
            for name in joint_names:
                actuator_id = mujoco.mj_name2id(
                    self.model, mujoco.mjtObj.mjOBJ_ACTUATOR, name
                )
                if actuator_id >= 0:
                    self.control_values[name] = self.data.ctrl[actuator_id]
        
        joint_values = {}
        
        # Process joint mappings from arm config
        for joint_mapping in self.arm_config.joints:
            if joint_mapping.name not in self.control_values:
                continue
            
            # Get delta value based on control axis
            delta = 0.0
            if joint_mapping.control_axis == 'left_x':
                delta = deltas.get('x', 0)
            elif joint_mapping.control_axis == 'left_y':
                delta = deltas.get('y', 0)
            elif joint_mapping.control_axis == 'right_x':
                delta = deltas.get('wrist', 0)
            elif joint_mapping.control_axis == 'right_y':
                delta = deltas.get('z', 0)
            elif joint_mapping.control_axis == 'bumpers' and buttons:
                # Use bumpers for control (LB = negative, RB would be precision mode)
                # Only use LB for actual control since RB is for precision
                if buttons.get('lb', False):
                    delta = -0.1
                # Note: RB is used for precision mode, not for control
            elif joint_mapping.control_axis == 'dpad_x' and buttons:
                # D-pad left/right for control
                if buttons.get('dpadLeft', False):
                    delta = -0.1
                elif buttons.get('dpadRight', False):
                    delta = 0.1
            elif joint_mapping.control_axis == 'dpad_y' and buttons:
                # D-pad up/down for control
                if buttons.get('dpadUp', False):
                    delta = 0.1
                elif buttons.get('dpadDown', False):
                    delta = -0.1
            elif joint_mapping.control_axis == 'triggers':
                # L2/R2 triggers for continuous rotation (screwdriver)
                # These come through the gripper channel
                if gripper == 'open':  # R2 (RT) - clockwise
                    delta = 0.2  # Continuous rotation speed
                elif gripper == 'close':  # L2 (LT) - counter-clockwise
                    delta = -0.2  # Continuous rotation speed
            
            # Apply inversion if needed
            if joint_mapping.inverted:
                delta = -delta
            
            # Apply speed multiplier
            delta *= joint_mapping.speed_multiplier
            
            # Update joint value
            if abs(delta) > 0.001:  # Only update if there's meaningful input
                current_value = self.control_values.get(joint_mapping.name, 0)
                joint_values[joint_mapping.name] = current_value + delta
        
        # Handle gripper control (skip entirely if any joint uses triggers)
        has_trigger_control = any(
            j.control_axis == 'triggers' for j in self.arm_config.joints
        )
        
        if gripper and self.arm_config.gripper_joint and not has_trigger_control:
            gripper_joint = self.arm_config.gripper_joint
            if gripper_joint in self.control_values:
                if gripper == 'open':
                    joint_values[gripper_joint] = self.arm_config.gripper_open_position
                elif gripper == 'close':
                    joint_values[gripper_joint] = self.arm_config.gripper_close_position
                # 'stay' means don't change gripper
        
        # Apply joint limits
        for name, value in joint_values.items():
            # Get joint limits from model if available
            joint_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_JOINT, name)
            if joint_id >= 0 and self.model.jnt_limited[joint_id]:
                min_limit = self.model.jnt_range[joint_id][0]
                max_limit = self.model.jnt_range[joint_id][1]
                joint_values[name] = np.clip(value, min_limit, max_limit)
        
        # Update control values
        self.control_values.update(joint_values)
    
    def update_camera(self, camera_params: dict):
        """Update camera parameters."""
        if 'lookat' in camera_params:
            self.cam.lookat = np.array(camera_params['lookat'])
        if 'distance' in camera_params:
            self.cam.distance = camera_params['distance']
        if 'elevation' in camera_params:
            self.cam.elevation = camera_params['elevation']
        if 'azimuth' in camera_params:
            self.cam.azimuth = camera_params['azimuth']
    
    def get_joint_names(self):
        """Get list of joint names."""
        names = []
        for i in range(self.model.njnt):
            name = mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_JOINT, i)
            if name:
                names.append(name)
        return names
    
    def get_joint_info(self, joint_name: str):
        """Get detailed information about a joint."""
        joint_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_JOINT, joint_name)
        if joint_id < 0:
            return None
        
        qpos_addr = self.model.jnt_qposadr[joint_id]
        
        # Get joint limits if they exist
        has_limits = self.model.jnt_limited[joint_id]
        if has_limits:
            min_limit = self.model.jnt_range[joint_id][0]
            max_limit = self.model.jnt_range[joint_id][1]
        else:
            # Default range for unlimited joints
            min_limit = -3.14
            max_limit = 3.14
        
        return {
            "name": joint_name,
            "current_value": float(self.data.qpos[qpos_addr]),
            "min": float(min_limit),
            "max": float(max_limit),
            "has_limits": bool(has_limits)
        }


# Create FastAPI app
app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:1337"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global simulation server
sim_server: Optional[HeadlessMuJoCoServer] = None
current_arm_config: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Initialize simulation on startup."""
    global sim_server, current_arm_config
    # Check environment variable or default to 6DOF screwdriver version
    robot_version = os.environ.get('ROBOT_VERSION', '6dof_screwdriver').lower()
    
    # Map environment variable to config ID
    if robot_version == '6dof':
        config_id = 'low_cost_6dof'
    elif robot_version == '6dof_screwdriver':
        config_id = 'low_cost_6dof_screwdriver'
    elif robot_version == '5dof':
        config_id = 'low_cost_5dof'
    else:
        config_id = 'low_cost_6dof_screwdriver'  # Default to screwdriver
    
    # Get arm configuration
    arm_config = get_arm_config(config_id)
    if not arm_config:
        arm_config = get_arm_config('low_cost_6dof_screwdriver')  # Fallback to screwdriver
    
    print(f"Loading robot configuration: {arm_config.name}")
    sim_server = HeadlessMuJoCoServer(arm_config)
    current_arm_config = config_id


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    await websocket.accept()
    
    try:
        while True:
            sim_server.step()
            jpeg_bytes = sim_server.render()
            state = sim_server.get_state()
            message = {
                'type': 'frame',
                'image': base64.b64encode(jpeg_bytes).decode('utf-8'),
                'state': state
            }
            await websocket.send_json(message)
            
            # Check for incoming messages (non-blocking)
            try:
                # Set timeout to match simulation timestep
                data = await asyncio.wait_for(
                    websocket.receive_text(), 
                    timeout=sim_server.model.opt.timestep
                )
                
                msg = json.loads(data)
                if msg['type'] == 'control':
                    sim_server.set_control(msg['data'])
                elif msg['type'] == 'camera':
                    sim_server.update_camera(msg['data'])
                elif msg['type'] == 'gamepad_control':
                    sim_server.handle_gamepad_control(
                        msg.get('deltas', {'x': 0, 'y': 0, 'z': 0, 'wrist': 0}),
                        msg.get('gripper'),
                        msg.get('buttons', {})
                    )
                    
            except asyncio.TimeoutError:
                pass  # No message received, continue
            
            # Sleep to maintain real-time simulation
            await asyncio.sleep(sim_server.model.opt.timestep)
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()


@app.get("/api/status")
async def get_status():
    """Get simulation status."""
    if sim_server:
        return {
            "status": "running",
            "model_loaded": True,
            "timestep": sim_server.model.opt.timestep,
            "joints": list(sim_server.get_joint_names())
        }
    return {"status": "not_initialized", "model_loaded": False}


@app.get("/api/joints")
async def get_joints():
    """Get available joint information."""
    if not sim_server:
        return {"error": "Simulation not initialized"}
    
    joints = []
    for name in sim_server.get_joint_names():
        # Skip the red box joint from frontend controls
        if name == "red_box_joint":
            continue
        joint_info = sim_server.get_joint_info(name)
        joints.append(joint_info)
    
    return {"joints": joints}


@app.get("/api/arms")
async def get_arms():
    """Get available arm configurations."""
    arms = get_available_arms()
    return {
        "arms": arms,
        "current": current_arm_config
    }


@app.post("/api/arms/{arm_id}")
async def switch_arm(arm_id: str):
    """Switch to a different arm configuration."""
    global sim_server, current_arm_config
    
    arm_config = get_arm_config(arm_id)
    if not arm_config:
        return {"error": f"Unknown arm configuration: {arm_id}"}
    
    try:
        sim_server = HeadlessMuJoCoServer(arm_config)
        current_arm_config = arm_id
        
        return {
            "success": True,
            "arm": {
                "id": arm_config.id,
                "name": arm_config.name,
                "description": arm_config.description
            }
        }
    except Exception as e:
        print(f"Failed to switch arm: {e}")
        return {"error": f"Failed to switch arm: {str(e)}"}

app.mount("/", StaticFiles(directory=str(Path(__file__).parent.parent / "frontend" / "dist"), html=True), name="static")

def main():
    """Main entry point for the backend server."""
    uvicorn.run(app, host="0.0.0.0", port=1337)


if __name__ == "__main__":
    main()