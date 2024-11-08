import base64
import itertools

from serializing import *
from maker import Maker
from tools.funcs import pairs_to_dict, dict_to_pairs, Factory
import tools.decompressing
from classes.gd_module import GdModule
from classes.save import *

S = SerializingFamily.get('save')

key = Maker(WrapKeyInfo)
field = Maker(FieldInfo)

key.setup(optimize_key=None)
key(...).setup(serializer=DoNothing(), optimize_key=None)
key(str).setup(serializer=Func(str, str), default_data='')
key(int).setup(serializer=Func(int, str), default_data='0')
key(float).setup(serializer=Func(float, lambda x: f'{x:0.3f}'), default_data='0.')
key(bool).setup(serializer=Func(lambda s: s == '1', lambda x: '1' if x else '0'), default_data='0')
key('b64str').setup(serializer=Func(
    lambda val: base64.b64decode(val.encode('utf-8'), altchars=b'-_').decode('utf-8'),
    lambda val: base64.b64encode(val.encode('utf-8'), altchars=b'-_').decode('utf-8')
), default_data='')

field.setup(serializer=True)
field(...).setup()

gd_object_szr = SerializingFamily.get('gd_object')['GdObject']


class LevelSerializer(Base):
    def __init__(self, level_data_serializer: Base):
        self.level_data_serializer = level_data_serializer

    def analyze(self, info: LevelInfo):
        data = tools.decompressing.decompress(info.data.encode('utf-8')).decode('utf-8')
        settings, *objects, _ = data.split(';')
        module = GdModule()
        with module:
            level = self.level_data_serializer.analyze({
                'info': info,
                'settings': pairs_to_dict(settings.split(',')),
                'module': module,
            })
        with level:
            module.objects = [gd_object_szr.analyze(obj) for obj in objects]
        return level

    def compile(self, level, data=None):
        with level:
            objects = [gd_object_szr.compile(obj) for obj in level.module.objects]
            dct = self.level_data_serializer.compile(level)
            info, settings, _ = dct['info'], dct['settings'], dct['module']
            settings = ','.join(dict_to_pairs(settings))
        data = ';'.join(itertools.chain((settings,), objects, ('',)))
        data = tools.decompressing.compress(data.encode('utf-8')).decode('utf-8')
        return data


S[Level] = LevelSerializer(MultiField(
    field[...]('info'),
    field[...]('settings'),
    field[...]('module'),
) >> ToClass(Level))

S[LevelInfo] = WrapKeys(
    key[...]('k1', 'id'),
    key[...]('k2', 'name'),
    key['b64str']('k3', 'description'),
    key[...]('k4', 'data'),
    key[...]('k5', 'creator'),
    key[...]('k8', 'official_song'),
    key[...]('k11', 'downloads'),
    key[...]('k14', 'verified'),
    key[...]('k15', 'uploaded'),
    key[...]('k16', 'version'),
    key[...]('k18', 'attempts'),
    key[...]('k19', 'normal_mode_progress'),
    key[...]('k20', 'practive_mode_progress'),
    key[...]('k21', 'level_type'),
    key[...]('k22', 'likes'),
    key[...]('k23', 'length'),
    key[...]('k26', 'stars'),
    key[...]('k34', 'info'),
    key[...]('k36', 'jumps'),
    key[...]('k41', 'password'),
    key[...]('k42', 'original'),
    key[...]('k45', 'custom_song'),
    key[...]('k46', 'revision'),
    key[...]('k48', 'objects'),
    key[...]('k50', 'binary_version'),
    key[...]('k61', 'first_coin_acquired'),
    key[...]('k62', 'second_coin_acquired'),
    key[...]('k63', 'third_coin_acquired'),
    key[...]('k66', 'requested_stars'),
    key[...]('k67', 'extra'),
    key[...]('k74', 'timely_id'),
    key[...]('k79', 'unlisted'),
    key[...]('k80', 'senconds_spent_in_editor'),
    key[...]('k84', 'folder'),
    key[...]('kI1', 'editor_x'),
    key[...]('kI2', 'editor_y'),
    key[...]('kI3', 'editor_zoom'),
    key[...]('kI4', 'editor_tab_page'),
    key[...]('kI5', 'editor_tab'),
    key[...]('kI6', 'editor_tab_pages_dict'),
    key[...]('kI7', 'editor_layer'),
    key[...]('kCEK', 'kcek'),
    key[...](..., 'unused'),
) >> MultiField(
    field[...]('name'),
    field[...]('revision'),
    field[...]('data'),
    field[...]('description'),
    field[...]('unused', Key(...)),
) >> ToClass(LevelInfo)


def check_llm_03(data):
    """ just curious what it could be, alarm the unexpected value """
    match data:
        case []:
            pass
        case _:
            print(f'LocalLevelsSave.LLM_03 has a value: {data}')


S[Save] = WrapKeys(
    key[...]('LLM_01', 'levels', List(S[LevelInfo])),
    key[int]('LLM_02', 'version'),
    key[...]('LLM_03', None, Func(check_llm_03), default_data=Factory(list)),
) >> ToClass(Save)
