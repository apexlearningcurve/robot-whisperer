from abb import Robot

if __name__ == "__main__":
    robot = Robot("0.0.0.0", port_motion=5000)
    while True:
        input("Press enter to send")
        robot.send("hey")
