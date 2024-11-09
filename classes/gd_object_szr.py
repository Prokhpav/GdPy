import base64
from types import EllipsisType
from attrs import define
from bidict import bidict

from serializing import *
import recognizing as R
from maker import Maker
from tools.funcs import pairs_to_dict, dict_to_pairs
from . import gd_object as gd
from .enums import *
from .gd_id import *
from .gd_module import GdModule, GdIdRef

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
             bases: tuple[type[object]] | None = None
             ) -> Base:
        if bases is None:
            bases = klass.__mro__[:0:-1]
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
            value['1'] = value_id
        return ','.join(dict_to_pairs(value))


class SplitDict(Base):

    def __init__(self,
                 serializer: Base,
                 separator: str
                 ):
        self.serializer = serializer
        self.separator = separator

    def analyze(self, data: str):
        return pairs_to_dict(self.serializer.analyze(val) for val in data.split(self.separator))

    def compile(self, value, data=None):
        return self.separator.join(self.serializer.compile(val) for val in dict_to_pairs(value))


class GdIdSerializer(Base):
    def __init__(self, klass: type[GdIdRef]):
        self.klass = klass

    def analyze(self, data: str):
        return self.klass(int(data))

    def compile(self, value, data=None):
        return str(GdModule.C().ids[self.klass].get_value(value))


S['GdObject'] = gd_object_serializer = GdObjectSerialzier(R.Map(
    R.Key('1', int),
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
        )
    }
))

key = Maker(WrapKeyInfo)
field = Maker(FieldInfo)
inherit = InheritableFields(gd_object_serializer.serializers)

key.setup(optimize_key=True)
key(...).setup(serializer=DoNothing(), optimize_key=None)
key(str).setup(serializer=Func(str, str), default_data='')
key(int).setup(serializer=Func(int, str), default_data='0')
key(float).setup(serializer=Func(float, lambda x: f'{x:0.3f}'), default_data='0.')
key(bool).setup(serializer=Func(lambda s: s == '1', lambda x: '1' if x else '0'), default_data='0')
key('b64str').setup(serializer=Func(
    lambda val: base64.b64decode(val.encode('utf-8'), altchars=b'-_').decode('utf-8'),
    lambda val: base64.b64encode(val.encode('utf-8'), altchars=b'-_').decode('utf-8')
), default_data='')
key(Group).setup(serializer=GdIdSerializer(Group), default_data='0')
key(Item).setup(serializer=GdIdSerializer(Item), default_data='0')
key(Block).setup(serializer=GdIdSerializer(Block), default_data='0')

field(...).setup(serializer=True)

# debug
from data.property_ids import NAME_TO_ID

additional = [key[...](str(k), f'{k:>3}: {name}') for name, k in NAME_TO_ID.items() if k != 1]

inherit.make(
    gd.GdObjectBase,
    WrapKeys(*additional).combine(WrapKeys(
        key[...](..., 'unused'),
        key[float]('2', None, optimize_key=False),  # removed x for debug
        key[float]('3', None, optimize_key=False),  # removed y for debug

        key[int]('155', None)  # debug
    )),
    MultiField(
        field[...]('unused', Key(...), optimize_name=True),
        field[...]('x'),
        field[...]('y')
    )
)
# inherit.make(gd.AnyId)
inherit.make(
    gd.GdObjectAnyId,
    WrapKeys(
        key[int]('1', 'id'),
    ),
    MultiField(
        field[...]('id', optimize_name=False),
    )
)

inherit.make(
    gd.SpecialId,
    WrapKeys(
        key[int]('1', 'id')
    ),
    MultiField(
        field[...](None, Key('id'))
    )
)

