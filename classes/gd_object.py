from typing import ClassVar

from attrs import define as define_gd  # to trick pycharm
from python.attrs_wrap import define_gd, field
from ignore_default import IgnoreDefault
from data.special_ids import special_ids
from .enums import *
from .gd_id import Group, Item, Block


@define_gd
class GdObjectBase(IgnoreDefault):
    x: float
    y: float


@define_gd
class AnyId(IgnoreDefault):
    id: int = field()


@define_gd
class SpecialId(IgnoreDefault):
    __id__: ClassVar[int] = None
    __all_classes__: ClassVar[dict[int, type]] = {}

    @property
    def id(self) -> int:
        return self.__class__.__id__

    @id.setter
    def id(self, id: int):
        raise AttributeError(f'id of {self.__class__.__name__} cannot be changed')

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if getattr(cls, '__id__', None) is None:
            cls.__id__ = special_ids.inv[cls.__name__]
            SpecialId.__all_classes__[cls.__id__] = cls


@define_gd
class GdObjectAnyId(GdObjectBase, AnyId):
    pass


HasId = GdObjectAnyId | SpecialId


@define_gd
class Trigger(GdObjectBase):
    triggered: Triggered = field(default=Triggered.Coord)


@define_gd
class TargetTrigger(Trigger):
    target: Group = field(factory=Group)


@define_gd
class Spawn(TargetTrigger, SpecialId):
    delay: float = 0.
    delay_variation: float = 0.
    remapping: dict[int, int] = field(factory=list)
    reset_remap: bool = False
    spawn_ordered: bool = False
    preview_disable: bool = False


@define_gd
class Toggle(TargetTrigger, SpecialId):
    activate: bool = False


@define_gd
class Stop(TargetTrigger, SpecialId):
    mode: StopMode = StopMode.Stop
    use_control_id: bool = False


@define_gd
class Pickup(Trigger, SpecialId):
    item: Item = field(factory=Item)
    count: int = 0
    modifier: float = 1.
    mode: PickupMode = PickupMode.Add


@define_gd
class Count(TargetTrigger, SpecialId):
    item: Item = field(factory=Item)
    count: int = 0
    activate: bool = False
    multi_activate: bool = False


@define_gd
class InstantCount(TargetTrigger, SpecialId):
    item: Item = field(factory=Item)
    count: int = 0
    comparison: Comparison = Comparison.Equals
    activate: bool = False


@define_gd
class CounterLabel(GdObjectBase, SpecialId):
    item: Item = field(factory=Item)
    text_align: TextAlign = TextAlign.Center
    seconds_only: bool = False
    as_timer: bool = False
    special_mode: CounterMode = CounterMode.Normal


@define_gd
class Touch(TargetTrigger, SpecialId):
    hold_mode: bool = False
    toggle_mode: ToggleMode = ToggleMode.Change
    player_only: PlayerOnly = PlayerOnly.Both
    dual_mode: bool = False


@define_gd  # do not use
class CollisionBase(TargetTrigger):
    block_a: Block = field(factory=Block)
    block_b: Block = field(factory=Block)
    player_collision: CollisionPlayer = CollisionPlayer.No  # replace block_a as player or collision between players


@define_gd
class Collision(CollisionBase, SpecialId):
    activate: bool = False
    on_exit: bool = False


@define_gd
class InstantCollision(CollisionBase, SpecialId):
    target_false: Group = field(factory=Group)


@define_gd
class CollisionState(TargetTrigger, SpecialId):  # player collision area
    triggered: Triggered = Triggered.TouchMulti
    target_exit: Group = field(factory=Group)


@define_gd
class CollisionBlock(GdObjectBase, SpecialId):
    block: Block = field(factory=Block)
    dynamic: bool = False


@define_gd
class ToggleBlock(TargetTrigger, SpecialId):
    triggered: Triggered = Triggered.Touch


@define_gd
class Reset(TargetTrigger, SpecialId):
    pass


#

@define_gd  # do not use
class EasingTrigger(TargetTrigger):
    duration: float = 0.
    easing: Easing = Easing.Default
    easing_rate: float = 2.


@define_gd
class Move(EasingTrigger, SpecialId):
    silent: bool = False  # platformer player not sticking to instant-moving block


@define_gd
class MoveBy(Move):
    move_x: int = 0  # 30 units per cell
    move_y: int = 0
    lock_x: Lock = Lock.No
    lock_y: Lock = Lock.No
    mod_x: float = 1.
    mod_y: float = 1.
    small_steps: bool = True  # show small steps in editor


@define_gd
class MoveTo(Move):
    center: Group = field(factory=Group)
    target_pos: Group = field(factory=Group)


@define_gd
class MoveAt(Move):
    center: Group = field(factory=Group)
    target_pos: Group = field(factory=Group)
    distance: int = 0  # 30 units per cell


@define_gd
class Rotate(EasingTrigger, SpecialId):
    center: Group = field(factory=Group)
    degrees: float = 0.
    lock_object_rotation: bool = False
    dynamic_rotation: bool = False


# @define_gd
# class RotateBy(Rotate):
#     pass
#
#
# @define_gd
# class RotateAt(Rotate):
#     pass
#
#
# @define_gd
# class RotateTo(Rotate):
#     pass
