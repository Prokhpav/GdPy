import base64
from types import EllipsisType

from bidict import bidict

from serializing import *
import recognizing as R
from maker import Maker
from serializing import SplitDict, MultiKey
from tools.funcs import pairs_to_dict, dict_to_pairs
from . import gd_object as gd
from .enums import *
from .gd_id import *
from .gd_id import Timer
from .gd_module import GdIdRef
from .gd_object import Move, ItemEdit
from attrs import define

S = SerializingFamily.get('gd_object')


@define
class InheritableInfo:
    klass: type[object]
    keys: WrapKeys
    fields: MultiField
    serialzier: Base


class InheritableFields:
    infos: dict[type[object], InheritableInfo]
    S: dict[type[object], Base]

    def __init__(self, serializers: dict[type[object], Base] | None = None):
        self.infos = {}
        self.serializers = {} if serializers is None else serializers

    def make(self,
             klass: type[object],
             keys: WrapKeys = None,
             fields: MultiField = None,
             *,
             to_klass: bool = True,
             bases: tuple[type[object] | EllipsisType, ...] | None = None
             ) -> Base:
        if bases is None:
            bases = klass.__mro__[:0:-1]
        elif Ellipsis in bases:
            bases = klass.__mro__[:0:-1] + tuple(base for base in bases if base is not Ellipsis)
        new_keys = WrapKeys()
        new_fields = MultiField()
        for base in bases:
            if base not in self.infos:
                continue
            info = self.infos[base]
            new_keys = new_keys.combine(info.keys)
            new_fields = new_fields.combine(info.fields)
        if keys is not None:
            new_keys = new_keys.combine(keys)
        if fields is not None:
            new_fields = new_fields.combine(fields)

        serializer = new_keys >> new_fields
        if to_klass:
            serializer = serializer >> ToClass(klass)

        if klass in self.infos:
            raise KeyError(f'Overriding {klass}')
        self.infos[klass] = InheritableInfo(klass, new_keys, new_fields, serializer)
        self.serializers[klass] = serializer
        return serializer


class GdObjectSerialzier(Base):
    recognizer: R.Base
    S: dict[type | EllipsisType, Base]

    def __init__(self, recognizer: R.Base):
        self.recognizer = recognizer
        self.serializers = {}

    def analyze(self, data: str):
        data = pairs_to_dict(data.split(','))
        klass = self.recognizer(data)
        if klass not in self.serializers:
            print(f'WARN: recognized class withous serializer: {klass}')
            klass = gd.GdObjectAnyId
        return self.serializers[klass].analyze(data)

    def compile(self, value, data=None):
        value_id = value.__id__ if isinstance(value, gd.SpecialId) else None
        value = self.serializers[type(value)].compile(value)
        if value_id is not None:
            value['1'] = str(value_id)
        return ','.join(dict_to_pairs(value))


class GdIdSerializer(Base):
    def __init__(self, klass: type[GdIdRef]):
        self.klass = klass

    def analyze(self, data: str):
        return self.klass(int(data))

    def compile(self, value: GdIdRef, data=None):
        return str(value.get_value())


def make_keys(*keys: WrapKeyInfo | str | tuple) -> WrapKeys:
    processed = []
    for wrap_key in keys:
        match wrap_key:
            case WrapKeyInfo():
                pass
            case (str(key_), name):
                wrap_key = key[...](key_, name)
            case (str(key_), name, Base(szr)):
                wrap_key = key[...](key_, name, szr)
            case (str(key_), name, type_):
                wrap_key = key[type_](key_, name)
            case (str(key_), name, type_, Base()):
                wrap_key = key[type_](key_, name, szrs[type_] >> wrap_key[3])
            case _:
                raise TypeError()
        processed.append(wrap_key)
    return WrapKeys(*processed)


