"""Main CLI entry point for drex."""

import click
from pathlib import Path
from rich.console import Console

console = Console()


@click.group()
@click.version_option()
@click.pass_context
def cli(ctx):
    """Drex - Assembler 0 robotics platform CLI."""
    # Store extension loader in context for commands that need it
    ctx.ensure_object(dict)
    from drex.extensions import ExtensionLoader
    ctx.obj['extension_loader'] = ExtensionLoader()


@cli.group()
def studio():
    """LeRobot Data Studio commands."""
    pass


@studio.command()
@click.option("--port", default=8000, help="Backend port (default: 8000)")
def start(port: int):
    """Start the LeRobot Data Studio (backend + frontend)."""
    import subprocess
    import os
    from pathlib import Path
    
    # Find the lerobot-data-studio package directory
    studio_dir = Path(__file__).parent.parent.parent.parent / "lerobot-data-studio"
    
    if not studio_dir.exists():
        console.print("❌ Error: lerobot-data-studio package not found. LeRobot Data Studio is now managed in a separate repository. You might need to clone it to that location see https://github.com/jackvial/lerobot-data-studio", style="red")
        console.print(f"Expected location: {studio_dir}", style="dim")
        return
    
    run_script = studio_dir / "run_dev.sh"
    if not run_script.exists():
        console.print("❌ Error: run_dev.sh not found in lerobot-data-studio", style="red")
        return
    
    console.print("🚀 Starting LeRobot Data Studio...", style="green")
    console.print(f"📁 Studio directory: {studio_dir}", style="dim")
    
    try:
        # Run the script in the studio directory
        subprocess.run([str(run_script)], cwd=studio_dir, check=True)
    except subprocess.CalledProcessError as e:
        console.print(f"❌ Error starting studio: {e}", style="red")
    except KeyboardInterrupt:
        console.print("\n👋 Studio stopped", style="yellow")


@cli.command()
@click.pass_context
def extensions(ctx):
    """List available extensions."""
    loader = ctx.obj.get('extension_loader')
    if not loader:
        from drex.extensions import ExtensionLoader
        loader = ExtensionLoader()
    
    extensions = loader.load_extensions()
    
    console.print("\n[bold]Available Extensions:[/bold]")
    if not extensions:
        console.print("  No extensions found in drex_extensions/", style="dim")
        console.print("  Extensions path:", loader.extensions_path or "not found", style="dim")
    else:
        for ext in extensions:
            console.print(f"  • {ext.name}: {ext.description}")
    console.print()

@cli.group()
def dataset():
    """Dataset management commands."""
    pass


@dataset.command()
@click.argument("repo_id", required=True)
def stats(repo_id: str):
    """Display statistics for a dataset from Hugging Face Hub.
    
    Downloads the dataset and shows:
    - Number of episodes
    - Task descriptions and counts
    - Episode length statistics (min, max, average)
    
    Example:
        drex dataset stats jackvial/screwdriver-panel-3-pos-clean-merged
    """
    from collections import Counter
    import numpy as np
    from lerobot.datasets.lerobot_dataset import LeRobotDataset
    
    console.print(f"📊 Loading dataset: {repo_id}", style="green")
    
    try:
        # Load the dataset
        dataset = LeRobotDataset(repo_id)
        
        # Get episode data
        episode_data_index = dataset.episode_data_index
        num_episodes = len(episode_data_index["from"])
        
        # Calculate episode lengths
        episode_lengths = []
        for i in range(num_episodes):
            start = episode_data_index["from"][i].item()
            end = episode_data_index["to"][i].item()
            length = end - start
            episode_lengths.append(length)
        
        # Get task descriptions
        task_counter = Counter()
        for i in range(num_episodes):
            if hasattr(dataset, 'meta') and hasattr(dataset.meta, 'episodes'):
                tasks = dataset.meta.episodes[i].get("tasks", [])
            else:
                # Try to get tasks from dataset info
                tasks = dataset.info.get("episodes", [{}])[i].get("tasks", [])
            
            for task in tasks:
                task_counter[task] += 1
        
        # Print statistics
        console.print("\n📈 Dataset Statistics:", style="bold blue")
        console.print(f"  Total episodes: {num_episodes}")
        console.print(f"  Total frames: {len(dataset)}")
        
        console.print("\n📏 Episode Length Statistics:", style="bold blue")
        console.print(f"  Min length: {min(episode_lengths)} frames")
        console.print(f"  Max length: {max(episode_lengths)} frames")
        console.print(f"  Average length: {np.mean(episode_lengths):.1f} frames")
        console.print(f"  Std deviation: {np.std(episode_lengths):.1f} frames")
        
        console.print("\n🏷️  Task Descriptions (unique per episode):", style="bold blue")
        if task_counter:
            for task, count in sorted(task_counter.items(), key=lambda x: -x[1]):
                console.print(f"  '{task}': {count} episodes")
        else:
            console.print("  No task descriptions found")
        
        # Print episode breakdown by task
        console.print("\n📋 Episodes by Task:", style="bold blue")
        task_to_episodes = {}
        for i in range(num_episodes):
            if hasattr(dataset, 'meta') and hasattr(dataset.meta, 'episodes'):
                tasks = dataset.meta.episodes[i].get("tasks", [])
            else:
                tasks = dataset.info.get("episodes", [{}])[i].get("tasks", [])
            
            for task in tasks:
                if task not in task_to_episodes:
                    task_to_episodes[task] = []
                task_to_episodes[task].append(i)
        
        for task, episodes in sorted(task_to_episodes.items()):
            console.print(f"\n  Task: '{task}'")
            console.print(f"    Episodes: {episodes[:10]}{'...' if len(episodes) > 10 else ''}")
            console.print(f"    Count: {len(episodes)}")
        
    except Exception as e:
        console.print(f"❌ Error loading dataset: {e}", style="red")
        raise click.ClickException(str(e))


