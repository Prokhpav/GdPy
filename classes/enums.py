from enum import IntEnum


class Triggered(IntEnum):
    Coord = 0
    Touch = 1
    Spawn = 2
    TouchMulti = 3
    SpawnMulti = 4

class Easing(IntEnum):
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

class Lock(IntEnum):
    No = 0
    Player = 1
    Camera = 2

class StopMode(IntEnum):
    Stop = 0
    Pause = 1
    Resume = 2

class PickupMode(IntEnum):
    Add = 0
    Multiply = 1
    Divide = 2
    Override = 3

class Comparison(IntEnum):
    Equals = 0
    Larger = 1
    Smaller = 2

class TextAlign(IntEnum):
    Center = 0
    Left = 1
    Right = 2

class CounterMode(IntEnum):
    Normal = 0
    MainTime = -1
    Points = -2
    Attempts = -3

class ToggleMode(IntEnum):
    Change = 0
    On = 1
    Off = 2

class PlayerOnly(IntEnum):
    Both = 0
    P1 = 1
    P2 = 2

class CollisionPlayer(IntEnum):
    No = 0
    P1 = 1
    P2 = 2
    P = 3  # any player
    PP = 4  # collision between players