def make_fields(*fields: FieldInfo | str | tuple) -> MultiField:
    """
    name
    (name,)
    (name, key_szr)  # key_szr: str | Base | ...
    (name, key_szr, szr2)
    (name, key_szr, type_)
    (name, key_szr, type_, szr2)
    """
    processed = []
    for fld in fields:
        match fld:
            case FieldInfo():
                pass
            case (name, ) | name if name is None or name is Ellipsis or isinstance(name, str):
                fld = field[...](name, Key(name))
            case (name, key_szr, *rest) if name is None or name is Ellipsis or isinstance(name, str):
                match key_szr:
                    case str():
                        key_szr = Key(key_szr)
                    case EllipsisType():
                        key_szr = Key(name)
                    case Base():
                        pass
                    case _:
                        raise TypeError()
                type_ = ...
                match rest:
                    case ():
                        pass
                    case (Base(), ):
                        key_szr = key_szr >> rest[0]
                    case (type_, ):
                        pass
                    case (type_, Base()):
                        key_szr = key_szr >> rest[1]
                    case _:
                        raise TypeError()
                fld = field[type_](name, key_szr)
            case _:
                raise TypeError()
        processed.append(fld)
    return MultiField(*processed)


S['GdObject'] = gd_object_serializer = GdObjectSerialzier(R.Map(
    R.Key('1', int, default=0),
    gd.SpecialId.__all_classes__ | {
        ...: gd.GdObjectAnyId,
        gd.Move.__id__: R.Map(
            R.Tuple(
                R.Key('100', bool, False),  # target_mode
                R.Key('394', bool, False)  # direction_mode
            ), {
                (False, False): gd.MoveBy,
                (True, False): gd.MoveTo,
                (False, True): gd.MoveAt,
            }
        ),
        gd.Rotate.__id__: R.Map(
            R.Tuple(
                R.Key('100', bool, False),  # aim_mode
                R.Key('394', bool, False),  # follow_mode
            ), {
                (False, False): gd.RotateBy,
                (True, False): gd.RotateAim,
                (False, True): gd.RotateAs,
            }
        )
    }
))

key = Maker(WrapKeyInfo)
field = Maker(FieldInfo)
inherit = InheritableFields(gd_object_serializer.serializers)

szrs = {}
szrs[...] = DoNothing()
szrs[str] = Func(str, str)
szrs[int] = Func(int, str)
szrs[float] = Func(float, lambda x: f'{x:0.3f}')
szrs[bool] = Func(lambda s: s == '1', lambda x: '1' if x else '0')
szrs['b64str'] = Func(
    lambda val: base64.b64decode(val.encode('utf-8'), altchars=b'-_').decode('utf-8'),
    lambda val: base64.b64encode(val.encode('utf-8'), altchars=b'-_').decode('utf-8')
)
szrs['List[Group]'] = StrSplit('.') >> List(GdIdSerializer(Group))
szrs['HSV'] = StrSplit('a') >> Tuple(
    szrs[int], szrs[float], szrs[float], szrs[bool], szrs[bool], iterate=True
) >> ToAttrs(HSV)

key.setup(optimize_key=True)
key(...).setup(serializer=DoNothing(), optimize_key=None)
key(str).setup(serializer=szrs[str], default_data='')
key(int).setup(serializer=szrs[int], default_data='0')
key(float).setup(serializer=szrs[float], default_data='0.')
key(bool).setup(serializer=szrs[bool], default_data='0')
key('b64str').setup(serializer=szrs['b64str'], default_data='')
key('List[Group]').setup(serializer=szrs['List[Group]'], default_data='')
key('HSV').setup(serializer=szrs['HSV'], default_data='0a0a0a0a0')
key(Group).setup(serializer=GdIdSerializer(Group), default_data='0')

field(...).setup(serializer=True)
field(Group).setup(additional_serializer=GdIdSerializer(Group))
field(Item).setup(additional_serializer=GdIdSerializer(Item))
field(Block).setup(additional_serializer=GdIdSerializer(Block))

# debug
from data.property_ids import NAME_TO_ID

additional = [key[...](str(k), f'{k:>3}: {name}') for name, k in NAME_TO_ID.items() if k != 1]

