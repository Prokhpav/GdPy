from enum import IntEnum
from attrs import define

from classes.gd_id import Group


class MyIntEnum(IntEnum):
    def __repr__(self):
        return f'{self.__class__.__name__}.{self.name}'


@define(slots=True, repr=False)
class HSV:
    h: int = 0
    s: float = 0.0
    v: float = 0.0
    absoluteSaturation: bool = False
    absoluteBrightness: bool = False

    def __repr__(self):
        return f'{self.__class__.__name__}({self.h}, {self.s:.2f}, {self.v:.2f}, {self.absoluteSaturation}, {self.absoluteBrightness})'


class Triggered(MyIntEnum):
    Coord = 0
    Touch = 1
    Spawn = 2
    TouchMulti = 3
    SpawnMulti = 4


class Easing(MyIntEnum):
    Default = 0
    EaseInOut = 1
    EaseIn = 2
    EaseOut = 3
    ElasticInOut = 4
    ElasticIn = 5
    ElasticOut = 6
    BounceInOut = 7
    BounceIn = 8
    BounceOut = 9
    ExponentialInOut = 10
    ExponentialIn = 11
    ExponentialOut = 12
    SineInOut = 13
    SineIn = 14
    SineOut = 15
    BackInOut = 16
    BackIn = 17
    BackOut = 18


class Lock(MyIntEnum):
    No = 0
    Player = 1
    Camera = 2


class StopMode(MyIntEnum):
    Stop = 0
    Pause = 1
    Resume = 2


class PickupMode(MyIntEnum):
    Add = 0
    Multiply = 1
    Divide = 2
    Override = 3


class Comparison(MyIntEnum):
    Equals = 0
    Larger = 1
    Smaller = 2


class TextAlign(MyIntEnum):
    Center = 0
    Left = 1
    Right = 2


class CounterMode(MyIntEnum):
    Normal = 0
    MainTime = -1
    Points = -2
    Attempts = -3


class ToggleMode(MyIntEnum):
    Change = 0
    On = 1
    Off = 2


class PlayerOnly(MyIntEnum):
    Both = 0
    P1 = 1
    P2 = 2


class CollisionPlayer(MyIntEnum):
    No = 0
    P1 = 1
    P2 = 2
    P = 3  # any player
    PP = 4  # collision between players


class XYOnly(MyIntEnum):
    Both = 0
    X = 1
    Y = 2


class TargetPlayer(MyIntEnum):
    No = 0
    P1 = 1
    P2 = 2


@define
class ClampRect:
    min_x: Group
    min_y: Group
    max_x: Group
    max_y: Group


class ItemType(MyIntEnum):
    No = 0
    Item = 1
    Timer = 2
    Points = 3
    MainTime = 4
    Attempts = 5


class ItemOperator(MyIntEnum):
    Override = 0
    Add = 1
    Sub = 2
    Mul = 3
    Div = 4


class SignFunc(MyIntEnum):
    No = 0
    Abs = 1
    Neg = 2


class RoundingFunc(MyIntEnum):
    No = 0
    Round = 1
    Floor = 2
    Ceil = 3


class ItemComparison(MyIntEnum):
    Equals = 0
    Less = 1
    LessEquals = 2
    Greater = 3
    GreaterEquals = 4
    NotEquals = 5