inherit.make(
    gd.Trigger,
    WrapKeys(
        key[bool]('36', None, default_data='1', optimize_key=False),
        key[bool]('11', 'touch_triggered'),
        key[bool]('62', 'spawn_triggered'),
        key[bool]('87', 'multi_triggered')
    ),
    MultiField(
        field[...]('triggered', Tuple(
            Key('touch_triggered'),
            Key('spawn_triggered'),
            Key('multi_triggered')
        ) >> Mapping(
            ((True, True, False), Triggered.Coord),  # impossible state
            ((False, False, True), Triggered.Coord),  # impossible state
            ((True, True, True), Triggered.Coord),  # impossible state
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
    WrapKeys(
        key[Group]('51', 'target_group_id'),
    ),
    MultiField(
        field[...]('target', Key('target_group_id'))
    )
)

inherit.make(
    gd.Spawn,
    WrapKeys(
        key[bool]('63', 'delay'),
        key[bool]('556', 'delay_variation'),
        key[...]('442', 'remapping', serializer=SplitDict(Func(int, str), '.')),
        key[bool]('581', 'reset_remap'),
        key[bool]('441', 'spawn_ordered'),
        key[bool]('102', 'preview_disable'),
    ),
    MultiField(
        field[...]('delay'),
        field[...]('delay_variation'),
        field[...]('remapping'),
        field[...]('reset_remap'),
        field[...]('spawn_ordered'),
        field[...]('preview_disable'),
    )
)

inherit.make(
    gd.Toggle,
    WrapKeys(
        key[bool]('56', 'activate_group')
    ),
    MultiField(
        field[...]('activate', Key('activate_group'))
    )
)

inherit.make(
    gd.Stop,
    WrapKeys(
        key[int]('580', 'stop_mode'),
        key[bool]('535', 'use_control_id'),
    ),
    MultiField(
        field[...]('stop', Key('stop_mode') >> ToEnum(StopMode)),
        field[...]('use_control_id'),
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
    WrapKeys(
        key[Item]('80', 'item'),
        key[int]('77', 'count'),
        key[float]('449', 'modifier'),
        key[int]('88', 'mode'),
        key[bool]('139', 'override')
    ),
    MultiField(
        field[...]('item'),
        field[...]('count'),
        field[...]('modifier'),
        field[...]('mode', Tuple(Key('mode'), Key('override')) >> PickupOverrideSerializer()),
    )
)

inherit.make(
    gd.Count,
    WrapKeys(
        key[Item]('80', 'item'),
        key[int]('77', 'count'),
        key[float]('56', 'activate_group'),
        key[bool]('104', 'multi_activate'),
    ),
    MultiField(
        field[...]('item'),
        field[...]('count'),
        field[...]('activate', Key('activate_group')),
        field[...]('multi_activate'),
    )
)

inherit.make(
    gd.InstantCount,
    WrapKeys(
        key[Item]('80', 'item'),
        key[int]('77', 'count'),
        key[float]('56', 'activate_group'),
        key[int]('88', 'comparison'),
    ),
    MultiField(
        field[...]('item'),
        field[...]('count'),
        field[...]('activate', Key('activate_group')),
        field[...]('comparison', Key('comparison') >> ToEnum(Comparison)),
    )
)

inherit.make(
    gd.CounterLabel,
    WrapKeys(
        key[Item]('80', 'item'),
        key[int]('391', 'text_align'),
        key[bool]('389', 'seconds_only'),
        key[bool]('466', 'as_timer'),
        key[int]('390', 'special_mode')
    ),
    MultiField(
        field[...]('item'),
        field[...]('text_align'),
        field[...]('seconds_only'),
        field[...]('as_timer'),
        field[...]('special_mode', Key('special_mode') >> ToEnum(CounterMode))
    )
)

inherit.make(
    gd.Touch,
    WrapKeys(
        key[bool]('81', 'hold_mode'),
        key[int]('82', 'toggle_mode'),
        key[int]('198', 'player_only'),
        key[bool]('89', 'dual_mode'),
    ),
    MultiField(
        field[...]('hold_mode'),  # if True, does the opposite of toggle_mode when touch ends
        field[...]('toggle_mode', Key('toggle_mode') >> ToEnum(ToggleMode)),
        field[...]('player_only', Key('player_only') >> ToEnum(PlayerOnly)),
        field[...]('dual_mode'),  # legacy, use player_only.P1 instead
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
    WrapKeys(
        key[Block]('80', 'block_a'),
        key[Block]('95', 'block_b'),
        key[bool]('138', 'player_1'),
        key[bool]('200', 'player_2'),
        key[bool]('201', 'player_player'),
    ),
    MultiField(
        field[...]('block_a'),
        field[...]('block_b'),
        field[...]('player_collision', Tuple(Key('player_1'), Key('player_2'), Key('player_player')) >> CollisionPlayerSerializer()),
    )
)

inherit.make(
    gd.Collision,
    WrapKeys(
        key[float]('10', None),  # duration=0.5, accidentally RobTob leaves it
        key[bool]('56', 'activate_group'),
        key[bool]('93', 'on_exit')
    ),
    MultiField(
        field[...]('activate', Key('activate_group')),
        field[...]('on_exit'),
    )
)

inherit.make(
    gd.InstantCollision,
    WrapKeys(
        key[Group]('71', 'target_false'),
    ),
    MultiField(
        field[...]('target_false'),
    )
)

inherit.make(
    gd.CollisionState,
    WrapKeys(
        key[Group]('71', 'target_exit'),
    ),
    MultiField(
        field[...]('target_exit'),
    )
)

inherit.make(
    gd.CollisionBlock,
    WrapKeys(
        key[bool]('36', None, default_data='1', optimize_key=False),
        key[Block]('80', 'block'),
        key[bool]('94', 'dynamic')
    ),
    MultiField(
        field[...]('block'),
        field[...]('dynamic'),
    )
)

inherit.make(
    gd.ToggleBlock,
    WrapKeys(
        key[bool]('56', 'activate_group'),
        key[bool]('444', 'no_multi_activate'),
        key[bool]('445', 'claim_touch'),
        key[bool]('504', 'spawn_only'),
    ),
    MultiField(
        field[...]('activate', Key('activate_group')),
        field[...]('no_multi_activate'),
        field[...]('claim_touch'),
        field[...]('spawn_only'),
    )
)

inherit.make(
    gd.Reset,
)

inherit.make(
    gd.EasingTrigger,
    WrapKeys(
        key[float]('10', 'duration'),
        key[int]('30', 'easing'),
        key[float]('85', 'easing_rate', default_value=2.),
    ),
    MultiField(
        field[...]('duration'),
        field[...]('easing', Key('easing') >> ToEnum(Easing)),
        field[...]('easing_rate'),
    )
)

inherit.make(
    gd.Move,
    WrapKeys(
        key[bool]('397', 'dynamic_mode'),
        key[bool]('544', 'silent'),
        key[int]('28', None),
        key[int]('29', None),
        key[bool]('58', None),
        key[bool]('59', None),
        key[bool]('100', None),  # target_mode
        key[bool]('394', None),  # direction_mode
    ),
    MultiField(
        field[...]('silent'),
    )
)

inherit.make(
    gd.MoveBy,
    WrapKeys(
        key[int]('28', 'move_x'),
        key[int]('29', 'move_y'),
        key[bool]('58', 'lock_to_player_x'),
        key[bool]('59', 'lock_to_player_y'),
        key[bool]('141', 'lock_to_camera_x'),
        key[bool]('142', 'lock_to_camera_y'),
        key[float]('143', 'mod_x'),
        key[float]('144', 'mod_y'),
        key[bool]('393', 'small_steps'),
    ),
    MultiField(
        field[...]('move_x'),
        field[...]('move_y'),
        field[...]('lock_x', Key('lock_to_player_x')),
        field[...]('lock_y', Key('lock_to_player_y')),
        field[...]('mod_x'),
        field[...]('mod_y'),
        field[...]('small_steps'),
    )
)

inherit.make(
    gd.MoveTo,
    WrapKeys(
        key[Group]('395', 'center_group_id'),
        key[Group]('71', 'target_pos_group_id'),
        key[int]('101', 'target_pos_move_mode', ),
        key[bool]('138', 'target_pos_p1'),
        key[bool]('200', 'target_pos_p2'),
    ),
    MultiField(
        field[...]('center', Key('center_group_id')),
        field[...]('target_pos', Key('target_pos_group_id')),
    )
)

inherit.make(
    gd.MoveAt,
    WrapKeys(
        key[Group]('395', 'center_group_id'),
        key[Group]('71', 'target_pos_group_id'),
        key[int]('396', 'distance', ),
        key[bool]('138', 'target_pos_p1'),
        key[bool]('200', 'target_pos_p2'),
    ),
    MultiField(
        field[...]('center', Key('center_group_id')),
        field[...]('target_pos', Key('target_pos_group_id')),
        field[...]('distance'),
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
    WrapKeys(
        key[Group]('71', 'center'),
        key[float]('68', 'rotate_degrees'),
        key[int]('69', 'times_360'),
        key[bool]('70', 'lock_object_rotation'),
        key[bool]('397', 'dynamic_rotation'),
    ),
    MultiField(
        field[...]('center'),
        field[...]('degrees', Tuple(Key('rotate_degrees'), Key('times_360')) >> RotateDegreesSerializer()),
        field[...]('lock_object_rotation'),
        field[...]('dynamic_rotation'),
    )
)