inherit.make(
    gd.GdObjectBase,
    WrapKeys(*additional) | make_keys(
        key[...](..., 'unused'),
        key[int]('1', 'id', default_value=0),
        ('57', 'groups', 'List[Group]'),
        ('274', 'parent_groups', 'List[Group]'),
        # arrangement
        ('2', 'x', float),
        ('3', 'y', float),
        ('4', 'flip_h', float),
        ('5', 'flip_v', float),
        ('6', 'rotation', float),
        # appearance
        ('21', 'color', int),  # todo: GdID ColorId
        ('22', 'color_detail', int),
        ('497', 'color_treatment', int),  # 0 - default, 1 - base, 2 - detail
        ('41', 'hsv_enabled', bool),
        ('42', 'hsv_detail_enabled', bool),
        ('43', 'hsv', 'HSV'),
        ('44', 'hsv_detail', 'HSV'),
        ('155', 'hsv_index', int),
        ('156', 'hsv_detail_index', int),
        # edit group
        ('20', 'editor_layer_1', int),
        ('61', 'editor_layer_2', int),
        ('25', 'z_order', bool),
        ('24', 'z_layer', bool),
        # extra
        ('64', 'dont_fade', bool),
        ('67', 'dont_enter', bool),
        ('116', 'no_effects', bool),
        ('34', 'group_parent', bool),
        ('279', 'area_parent', bool),
        ('496', 'dont_boost_y', bool),
        ('509', 'dont_boost_x', bool),
        ('103', 'high_detail', bool),
        ('121', 'no_touch', bool),
        ('134', 'passable', bool),
        ('135', 'hide', bool),
        ('136', 'non_stick_x', bool),
        ('495', 'extra_sticky', bool),
        ('511', 'extended_collision', bool),
        ('137', 'ice_block', bool),
        ('193', 'grip_slope', bool),
        ('96', 'no_glow', bool),
        ('507', 'no_particle', bool),
        ('289', 'non_stick_y', bool),
        ('356', 'scale_stick', bool),
        ('372', 'no_audio_scale', bool),
        # extra 2
        ('343', 'enter_channel', int),  # todo: GdId EnterChannel
        ('446', 'material', int),
        # common in triggers
        ('11', 'touch_triggered', bool),
        ('62', 'spawn_triggered', bool),
        ('87', 'multi_triggered', bool),
        ('51', 'target_group', int),
        ('71', 'target_group_2', int),
        ('80', 'target_id', int),
        ('95', 'target_id_2', int),
        ('56', 'activate_group', bool),
        ('77', 'count', int),
        ('138', 'player_1', bool),
        ('200', 'player_2', bool),
        ('397', 'dynamic_mode', bool),
    ) | make_keys(
        key[float]('2', 'x', optimize_key=False),
        key[float]('3', 'y', optimize_key=False),
    ),
    make_fields(
        field[...]('unused', Key(...), optimize_name=True),
        'x',
        'y',
        'rotation',
    )
)
# inherit.make(gd.AnyId)
inherit.make(
    gd.GdObjectAnyId,
    make_keys(),
    make_fields(
        field[...]('id', optimize_name=False),
    )
)

inherit.make(
    gd.SpecialId,
    make_keys(),
    make_fields(field[...](None, Key('id')))
)

inherit.make(
    gd.Trigger,
    make_keys(
        key[bool]('36', None, default_data='1', optimize_key=False),
    ),
    make_fields(
        field[...]('triggered', MultiKey(
            'touch_triggered', 'spawn_triggered', 'multi_triggered'
        ) >> Mapping(
            # ((True, True, False), Triggered.Coord),  # impossible state
            # ((False, False, True), Triggered.Coord),  # impossible state
            # ((True, True, True), Triggered.Coord),  # impossible state
            ((False, False, False), Triggered.Coord),
            ((True, False, False), Triggered.Touch),
            ((False, True, False), Triggered.Spawn),
            ((True, False, True), Triggered.TouchMulti),
            ((False, True, True), Triggered.SpawnMulti),
        ))
    )
)

inherit.make(
    gd.TargetTrigger,
    make_keys(),
    make_fields(
        ('target', 'target_group', Group)
    )
)

