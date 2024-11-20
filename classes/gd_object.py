from typing import ClassVar

from attrs import define as define_gd  # to trick pycharm
from python.attrs_wrap import define_gd, field
from ignore_default import IgnoreDefault
from data.special_ids import special_ids
from .enums import *
from .gd_id import Group, Item, Block, Timer


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
    target: Group = Group.Empty


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
    item: Item = Item.Empty
    count: int = 0
    modifier: float = 1.
    mode: PickupMode = PickupMode.Add


@define_gd
class Count(TargetTrigger, SpecialId):
    item: Item = Item.Empty
    count: int = 0
    activate: bool = False
    multi_activate: bool = False


@define_gd
class InstantCount(TargetTrigger, SpecialId):
    item: Item = Item.Empty
    count: int = 0
    comparison: Comparison = Comparison.Equals
    activate: bool = False


@define_gd
class CounterLabel(GdObjectBase, SpecialId):
    item: Item = Item.Empty
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
    block_a: Block = Block.Empty
    block_b: Block = Block.Empty
    player_collision: CollisionPlayer = CollisionPlayer.No  # replace block_a as player or collision between players


@define_gd
class Collision(CollisionBase, SpecialId):
    activate: bool = False
    on_exit: bool = False


@define_gd
class InstantCollision(CollisionBase, SpecialId):
    target_false: Group = Group.Empty


@define_gd
class CollisionState(TargetTrigger, SpecialId):  # player collision area
    triggered: Triggered = Triggered.TouchMulti
    target_exit: Group = Group.Empty


@define_gd
class CollisionBlock(GdObjectBase, SpecialId):
    block: Block = Block.Empty
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
    center: Group = Group.Empty
    target_pos: Group = Group.Empty
    target_player: TargetPlayer = TargetPlayer.No
    mode: XYOnly = XYOnly.Both
    dynamic: bool = False


@define_gd
class MoveAt(Move):
    center: Group = Group.Empty
    target_pos: Group = Group.Empty
    target_player: TargetPlayer = TargetPlayer.No
    distance: int = 0  # 30 units per cell
    dynamic: bool = False


@define_gd
class Rotate(EasingTrigger, SpecialId):
    center: Group = Group.Empty
    degrees: float = 0.
    lock_object_rotation: bool = False


@define_gd
class RotateBy(Rotate):
    pass


@define_gd
class RotateAim(Rotate):
    dynamic: bool = False


@define_gd
class RotateAs(Rotate):
    dynamic: bool = False


@define_gd
class Text(GdObjectBase, SpecialId):
    text: str = 'a'
    kerning: int = 0


@define_gd
class ItemEdit(Trigger, SpecialId):
    """
    Points -> Item(-1)
    """
    a: Item | Timer = Item.Empty
    b: Item | Timer = Item.Empty
    mod: float = 1.
    result: Item | Timer = Item.Empty

    operator_a_b: ItemOperator = ItemOperator.Add  # Add, Sub, Mul, Div
    operator_ab_mod: ItemOperator = ItemOperator.Mul  # Mul, Div
    rounding_abm: RoundingFunc = RoundingFunc.No
    sign_abm: SignFunc = SignFunc.No
    operator_c_abm: ItemOperator = ItemOperator.Override  # all 5 operators
    rounding_cabm: RoundingFunc = RoundingFunc.No
    sign_cabm: SignFunc = SignFunc.No

    """
    def __pseudocode(self):
        has_a = ...
        has_b = ...
        if has_a and has_b:
            abm = '(a <op_a_b> b) <op_ab_mod> mod'
        elif has_a:
            abm = 'a <op_ab_mod> mod'
        elif has_b:
            abm = 'b <op_ab_mod> mod'
        else:
            abm = 'mod'
        abm = 'sign_abm(round_abm(abm))'
        cabm = 'c <op_c_abm> abm'
        result = 'sign_cabm(round_cabm(cabm))'
    """


@define_gd
class ItemCompare(TargetTrigger, SpecialId):
    target_false: Group = Group.Empty
    a: Item | Timer = Item.Empty
    b: Item | Timer = Item.Empty
    mod_a: float = 1.
    mod_b: float = 1.
    operator_a: ItemOperator = ItemOperator.Mul
    operator_b: ItemOperator = ItemOperator.Mul
    rounding_a: RoundingFunc = RoundingFunc.No
    rounding_b: RoundingFunc = RoundingFunc.No
    sign_a: SignFunc = SignFunc.No
    sign_b: SignFunc = SignFunc.No
    comparison: ItemComparison = ItemComparison.Equals
    tolerance: float = 0.


@define_gd
class ItemPersistent(Trigger, SpecialId):
    target: Item | Timer = Item.Empty
    persistent: bool = False
    target_all: bool = False
    reset: bool = False