@dataset.command()
@click.argument("repo_id", required=True)
def frames(repo_id: str):
    """Extract first and last 5 frames from each episode in a dataset.
    
    Saves frames to:
    - data/screwdriver-390-detector/start-frames/
    - data/screwdriver-390-detector/end-frames/
    
    Frame naming: screwdriver_390_start_{episode_index}_{frame_index}.png
    
    Example:
        drex dataset frames jackvial/screwdriver-390
    """
    from pathlib import Path
    from PIL import Image
    import numpy as np
    import torch
    from lerobot.datasets.lerobot_dataset import LeRobotDataset
    
    console.print(f"📥 Loading dataset: {repo_id}", style="green")
    
    try:
        # Load the dataset
        dataset = LeRobotDataset(repo_id)
        
        # Create output directories
        base_dir = Path("data/screwdriver-390-detector")
        start_frames_dir = base_dir / "start-frames"
        end_frames_dir = base_dir / "end-frames"
        
        start_frames_dir.mkdir(parents=True, exist_ok=True)
        end_frames_dir.mkdir(parents=True, exist_ok=True)
        
        console.print(f"📁 Output directories created:", style="dim")
        console.print(f"  - {start_frames_dir}", style="dim")
        console.print(f"  - {end_frames_dir}", style="dim")
        
        # Get episode data
        episode_data_index = dataset.episode_data_index
        num_episodes = len(episode_data_index["from"])
        
        console.print(f"\n🎬 Processing {num_episodes} episodes...", style="blue")
        
        # Get camera keys from dataset metadata
        if hasattr(dataset, 'meta') and hasattr(dataset.meta, 'camera_keys'):
            camera_keys = dataset.meta.camera_keys
        else:
            # Fallback: look for observation.image keys in the dataset
            sample_item = dataset.hf_dataset[0] if hasattr(dataset, 'hf_dataset') else dataset[0]
            camera_keys = [key for key in sample_item.keys() if key.startswith("observation.image.")]
        
        if not camera_keys:
            console.print("❌ No camera keys found in dataset", style="red")
            return
        
        # Look for side camera specifically
        side_camera_key = None
        for key in camera_keys:
            if 'side' in key.lower():
                side_camera_key = key
                break
        
        if not side_camera_key:
            console.print("❌ No side camera found in dataset", style="red")
            console.print(f"Available cameras: {camera_keys}", style="dim")
            return
        
        camera_key = side_camera_key
        # Extract camera name from key (e.g., "observation.images.side" -> "side")
        camera_name = camera_key.split('.')[-1]
        console.print(f"📷 Using camera: {camera_key}", style="dim")
        
        frames_saved = 0
        
        # Process each episode
        for episode_idx in range(num_episodes):
            start_idx = episode_data_index["from"][episode_idx].item()
            end_idx = episode_data_index["to"][episode_idx].item()
            episode_length = end_idx - start_idx
            
            console.print(f"\n📹 Episode {episode_idx}: {episode_length} frames", style="dim")
            
            # Extract first 5 frames
            for frame_idx in range(min(5, episode_length)):
                global_idx = start_idx + frame_idx
                frame_data = dataset[global_idx][camera_key]
                
                # Convert to PIL Image
                if torch.is_tensor(frame_data):
                    # Convert tensor to numpy
                    frame_data = frame_data.cpu().numpy()
                
                if isinstance(frame_data, np.ndarray):
                    # Assuming CHW format, convert to HWC
                    if frame_data.ndim == 3 and frame_data.shape[0] in [1, 3]:
                        frame_data = frame_data.transpose(1, 2, 0)
                    # Convert to uint8 if needed
                    if frame_data.dtype != np.uint8:
                        frame_data = (frame_data * 255).astype(np.uint8)
                    image = Image.fromarray(frame_data.squeeze())
                else:
                    image = frame_data
                
                # Save the frame
                filename = f"screwdriver_390_{camera_name}_start_{episode_idx}_{frame_idx}.png"
                filepath = start_frames_dir / filename
                image.save(filepath)
                frames_saved += 1
            
            # Extract last 5 frames
            start_of_last_5 = max(0, episode_length - 5)
            for i, frame_idx in enumerate(range(start_of_last_5, episode_length)):
                global_idx = start_idx + frame_idx
                frame_data = dataset[global_idx][camera_key]
                
                # Convert to PIL Image
                if torch.is_tensor(frame_data):
                    # Convert tensor to numpy
                    frame_data = frame_data.cpu().numpy()
                
                if isinstance(frame_data, np.ndarray):
                    # Assuming CHW format, convert to HWC
                    if frame_data.ndim == 3 and frame_data.shape[0] in [1, 3]:
                        frame_data = frame_data.transpose(1, 2, 0)
                    # Convert to uint8 if needed
                    if frame_data.dtype != np.uint8:
                        frame_data = (frame_data * 255).astype(np.uint8)
                    image = Image.fromarray(frame_data.squeeze())
                else:
                    image = frame_data
                
                # Save the frame
                filename = f"screwdriver_390_{camera_name}_end_{episode_idx}_{i}.png"
                filepath = end_frames_dir / filename
                image.save(filepath)
                frames_saved += 1
        
        console.print(f"\n✅ Frame extraction completed!", style="green")
        console.print(f"📊 Total frames saved: {frames_saved}", style="blue")
        console.print(f"  - Start frames: {start_frames_dir}", style="dim")
        console.print(f"  - End frames: {end_frames_dir}", style="dim")
        
    except Exception as e:
        console.print(f"❌ Error extracting frames: {e}", style="red")
        raise click.ClickException(str(e))


