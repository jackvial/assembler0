from assembler0_robot.robots import SO101ScrewdriverFollower, SO101ScrewdriverFollowerConfig

def main():
    config = SO101ScrewdriverFollowerConfig(
        port="/dev/ttyACM0",
        id="so101_screwdriver_follower",
    )
    follower = SO101ScrewdriverFollower(config)
    follower.setup_motors()


if __name__ == "__main__":
    main()