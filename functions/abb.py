"""
Michael Dawson-Haggerty

abb.py: contains classes and support functions which interact with an ABB Robot running our software stack (RAPID code module SERVER)


For functions which require targets (XYZ positions with quaternion orientation),
targets can be passed as [[XYZ], [Quats]] OR [XYZ, Quats]

"""

import socket
import json
import time
import inspect
from typing import Literal, List, Tuple
from collections import deque
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Robot:
    def __init__(
        self,
        ip: str = "192.168.125.1",
        port_motion: int = 5000,
        port_logger: int = 5001,
    ) -> None:
        self.delay = 0.08

        self.connect_motion((ip, port_motion))
        # log_thread = Thread(target = self.get_net,
        #                    args   = ((ip, port_logger))).start()

        self.ip = ip
        self.port_motion = port_motion
        self.set_units("millimeters", "degrees")
        self.set_tool()
        self.set_workobject()
        self.set_speed()
        self.set_zone()

    def connect_motion(self, remote: Tuple[str, str]) -> None:
        log.info("Attempting to connect to robot motion server at %s", str(remote))
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(2.5)
        self.sock.connect(remote)
        self.sock.settimeout(None)
        log.info("Connected to robot motion server at %s", str(remote))

    def connect_logger(self, remote: Tuple[str, str], maxlen: int = None):
        self.pose = deque(maxlen=maxlen)
        self.joints = deque(maxlen=maxlen)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(remote)
        s.setblocking(1)
        try:
            while True:
                data = map(float, s.recv(4096).split())
                if int(data[1]) == 0:
                    self.pose.append([data[2:5], data[5:]])
                # elif int(data[1]) == 1: self.joints.append([a[2:5], a[5:]])
        finally:
            s.shutdown(socket.SHUT_RDWR)

    def set_units(
        self,
        linear: Literal["millimeters", "meters", "inches"],
        angular: Literal["degrees", "radians"],
    ) -> None:
        units_l = {"millimeters": 1.0, "meters": 1000.0, "inches": 25.4}
        units_a = {"degrees": 1.0, "radians": 57.2957795}
        self.scale_linear = units_l[linear]
        self.scale_angle = units_a[angular]

    def set_cartesian(self, pose: List[list]) -> bytes | None:
        """
        Executes a move immediately from the current pose,
        to 'pose', with units of millimeters.
        """
        msg = "01 " + self.format_pose(pose)
        return self.send(msg)

    def set_joints(self, joints: List[float]) -> bytes | None:
        """
        Executes a move immediately, from current joint angles,
        to 'joints', in degrees.
        """
        if len(joints) != 6:
            return False
        msg = "02 "
        for joint in joints:
            msg += format(joint * self.scale_angle, "+08.2f") + " "
        msg += "#"
        return self.send(msg)

    def get_cartesian(self) -> List[float]:
        """
        Returns the current pose of the robot, in millimeters
        """
        msg = "03 #"
        data = self.send(msg).split()
        r = [float(s) for s in data]
        return [r[2:5], r[5:9]]

    def get_joints(self) -> List[float]:
        """
        Returns the current angles of the robots joints, in degrees.
        """
        msg = "04 #"
        data = self.send(msg).split()
        return [float(s) / self.scale_angle for s in data[2:8]]

    def get_external_axis(self) -> List[float]:
        """
        If you have an external axis connected to your robot controller
        (such as a FlexLifter 600, google it), this returns the joint angles
        """
        msg = "05 #"
        data = self.send(msg).split()
        return [float(s) for s in data[2:8]]

    def get_robotinfo(self) -> str:
        """
        Returns a robot- unique string, with things such as the
        robot's model number.
        Example output from and IRB 2400:
        ['24-53243', 'ROBOTWARE_5.12.1021.01', '2400/16 Type B']
        """
        msg = "98 #"
        data = str(self.send(msg))[5:].split("*")
        log.debug("get_robotinfo result: %s", str(data))
        return data

    def set_tool(self, tool: list = [[0, 0, 0], [1, 0, 0, 0]]) -> None:
        """
        Sets the tool centerpoint (TCP) of the robot.
        When you command a cartesian move,
        it aligns the TCP frame with the requested frame.

        Offsets are from tool0, which is defined at the intersection of the
        tool flange center axis and the flange face.
        """
        msg = "06 " + self.format_pose(tool)
        self.send(msg)
        self.tool = tool

    def load_json_tool(self, file_obj: str | dict) -> None:  # Check for dict type
        if isinstance(file_obj, str):
            file_obj = open(file_obj, "rb")
        tool = check_coordinates(json.load(file_obj))
        self.set_tool(tool)

    def get_tool(self) -> List[list]:
        log.debug("get_tool returning: %s", str(self.tool))
        return self.tool

    def set_workobject(self, work_obj: list = [[0, 0, 0], [1, 0, 0, 0]]) -> None:
        """
        The workobject is a local coordinate frame you can define on the robot,
        then subsequent cartesian moves will be in this coordinate frame.
        """
        msg = "07 " + self.format_pose(work_obj)
        self.send(msg)

    def set_speed(self, speed: list = [100, 50, 50, 50]) -> None:
        """
        speed: [robot TCP linear speed (mm/s), TCP orientation speed (deg/s),
                external axis linear, external axis orientation]
        """

        if len(speed) != 4:
            return False
        msg = "08 "
        msg += format(speed[0], "+08.1f") + " "
        msg += format(speed[1], "+08.2f") + " "
        msg += format(speed[2], "+08.1f") + " "
        msg += format(speed[3], "+08.2f") + " #"
        self.send(msg)

    def set_zone(
        self,
        zone_key: Literal[
            "z0", "z1", "z5", "z10", "z15", "z20", "z30", "z50", "z100", "z200"
        ] = "z1",
        point_motion: bool = False,
        manual_zone: list = None,
    ) -> bool:
        """
        Sets the motion zone of the robot. This can also be thought of as
        the flyby zone, AKA if the robot is going from point A -> B -> C,
        how close do we have to pass by B to get to C

        zone_key: uses values from RAPID handbook (stored here in zone_dict)
        with keys 'z*', you should probably use these

        point_motion: go to point exactly, and stop briefly before moving on

        manual_zone = [pzone_tcp, pzone_ori, zone_ori]
        pzone_tcp: mm, radius from goal where robot tool centerpoint
                   is not rigidly constrained
        pzone_ori: mm, radius from goal where robot tool orientation
                   is not rigidly constrained
        zone_ori: degrees, zone size for the tool reorientation
        """
        zone_dict = {
            "z0": [0.3, 0.3, 0.03],
            "z1": [1, 1, 0.1],
            "z5": [5, 8, 0.8],
            "z10": [10, 15, 1.5],
            "z15": [15, 23, 2.3],
            "z20": [20, 30, 3],
            "z30": [30, 45, 4.5],
            "z50": [50, 75, 7.5],
            "z100": [100, 150, 15],
            "z200": [200, 300, 30],
        }

        if point_motion:
            zone = [0, 0, 0]
        elif manual_zone is not None and len(manual_zone) == 3:
            zone = manual_zone
        elif zone_key in zone_dict.keys():
            zone = zone_dict[zone_key]
        else:
            return False

        msg = "09 "
        msg += str(int(point_motion)) + " "
        msg += format(zone[0], "+08.4f") + " "
        msg += format(zone[1], "+08.4f") + " "
        msg += format(zone[2], "+08.4f") + " #"
        self.send(msg)

    def buffer_add(self, pose: List) -> None:
        """
        Appends single pose to the remote buffer
        Move will execute at current speed (which you can change between buffer_add calls)
        """
        msg = "30 " + self.format_pose(pose)
        self.send(msg)

    def buffer_set(self, pose_list: List[list]) -> bool:
        """
        Adds every pose in pose_list to the remote buffer
        """
        self.clear_buffer()
        for pose in pose_list:
            self.buffer_add(pose)
        if self.buffer_len() == len(pose_list):
            log.debug("Successfully added %i poses to remote buffer", len(pose_list))
            return True
        else:
            log.warn("Failed to add poses to remote buffer!")
            self.clear_buffer()
            return False

    def clear_buffer(self) -> bytes | None:
        msg = "31 #"
        data = self.send(msg)
        if self.buffer_len() != 0:
            log.warn("clear_buffer failed! buffer_len: %i", self.buffer_len())
            raise NameError("clear_buffer failed!")
        return data

    def buffer_len(self) -> int:
        """
        Returns the length (number of poses stored) of the remote buffer
        """
        msg = "32 #"
        data = self.send(msg).split()
        return int(float(data[2]))

    def buffer_execute(self) -> bytes | None:
        """
        Immediately execute linear moves to every pose in the remote buffer.
        """
        msg = "33 #"
        return self.send(msg)

    def set_external_axis(
        self, axis_unscaled: List = [-550, 0, 0, 0, 0, 0]
    ) -> bytes | bool | None:
        if len(axis_unscaled) != 6:
            return False
        msg = "34 "
        for axis in axis_unscaled:
            msg += format(axis, "+08.2f") + " "
        msg += "#"
        return self.send(msg)

    def move_circular(self, pose_onarc, pose_end) -> bytes | bool | None:
        """
        Executes a movement in a circular path from current position,
        through pose_onarc, to pose_end
        """
        msg_0 = "35 " + self.format_pose(pose_onarc)
        msg_1 = "36 " + self.format_pose(pose_end)

        data = self.send(msg_0).split()
        if data[1] != "1":
            log.warn("move_circular incorrect response, bailing!")
            return False
        return self.send(msg_1)

    def set_dio(self, value: int, id: int = 0) -> bytes | None:  # Check value type
        """
        A function to set a physical DIO line on the robot.
        For this to work you're going to need to edit the RAPID function
        and fill in the DIO you want this to switch.
        """
        msg = "97 " + str(int(bool(value))) + " #"
        return self.send(msg)

    def send(self, message: str, wait_for_response: bool = True) -> bytes | None:
        """
        Send a formatted message to the robot socket.
        if wait_for_response, we wait for the response and return it
        """
        caller = inspect.stack()[1][3]
        log.debug("%-14s sending: %s", caller, message)
        self.sock.sendto(message.encode(), (self.ip, self.port_motion))
        time.sleep(self.delay)
        if not wait_for_response:
            return
        data = self.sock.recv(4096)
        log.debug("%-14s recieved: %s", caller, data)
        return data

    def format_pose(self, pose: List) -> str:
        pose = check_coordinates(pose)
        msg = ""
        for cartesian in pose[0]:
            msg += format(cartesian * self.scale_linear, "+08.1f") + " "
        for quaternion in pose[1]:
            msg += format(quaternion, "+08.5f") + " "
        msg += "#"
        return msg

    def close(self) -> None:
        self.send("99 #", False)
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        log.info("Disconnected from ABB robot.")

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()


def check_coordinates(coordinates: List) -> List:
    if (
        (len(coordinates) == 2)
        and (len(coordinates[0]) == 3)
        and (len(coordinates[1]) == 4)
    ):
        return coordinates
    elif len(coordinates) == 7:
        return [coordinates[0:3], coordinates[3:7]]
    log.warn("Recieved malformed coordinate: %s", str(coordinates))
    raise NameError("Malformed coordinate!")


if __name__ == "__main__":
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)-7s (%(filename)s:%(lineno)3s) %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )
    handler_stream = logging.StreamHandler()
    handler_stream.setFormatter(formatter)
    handler_stream.setLevel(logging.DEBUG)
    log = logging.getLogger("abb")
    log.setLevel(logging.DEBUG)
    log.addHandler(handler_stream)