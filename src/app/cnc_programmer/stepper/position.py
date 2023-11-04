from enum import Enum
import unittest


class Axis(Enum):
    X = 0
    Y = 1
    Z = 2


class PositionInSteps:
    def __init__(self, x: int = 0, y: int = 0, z: int = 0) -> None:
        self.pos: [int, int, int] = [x, y, z]

    def get(self, axis: Axis) -> int:
        return self.pos[axis.value]

    def set(self, axis: Axis, value: int) -> None:
        self.pos[axis.value] = value

    def increment(self, axis: Axis, increment: int) -> None:
        self.pos[axis.value] = self.pos[axis.value] + increment

    def to_mm(self, axis: Axis, steps_per_mm: int) -> float:
        return self.pos[axis.value]/steps_per_mm

    def __str__(self):
        return f'Pos_step({self.pos[0], self.pos[1], self.pos[2]})'


class TestPosition(unittest.TestCase):

    def test_set_increment(self):
        position = PositionInSteps(0, 0, 15)
        position.set(Axis.X, 5)
        position.set(Axis.Y, 10)
        position.increment(Axis.X, 10)
        position.increment(Axis.Y, 10)
        position.increment(Axis.Z, 10)
        self.assertEqual([position.get(Axis.X), position.get(Axis.Y), position.get(Axis.Z)], [15, 20, 25], "Should be [15, 20, 25]")

    def test_to_mm(self):
        position = PositionInSteps(15, 0, 15)
        self.assertEqual(position.to_mm(Axis.X, 400), 0.0375, "Should be 0.0375")
