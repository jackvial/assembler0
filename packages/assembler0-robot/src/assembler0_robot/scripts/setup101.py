from assembler0_robot.robots import SO101Follower, SO101FollowerConfig

def main():
    config = SO101FollowerConfig(
        port="/dev/ttyACM0",
        id="so101_follower",
    )
    follower = SO101Follower(config)
    follower.setup_motors()


if __name__ == "__main__":
    main()