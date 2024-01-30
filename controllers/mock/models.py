from pydantic import BaseModel


class Position(BaseModel):
    x: float
    y: float
    z: float


class QuaternionOrientation(BaseModel):
    q1: float
    q2: float
    q3: float
    q4: float


class Pose(BaseModel):
    position: Position
    orientation: QuaternionOrientation
