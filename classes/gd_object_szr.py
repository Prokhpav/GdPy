import base64
from types import EllipsisType
from attrs import define

from serializing import *
import recognizing as R
from maker import Maker
from tools.funcs import pairs_to_dict, dict_to_pairs
import classes.gd_object as gd

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
        return self.serializers[klass].analyze(data)

    def compile(self, value, data=None):
        value = self.serializers[type(value)].compile(value)
        return ','.join(dict_to_pairs(value))


S['GdObject'] = gd_object_serializer = GdObjectSerialzier(R.Map(
    R.Key('1', int), {
        ...: gd.GdObjectAnyId
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

field(...).setup(serializer=True)

inherit.make(
    gd.AnyId,
    WrapKeys(
        key[int]('1', 'id'),
        key[...](..., 'unused')
    ),
    MultiField(
        field[...]('id'),
        field[...]('unused', Key(...)),
    )
)
inherit.make(gd.GdObjectAnyId)