@cli.group()
def robot():
    """Robot inference commands."""
    pass


@robot.command()
@click.argument("wandb_weights_path", required=True)
@click.option("--robot-port", default="/dev/servo_5837053138", help="Robot servo port")
@click.option("--robot-id", default="koch_screwdriver_follower_20250802", help="Robot ID")
@click.option("--screwdriver-camera", default="/dev/video0", help="Screwdriver camera device")
@click.option("--side-camera", default="/dev/video2", help="Side camera device")
@click.option("--top-camera", default="/dev/video6", help="Top camera device")
@click.option("--camera-width", default=800, help="Camera width")
@click.option("--camera-height", default=600, help="Camera height")
@click.option("--camera-fps", default=30, help="Camera FPS")
@click.option("--duration", default=60, help="Inference duration in seconds")
@click.option("--fps", default=30, help="Inference FPS")
@click.option("--device", default="cuda", help="Device (cuda/cpu)")
@click.option("--screwdriver-current-limit", default=300, help="Screwdriver current limit")
@click.option("--clutch-ratio", default=0.5, help="Clutch ratio")
@click.option("--clutch-cooldown-s", default=1.0, help="Clutch cooldown in seconds")
@click.option("--base-dir", default="wandb_downloads", help="Base directory for downloaded artifacts")
def run(wandb_weights_path: str, robot_port: str, robot_id: str, screwdriver_camera: str,
        side_camera: str, top_camera: str, camera_width: int, camera_height: int,
        camera_fps: int, duration: int, fps: int, device: str,
        screwdriver_current_limit: int, clutch_ratio: float, clutch_cooldown_s: float,
        base_dir: str):
    """Run robot inference with Weights & Biases model weights.
    
    Downloads the weights if not already present, then runs inference.
    
    Example: drex robot run 'jackvial/assembler0-training/model-checkpoint-step-4000:v0'
    """
    import subprocess
    import re
    from pathlib import Path
    
    # Extract step number from artifact name
    step_match = re.search(r'step-(\d+)', wandb_weights_path)
    if not step_match:
        console.print("❌ Error: Could not extract step number from artifact name", style="red")
        console.print("💡 Expected format: '...model-checkpoint-step-4000:v0'", style="dim")
        return
    
    step_number = step_match.group(1)
    
    # Find project root
    current = Path.cwd()
    project_root = None
    
    while current != current.parent:
        pyproject_path = current / "pyproject.toml"
        if pyproject_path.exists():
            try:
                with open(pyproject_path, 'r') as f:
                    content = f.read()
                    if '[tool.uv.workspace]' in content and 'members = ["packages/*"]' in content:
                        project_root = current
                        break
            except Exception:
                pass
        current = current.parent
    
    if not project_root:
        project_root = Path.cwd()
    
    # Check if weights already exist
    # We need to determine the run_name first by checking existing downloads
    # or by downloading temporarily
    model_path = None
    
    # Look for existing downloads with this step number
    downloads_dir = project_root / base_dir
    if downloads_dir.exists():
        for run_dir in downloads_dir.iterdir():
            if run_dir.is_dir():
                step_dir = run_dir / step_number
                if step_dir.exists():
                    pretrained_model_path = step_dir / "pretrained_model"
                    if pretrained_model_path.exists():
                        model_path = pretrained_model_path
                        console.print(f"✅ Found existing weights at: {model_path}", style="green")
                        break
    
    # If not found, download the weights
    if not model_path:
        console.print(f"📥 Weights not found locally, downloading from W&B...", style="yellow")
        
        # Import the download function implementation
        import json
        import shutil
        import tempfile
        
        try:
            import wandb
        except ImportError:
            console.print("❌ Error: wandb package not installed", style="red")
            console.print("💡 Install with: pip install wandb", style="dim")
            return
        
        try:
            # Initialize W&B run
            run = wandb.init(project="artifact-download", job_type="download")
            
            # Create a temporary directory for initial download
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Download the artifact to temp directory
                artifact = run.use_artifact(wandb_weights_path, type='model')
                artifact_dir = Path(artifact.download(root=str(temp_path)))
                
                # The artifact downloads to a subdirectory, find the actual content directory
                actual_content_dir = artifact_dir
                
                # Look for train_config.json in the downloaded artifact
                train_config_path = None
                for path in artifact_dir.rglob("train_config.json"):
                    train_config_path = path
                    actual_content_dir = path.parent
                    break
                
                if not train_config_path or not train_config_path.exists():
                    console.print("⚠️  No train_config.json found in artifact", style="yellow")
                    run_name = "unknown_run"
                else:
                    with open(train_config_path, 'r') as f:
                        train_config = json.load(f)
                    
                    # Extract the last part of output_dir
                    output_dir = train_config.get("output_dir", "")
                    if output_dir:
                        run_name = Path(output_dir).name
                    else:
                        run_name = "unknown_run"
                
                # Create final directory structure
                final_base_dir = project_root / base_dir / run_name / step_number
                pretrained_model_dir = final_base_dir / "pretrained_model"
                
                pretrained_model_dir.mkdir(parents=True, exist_ok=True)
                
                # Check if the artifact has a pretrained_model subdirectory
                pretrained_model_src = actual_content_dir / "pretrained_model"
                
                if pretrained_model_src.exists() and pretrained_model_src.is_dir():
                    # Artifact has pretrained_model subdirectory
                    for item in pretrained_model_src.iterdir():
                        dest = pretrained_model_dir / item.name
                        if dest.exists():
                            if dest.is_dir():
                                shutil.rmtree(dest)
                            else:
                                dest.unlink()
                        shutil.move(str(item), str(dest))
                else:
                    # Artifact has flat structure, move everything to pretrained_model
                    for item in actual_content_dir.iterdir():
                        dest = pretrained_model_dir / item.name
                        if dest.exists():
                            if dest.is_dir():
                                shutil.rmtree(dest)
                            else:
                                dest.unlink()
                        shutil.move(str(item), str(dest))
                
                model_path = pretrained_model_dir
                console.print(f"✅ Weights downloaded to: {model_path}", style="green")
            
            # Finish the W&B run
            run.finish()
            
        except Exception as e:
            console.print(f"❌ Error downloading weights: {e}", style="red")
            console.print("💡 Make sure you're logged into W&B: wandb login", style="dim")
            return
    
    # Run inference with the model
    console.print(f"\n🤖 Starting robot inference with model: {model_path}", style="green")
    console.print(f"⏱️  Duration: {duration} seconds", style="dim")
    
    cmd = [
        "python", "-m", "assembler0_robot.scripts.inference",
        f"--robot_port={robot_port}",
        f"--robot_id={robot_id}",
        f"--model_path={model_path}",
        f"--screwdriver_camera={screwdriver_camera}",
        f"--side_camera={side_camera}",
        f"--top_camera={top_camera}",
        f"--camera_width={camera_width}",
        f"--camera_height={camera_height}",
        f"--camera_fps={camera_fps}",
        f"--duration={duration}",
        f"--fps={fps}",
        f"--device={device}",
        f"--screwdriver_current_limit={screwdriver_current_limit}",
        f"--clutch_ratio={clutch_ratio}",
        f"--clutch_cooldown_s={clutch_cooldown_s}"
    ]
    
    console.print(f"\n📋 Running command:", style="dim")
    console.print(" ".join(cmd), style="dim")
    
    try:
        subprocess.run(cmd, check=True)
        console.print(f"\n✅ Robot inference completed successfully!", style="green")
    except subprocess.CalledProcessError as e:
        console.print(f"\n❌ Error running inference: {e}", style="red")
    except KeyboardInterrupt:
        console.print(f"\n⚠️  Inference interrupted by user", style="yellow")


