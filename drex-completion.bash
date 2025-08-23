#!/bin/bash
# Bash completion for drex command

_drex_completion() {
    local cur prev words cword
    _init_completion || return

    # Top-level commands
    local top_commands="studio dataset robot wandb --help -h help"
    
    # Studio subcommands
    local studio_commands="start"
    
    # Dataset subcommands
    local dataset_commands="stats"
    
    # Robot subcommands
    local robot_commands="run"
    
    # Wandb subcommands
    local wandb_commands="download"
    
    # Common options
    local common_options="--help -h"
    local wandb_options="--base-dir"
    local robot_run_options="--robot-port --robot-id --screwdriver-camera --side-camera --top-camera --camera-width --camera-height --camera-fps --duration --fps --device --screwdriver-current-limit --clutch-ratio --clutch-cooldown-s --base-dir"

    case $cword in
        1)
            # First argument: top-level commands
            COMPREPLY=($(compgen -W "$top_commands" -- "$cur"))
            ;;
        2)
            # Second argument: depends on first
            case $prev in
                studio)
                    COMPREPLY=($(compgen -W "$studio_commands" -- "$cur"))
                    ;;
                dataset)
                    COMPREPLY=($(compgen -W "$dataset_commands" -- "$cur"))
                    ;;
                robot)
                    COMPREPLY=($(compgen -W "$robot_commands" -- "$cur"))
                    ;;
                wandb)
                    COMPREPLY=($(compgen -W "$wandb_commands" -- "$cur"))
                    ;;
                *)
                    COMPREPLY=()
                    ;;
            esac
            ;;
        3)
            # Third argument: depends on first command
            local command="${words[1]}"
            local subcommand="${words[2]}"
            
            if [[ "$command" == "studio" ]]; then
                # Studio subcommand handling
                case $subcommand in
                start)
                    COMPREPLY=($(compgen -W "--port $common_options" -- "$cur"))
                    ;;
                *)
                    COMPREPLY=()
                    ;;
                esac
            elif [[ "$command" == "dataset" ]]; then
                # Dataset subcommand handling
                case $subcommand in
                stats)
                    # First positional argument is the repo_id
                    # No specific completion for repo IDs
                    COMPREPLY=($(compgen -W "$common_options" -- "$cur"))
                    ;;
                *)
                    COMPREPLY=()
                    ;;
                esac
            elif [[ "$command" == "robot" ]]; then
                # Robot subcommand handling
                case $subcommand in
                run)
                    # First positional argument is required wandb_weights_path, no completion for that
                    COMPREPLY=($(compgen -W "$robot_run_options $common_options" -- "$cur"))
                    ;;
                *)
                    COMPREPLY=()
                    ;;
                esac
            elif [[ "$command" == "wandb" ]]; then
                # Wandb subcommand handling
                case $subcommand in
                download)
                    # First positional argument is required artifact_name, no completion for that
                    COMPREPLY=($(compgen -W "$wandb_options $common_options" -- "$cur"))
                    ;;
                *)
                    COMPREPLY=()
                    ;;
                esac
            fi
            ;;
        *)
            # Fourth argument and beyond: options based on subcommand
            local subcommand="${words[2]}"
            case $subcommand in
                download)
                    case $prev in
                        --base-dir)
                            # Directory completion for base directory
                            COMPREPLY=($(compgen -d -- "$cur"))
                            ;;
                        *)
                            COMPREPLY=($(compgen -W "$wandb_options $common_options" -- "$cur"))
                            ;;
                    esac
                    ;;
                run)
                    # Handle robot run command options
                    case $prev in
                        --robot-port|--screwdriver-camera|--side-camera|--top-camera)
                            # Device file completion
                            COMPREPLY=($(compgen -f -X '!*/dev/video*' -- "$cur") $(compgen -f -X '!*/dev/servo*' -- "$cur"))
                            ;;
                        --device)
                            # Device options
                            COMPREPLY=($(compgen -W "cuda cpu" -- "$cur"))
                            ;;
                        --camera-width)
                            # Common widths
                            COMPREPLY=($(compgen -W "640 800 1024 1280 1920" -- "$cur"))
                            ;;
                        --camera-height)
                            # Common heights
                            COMPREPLY=($(compgen -W "480 600 768 720 1080" -- "$cur"))
                            ;;
                        --camera-fps|--fps)
                            # Common FPS values
                            COMPREPLY=($(compgen -W "15 20 24 25 30 60" -- "$cur"))
                            ;;
                        --duration)
                            # Common durations
                            COMPREPLY=($(compgen -W "30 60 120 180 300" -- "$cur"))
                            ;;
                        --screwdriver-current-limit)
                            # Common current limits
                            COMPREPLY=($(compgen -W "200 250 300 350 400" -- "$cur"))
                            ;;
                        --clutch-ratio)
                            # Common clutch ratios
                            COMPREPLY=($(compgen -W "0.3 0.4 0.5 0.6 0.7" -- "$cur"))
                            ;;
                        --clutch-cooldown-s)
                            # Common cooldown values
                            COMPREPLY=($(compgen -W "0.5 1.0 1.5 2.0" -- "$cur"))
                            ;;
                        --base-dir)
                            # Directory completion
                            COMPREPLY=($(compgen -d -- "$cur"))
                            ;;
                        *)
                            # Check if command is for robot run
                            if [[ "${words[1]}" == "robot" && "${words[2]}" == "run" ]]; then
                                COMPREPLY=($(compgen -W "$robot_run_options $common_options" -- "$cur"))
                            else
                                COMPREPLY=()
                            fi
                            ;;
                    esac
                    ;;
                *)
                    COMPREPLY=()
                    ;;
            esac
            ;;
    esac
}

# Register the completion function
complete -F _drex_completion drex