inherit.make(
    gd.Spawn,
    make_keys(
        ('63', 'delay', bool),
        ('556', 'delay_variation', bool),
        key[...]('442', 'remapping', serializer=SplitDict(Func(int, str), '.')),
        ('581', 'reset_remap', bool),
        ('441', 'spawn_ordered', bool),
        ('102', 'preview_disable', bool),
    ),
    make_fields(
        'delay',
        'delay_variation',
        'remapping',
        'reset_remap',
        'spawn_ordered',
        'preview_disable',
    )
)

inherit.make(
    gd.Toggle,
    make_keys(),
    make_fields(
        field[...]('activate', 'activate_group')
    )
)

inherit.make(
    gd.Stop,
    make_keys(
        ('580', 'stop_mode', int),
        ('535', 'use_control_id', bool),
    ),
    make_fields(
        ('mode', 'stop_mode', ToEnum(StopMode)),
        'use_control_id',
    )
)


class PickupOverrideSerializer(Base):
    def analyze(self, data):
        mode, override = data
        if mode == 0 and override:
            return PickupMode.Override
        return PickupMode(mode)

    def compile(self, value, data=None):
        if value is PickupMode.Override:
            return 0, True
        return value.value, False


inherit.make(
    gd.Pickup,
    make_keys(
        ('449', 'modifier', float),
        ('88', 'mode', int),
        ('139', 'override', bool)
    ),
    make_fields(
        ('item', 'target_id', Item),
        'count',
        'modifier',
        ('mode', MultiKey('mode', 'override') >> PickupOverrideSerializer()),
    )
)

inherit.make(
    gd.Count,
    make_keys(
        ('104', 'multi_activate', bool),
    ),
    make_fields(
        ('item', 'target_id', Item),
        'count',
        ('activate', 'activate_group'),
        'multi_activate',
    )
)

inherit.make(
    gd.InstantCount,
    make_keys(
        ('88', 'comparison', int),
    ),
    make_fields(
        ('item', 'target_id', Item),
        'count',
        ('activate', 'activate_group'),
        ('comparison', ToEnum(Comparison)),
    )
)

inherit.make(
    gd.CounterLabel,
    make_keys(
        ('391', 'text_align', int),
        ('389', 'seconds_only', bool),
        ('466', 'as_timer', bool),
        ('390', 'special_mode', int)
    ),
    make_fields(
        ('item', 'target_id', Item),
        'text_align',
        'seconds_only',
        'as_timer',
        ('special_mode', ToEnum(CounterMode))
    )
)

inherit.make(
    gd.Touch,
    make_keys(
        ('f', 'hold_mode', bool),
        ('82', 'toggle_mode', int),
        ('198', 'player_only', int),
        ('89', 'dual_mode', bool),
    ),
    make_fields(
        'hold_mode',  # if True, does the opposite of toggle_mode when touch ends
        ('toggle_mode', ToEnum(ToggleMode)),
        ('player_only', ToEnum(PlayerOnly)),
        'dual_mode',  # legacy, use player_only.P1 instead
    )
)


class CollisionPlayerSerializer(Base):
    dct = bidict({
        CollisionPlayer.No: (False, False, False),
        CollisionPlayer.P1: (True, False, False),
        CollisionPlayer.P2: (False, True, False),
        CollisionPlayer.P: (True, True, False),
        CollisionPlayer.PP: (False, False, True),
    })

    def analyze(self, data):
        p1, p2, pp = data
        if pp:
            return CollisionPlayer.PP
        return self.dct.inv[(p1, p2, False)]

    def compile(self, value, data=None):
        return self.dct[value]


inherit.make(
    gd.CollisionBase,
    make_keys(
        ('201', 'player_player', bool),
    ),
    make_fields(
        ('block_a', 'target_id', Block),
        ('block_b', 'target_id_2', Block),
        ('player_collision', MultiKey('player_1', 'player_2', 'player_player') >> CollisionPlayerSerializer()),
    )
)

inherit.make(
    gd.Collision,
    make_keys(
        ('10', None, float),  # duration=0.5, accidentally RobTob leaves it
        ('93', 'on_exit', bool)
    ),
    make_fields(
        ('activate', 'activate_group'),
        'on_exit',
    )
)

