# Assembler 0 Robot Simulator

Server side MuJoCo simulator with browser based frontend.

## Installation

### Prerequisites

**Note:** This simulator requires a Linux machine with an NVIDIA GPU for headless rendering.

This package is part of the Assembler 0 monorepo. Please see the [main repository README](../../README.md#installation) for setup instructions:
- Clone the repository
- Install UV package manager
- Set up virtual environment
- Install all dependencies with `uv sync`

### Additional Setup

After completing the main installation, install frontend dependencies:
```bash
cd packages/assembler0-simulator/src/assembler0_simulator/frontend
npm install
```

## Usage

### Start the backend server
```bash
cd src/assembler0_simulator/backend
python main.py
```

### Start the frontend development server
```bash
cd src/assembler0_simulator/frontend
npm run dev
```

Access the simulator at `http://localhost:1337`

## Requirements
- Linux with NVIDIA GPU (EGL rendering support required)