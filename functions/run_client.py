from abb import Robot

if __name__ == "__main__":
    robot = Robot("0.0.0.0", port_motion=5000)
    input("Press enter to send")
    robot.get_joints()
    input("Press enter to send")
    robot.set_cartesian([[0, 0, 0], [1, 0, 0, 0]])
    input("Press enter to send")
    robot.send("hey")