inherit.make(
    gd.InstantCollision,
    make_keys(),
    make_fields(
        ('target_false', 'target_group_2', Group),
    )
)

inherit.make(
    gd.CollisionState,
    make_keys(),
    make_fields(
        ('target_exit', 'target_group_2', Group),
    )
)

inherit.make(
    gd.CollisionBlock,
    make_keys(
        key[bool]('36', None, default_data='1', optimize_key=False),
        ('94', 'dynamic', bool)
    ),
    make_fields(
        ('block', 'target_id', Block),
        'dynamic',
    )
)

inherit.make(
    gd.ToggleBlock,
    make_keys(
        ('444', 'no_multi_activate', bool),
        ('445', 'claim_touch', bool),
        ('504', 'spawn_only', bool),
    ),
    make_fields(
        ('activate', 'activate_group'),
        'no_multi_activate',
        'claim_touch',
        'spawn_only',
    )
)

inherit.make(
    gd.Reset,
)

inherit.make(
    gd.EasingTrigger,
    make_keys(
        ('10', 'duration', float),
        ('30', 'easing', int),
        ('85', 'easing_rate', float),
    ),
    make_fields(
        'duration',
        ('easing', ToEnum(Easing)),
        'easing_rate',
    )
)

inherit.make(
    gd.Move,
    make_keys(
        ('100', None, bool),  # target_mode
        ('394', None, bool),  # direction_mode
        ('544', 'silent', bool),
        ('28', 'move_x', int),
        ('29', 'move_y', int),
        ('58', 'lock_to_player_x', bool),
        ('59', 'lock_to_player_y', bool),
        ('141', 'lock_to_camera_x', bool),
        ('142', 'lock_to_camera_y', bool),
        ('143', 'mod_x', float),
        ('144', 'mod_y', float),
        ('393', 'small_steps', bool),
        ('395', 'center_group', Group),
        ('101', 'target_pos_move_mode', int),
        ('396', 'distance', int),
    ),
    make_fields(
        field[...]('silent'),
    )
)


class LockSerializer(Base):
    def __init__(self, lock_name, mod_name):
        self.lock_name = lock_name
        self.mod_name = mod_name

    def analyze(self, data):
        player, camera, mod = data
        match (player, camera, mod):
            case (False, False, _) | (_, _, 0.):
                return Lock.No
            case (True, False, _):
                return Lock.Player
            case (False, True, _):
                return Lock.Camera
            case _:
                return Lock.No

    def compile(self, value, data=None):
        lock, mod = value.get(self.lock_name, Lock.No), value.get(self.mod_name, 1.)
        match (lock, mod):
            case (Lock.No, _) | (_, 0.):
                return False, False, 1.
            case (Lock.Player, _):
                return True, False, mod
            case (Lock.Camera, _):
                return False, True, mod
            case _:
                raise TypeError(lock, mod)


inherit.make(
    gd.MoveBy,
    make_keys(),
    make_fields(
        'move_x',
        'move_y',
        field[...]('lock_x', MultiKey('lock_to_player_x', 'lock_to_camera_x', 'mod_x') >> LockSerializer('lock_x', 'mod_x'), compile_takes_value=True),
        field[...]('lock_y', MultiKey('lock_to_player_y', 'lock_to_camera_y', 'mod_y') >> LockSerializer('lock_y', 'mod_y'), compile_takes_value=True),
        'mod_x',  # todo: if lock!=No and mod == 0 change to lock=No and move=0
        'mod_y',  # the game doesn't save mod=0 and sets to default mod=1, can cause bugs
        'small_steps',
    )
)

target_player_szr = MultiKey('player_1', 'player_2') >> Mapping(
    # ((True, True), TargetPlayer.P1),  # impossible state
    ((False, False), TargetPlayer.No),
    ((True, False), TargetPlayer.P1),
    ((False, True), TargetPlayer.P2),
)

