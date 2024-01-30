import os
import json
import socket
from typing_extensions import Callable

from controllers.mock.models import Pose


class MockServer:
    def __init__(self, port: int = 5000) -> None:
        self.port = int(os.environ.get("PORT", str(port)))

        self.connection = socket.socket()
        # next line allows for port reuse
        self.connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.connection.bind(("", self.port))
        self.function_dict = {
            "01": self.move_tcp,
            "02": self.set_joints,
            "04": self.get_joints,
            "06": self.set_tool,
        }

    def run(self) -> None:
        self.connection.listen(5)
        print(f"Server listening on port: {self.port}")
        self.connection, addr = self.connection.accept()
        self.connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        with self.connection:
            print(f"Accepted connection from: {addr}")
            while True:
                data = self.connection.recv(4096)
                if not data:
                    continue
                message = str(data, encoding="utf-8")
                print(f"Message recieved: {message}")
                action, parameters = self.parse_message(message)

                if action is None:
                    self.connection.send(b"!")
                    continue

                fn = self.get_function(action)
                if fn is None:
                    self.connection.send(b"!")
                    continue

                if len(parameters):
                    fn(parameters)
                else:
                    fn()

                self.connection.send(b"#")

    def parse_message(self, message: str) -> tuple[str | None, list]:
        if not len(message):
            print("[ERROR] Invalid instruction, empty message")
            return None, []

        if message[-1] != "#":
            print("[ERROR] Invalid instruction, wrong format")
            return None, []

        instruction = message[:-1].split()
        action, parameters = instruction[0], instruction[1:]
        return action, parameters

    def get_function(self, action: str) -> Callable[[any], None] | None:
        if action not in self.function_dict.keys():
            print(f"[ERROR] Invalid action {action}")
            return None

        return self.function_dict[action]

    def get_joints(self) -> None:
        """
        Returns the current angles of the robots joints, in degrees.
        """
        print("Recieved get_joints action")

    def set_joints(self, joints: list) -> None:
        """
        Executes a move immediately, from current joint angles,
        to 'joints', in degrees.
        """
        print(f"Recieved set_joints action with parameters: {joints}")

    def set_tool(self, tool: list = [[0, 0, 0], [1, 0, 0, 0]]) -> None:
        print(f"Recieved set_tool action with parameters: {tool}")

    def move_tcp(self, pose: Pose) -> None:
        print(f"Recieved move_tcp action with parameters: {json.dumps(pose)}")


if __name__ == "__main__":
    server = MockServer()
    server.run()