@cli.group()
def wandb():
    """Weights & Biases commands."""
    pass


@wandb.command()
@click.argument("artifact_name", required=True)
@click.option("--base-dir", default="wandb_downloads", help="Base directory for downloaded artifacts (default: wandb_downloads)")
def download(artifact_name: str, base_dir: str = "wandb_downloads"):
    """Download a model artifact from Weights & Biases.
    
    Example: drex wandb download 'jackvial/assembler0-training/model-checkpoint-step-4000:v0'
    
    Downloads to: wandb_downloads/<run_name>/<step>/pretrained_model/
    """
    import json
    import re
    import shutil
    import tempfile
    from pathlib import Path
    
    try:
        import wandb
    except ImportError:
        console.print("❌ Error: wandb package not installed", style="red")
        console.print("💡 Install with: pip install wandb", style="dim")
        return
    
    # Extract step number from artifact name
    step_match = re.search(r'step-(\d+)', artifact_name)
    if not step_match:
        console.print("❌ Error: Could not extract step number from artifact name", style="red")
        console.print("💡 Expected format: '...model-checkpoint-step-4000:v0'", style="dim")
        return
    
    step_number = step_match.group(1)
    
    # Find project root (look for pyproject.toml with workspace config)
    current = Path.cwd()
    project_root = None
    
    while current != current.parent:
        pyproject_path = current / "pyproject.toml"
        if pyproject_path.exists():
            try:
                with open(pyproject_path, 'r') as f:
                    content = f.read()
                    if '[tool.uv.workspace]' in content and 'members = ["packages/*"]' in content:
                        project_root = current
                        break
            except Exception:
                pass
        current = current.parent
    
    if not project_root:
        project_root = Path.cwd()
        console.print("⚠️  Could not find project root, using current directory", style="yellow")
    
    console.print(f"📥 Downloading W&B artifact: {artifact_name}", style="green")
    
    try:
        # Initialize W&B run
        run = wandb.init(project="artifact-download", job_type="download")
        
        # Create a temporary directory for initial download
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Download the artifact to temp directory
            artifact = run.use_artifact(artifact_name, type='model')
            artifact_dir = Path(artifact.download(root=str(temp_path)))
            
            # The artifact downloads to a subdirectory, find the actual content directory
            # W&B creates a directory structure like: temp_dir/artifacts/model-checkpoint-step-4000:v0/
            actual_content_dir = artifact_dir
            
            # Look for train_config.json in the downloaded artifact
            train_config_path = None
            for path in artifact_dir.rglob("train_config.json"):
                train_config_path = path
                actual_content_dir = path.parent
                break
            
            if not train_config_path or not train_config_path.exists():
                console.print("⚠️  No train_config.json found in artifact", style="yellow")
                run_name = "unknown_run"
            else:
                console.print(f"📄 Found train_config.json at: {train_config_path.relative_to(temp_path)}", style="dim")
                with open(train_config_path, 'r') as f:
                    train_config = json.load(f)
                
                # Extract the last part of output_dir
                output_dir = train_config.get("output_dir", "")
                if output_dir:
                    run_name = Path(output_dir).name
                    console.print(f"📊 Extracted run name: {run_name}", style="dim")
                else:
                    console.print("⚠️  No output_dir found in train_config.json", style="yellow")
                    run_name = "unknown_run"
            
            # Create final directory structure
            final_base_dir = project_root / base_dir / run_name / step_number
            pretrained_model_dir = final_base_dir / "pretrained_model"
            
            pretrained_model_dir.mkdir(parents=True, exist_ok=True)
            
            # Check if the artifact has a pretrained_model subdirectory
            pretrained_model_src = actual_content_dir / "pretrained_model"
            
            if pretrained_model_src.exists() and pretrained_model_src.is_dir():
                # Artifact has pretrained_model subdirectory
                console.print(f"📦 Found pretrained_model subdirectory", style="dim")
                
                # Move pretrained_model files
                for item in pretrained_model_src.iterdir():
                    dest = pretrained_model_dir / item.name
                    if dest.exists():
                        if dest.is_dir():
                            shutil.rmtree(dest)
                        else:
                            dest.unlink()
                    shutil.move(str(item), str(dest))
            else:
                # Artifact has flat structure, move everything to pretrained_model
                console.print(f"📦 Moving all files to pretrained_model directory", style="dim")
                for item in actual_content_dir.iterdir():
                    dest = pretrained_model_dir / item.name
                    if dest.exists():
                        if dest.is_dir():
                            shutil.rmtree(dest)
                        else:
                            dest.unlink()
                    shutil.move(str(item), str(dest))
            
            console.print(f"✅ Artifact downloaded successfully!", style="green")
            console.print(f"📁 Location: {final_base_dir}", style="blue")
            console.print(f"📊 Structure:", style="dim")
            console.print(f"  - {base_dir}/{run_name}/{step_number}/pretrained_model/", style="dim")
            
            # Show file count
            try:
                pretrained_files = list(pretrained_model_dir.iterdir())
                console.print(f"\n📈 Downloaded {len(pretrained_files)} files to pretrained_model/", style="dim")
            except Exception:
                pass
            
            # Show artifact info
            console.print(f"\n📊 Artifact info:", style="blue")
            console.print(f"  - Name: {artifact.name}", style="dim")
            console.print(f"  - Version: {artifact.version}", style="dim")
            console.print(f"  - Run: {run_name}", style="dim")
            console.print(f"  - Step: {step_number}", style="dim")
        
        # Finish the W&B run
        run.finish()
        
    except Exception as e:
        console.print(f"❌ Error downloading artifact: {e}", style="red")
        console.print("💡 Make sure you're logged into W&B: wandb login", style="dim")
        console.print("💡 Check that the artifact name is correct and accessible", style="dim")


def main():
    """Main entry point that loads extensions."""
    # Create base CLI
    cli_with_extensions = cli
    
    # Load and register extensions
    from drex.extensions import ExtensionLoader
    loader = ExtensionLoader()
    extensions = loader.load_extensions()
    
    for extension in extensions:
        try:
            command_group = extension.get_commands()
            cli_with_extensions.add_command(command_group)
        except Exception as e:
            console.print(f"Warning: Failed to register extension {extension.name}: {e}", style="yellow")
    
    # Run CLI
    cli_with_extensions()


if __name__ == "__main__":
    main()