inherit.make(
    gd.MoveTo,
    make_keys(
    ),
    make_fields(
        ('center', 'center_group'),
        ('target_pos', 'target_group_2', Group),
        ('target_player', target_player_szr),
        ('mode', 'target_pos_move_mode', ToEnum(XYOnly)),
        ('dynamic', 'dynamic_mode'),
    )
)

inherit.make(
    gd.MoveAt,
    make_keys(
    ),
    make_fields(
        ('center', 'center_group'),
        ('target_pos', 'target_group_2', Group),
        ('target_player', target_player_szr),
        ('mode', 'target_pos_move_mode', ToEnum(XYOnly)),
        'distance',
        ('dynamic', 'dynamic_mode'),
    )
)


class RotateDegreesSerializer(Base):
    def analyze(self, data):
        degrees, times_360 = data
        return degrees + 360 * times_360

    def compile(self, value, data=None):
        return value % 360, value // 360


inherit.make(
    gd.Rotate,
    make_keys(
        ('100', None, bool),  # aim_mode
        ('394', None, bool),  # follow_mode
        ('68', 'degrees', float),
        ('69', 'times_360', int),
        ('70', 'lock_object_rotation', bool),
        ('403', 'dynamic_easing', int),
        ('401', 'rotation_target', Group),
        ('402', 'rotation_offset', float),
        ('516', 'target_clamp_min_x', Group),
        ('517', 'target_clamp_max_x', Group),
        ('518', 'target_clamp_min_y', Group),
        ('519', 'target_clamp_max_y', Group),
    ),
    make_fields(
        ('degrees', MultiKey('degrees', 'times_360') >> RotateDegreesSerializer()),
        ('center', 'target_group_2', Group),
        'lock_object_rotation',
    )
)

inherit.make(
    gd.RotateBy,
    make_keys(),
    make_fields()
)

inherit.make(
    gd.RotateAim,
    make_keys(),
    make_fields(
        'dynamic_mode',
        'dynamic_easing',
        'rotation_target',
        'rotation_offset',
        ('rotation_target_player', target_player_szr),
        ('target_clamp', MultiKey(
            'target_clamp_min_x',
            'target_clamp_min_y',
            'target_clamp_max_x',
            'target_clamp_max_y'
        ) >> ToAttrs(ClampRect)),
    ),
)

inherit.make(
    gd.RotateAs,
    make_keys(),
    make_fields(
        'dynamic_mode',
        'dynamic_easing',
        'rotation_target',
        'rotation_offset',
        ('rotation_target_player', target_player_szr),
    )
)

inherit.make(
    gd.Text,
    make_keys(
        key['b64str']('31', 'text', default_value='a'),
        ('488', 'kerning', int)
    ),
    make_fields(
        'text',
        'kerning',
    )
)


class ItemTypeSerializer(Base):
    def analyze(self, data):
        gd_id, type_ = data
        match type_:
            case ItemType.No:
                return Item.Empty
            case ItemType.Item:
                return Item(gd_id)
            case ItemType.Timer:
                return Timer(gd_id)
            case ItemType.Points:
                return Item.Points
            case ItemType.MainTime:
                return Timer.MainTime
            case ItemType.Attempts:
                return Item.Attempts
            case _:
                raise TypeError(data)

    def compile(self, value: Item | Timer, data=None):
        match value:
            case Item.Empty:
                return 0, ItemType.No
            case Item.Points:
                return 0, ItemType.Points
            case Item.Attempts:
                return 0, ItemType.Attempts
            case Item():
                return value.get_value(), ItemType.Item
            case Timer.Empty:
                return 0, ItemType.No
            case Timer.MainTime:
                return 0, ItemType.MainTime
            case Timer():
                return value.get_value(), ItemType.Timer
            case _:
                raise TypeError(value)


inherit.make(
    gd.ItemEdit,
    make_keys(
        ('476', 'item_type_1', int, ToEnum(ItemType)),  # 0 1 2 3 4 5
        ('477', 'item_type_2', int, ToEnum(ItemType)),  # .     0 1 2 3 4 5
        ('478', 'item_type_3', int, ToEnum(ItemType)),  # .       1 2 3
        ('479', 'mod', float),
        ('480', 'operator_1', int, ToEnum(ItemOperator)),  # 0 1 2 3 4  = + - * /
        ('481', 'operator_2', int, ToEnum(ItemOperator)),  # . 1 2 3 4
        ('482', 'operator_3', int, ToEnum(ItemOperator)),  # .     3 4
        ('578', 'sign_func_1', int, ToEnum(SignFunc)),  # 0 1 2   no, abs, neg
        ('579', 'sign_func_2', int, ToEnum(SignFunc)),  # 0 1 2
        ('485', 'rounding_func_1', int, ToEnum(RoundingFunc)),  # 0 1 2 3
        ('486', 'rounding_func_2', int, ToEnum(RoundingFunc)),  # 0 1 2 3  no, round, floor, ceil
    ),
    make_fields(
        ('a', MultiKey('target_id', 'item_type_1') >> ItemTypeSerializer()),
        ('b', MultiKey('target_id_2', 'item_type_2') >> ItemTypeSerializer()),
        ('mod',),
        ('result', MultiKey('target_group', 'item_type_3') >> ItemTypeSerializer()),
        ('operator_a_b', 'operator_2'),
        ('operator_ab_mod', 'operator_3'),
        ('rounding_abm', 'rounding_func_1'),
        ('sign_abm', 'sign_func_1'),
        ('operator_c_abm', 'operator_1'),
        ('rounding_cabm', 'rounding_func_2'),
        ('sign_cabm', 'sign_func_2'),
    )
)

inherit.make(
    gd.ItemCompare,
    make_keys(
        ('476', 'item_type_1', int, ToEnum(ItemType)),  # 0 1 2 3 4 5
        ('477', 'item_type_2', int, ToEnum(ItemType)),  # .     0 1 2 3 4 5
        ('479', 'mod', float),
        ('480', 'operator_1', int, ToEnum(ItemOperator)),  # 0 1 2 3 4  = + - * /
        ('481', 'operator_2', int, ToEnum(ItemOperator)),  # . 1 2 3 4
        ('482', 'operator_3', int, ToEnum(ItemComparison)),  # ==, >, >=, <, <=, !=
        ('483', 'mod_2', float),
        ('484', 'tolerance', float),
        ('578', 'sign_func_1', int, ToEnum(SignFunc)),  # 0 1 2   no, abs, neg
        ('579', 'sign_func_2', int, ToEnum(SignFunc)),  # 0 1 2
        ('485', 'rounding_func_1', int, ToEnum(RoundingFunc)),  # 0 1 2 3
        ('486', 'rounding_func_2', int, ToEnum(RoundingFunc)),  # 0 1 2 3  no, round, floor, ceil

    ),
    make_fields(
        ('a', MultiKey('target_id', 'item_type_1') >> ItemTypeSerializer()),
        ('b', MultiKey('target_id_2', 'item_type_2') >> ItemTypeSerializer()),
        ('mod_a', 'mod'),
        ('mod_b', 'mod_2'),
        ('operator_a', 'operator_1'),
        ('operator_b', 'operator_2'),
        ('rounding_a', 'rounding_func_1'),
        ('rounding_b', 'rounding_func_2'),
        ('sign_a', 'sign_func_1'),
        ('sign_b', 'sign_func_2'),
        ('comparison', 'operator_3'),
        ('tolerance',),
        ('target_true', 'target_group', Group),
        ('target_false', 'target_group_2', Group),
    )
)

class DecideItemTimer(Base):
    def analyze(self, data):
        target_id, is_timer = data
        if is_timer:
            return Timer(target_id)
        return Item(target_id)

    def compile(self, value: GdIdRef, data=None):
        return value.get_value(), isinstance(value, Timer)

inherit.make(
    gd.ItemPersistent,
    make_keys(
        ('491', 'persistent', bool),
        ('492', 'target_all', bool),
        ('493', 'reset', bool),
        ('494', 'is_timer', bool),
    ),
    make_fields(
        ('target', MultiKey('target_id', 'is_timer') >> DecideItemTimer()),
        'persistent',
        'target_all',
        'reset',
    )
)
