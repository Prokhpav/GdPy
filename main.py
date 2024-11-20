import classes
from classes.gd_id import Timer, Item
from classes.save import Save
from pathlib import Path
from python.pprint import pprint
from classes import gd_object as gd
from data.special_ids import special_ids

save_path = Path.home() / r"AppData\Local\GeometryDash\CCLocalLevels.dat"

save = Save.LoadFromDAT(save_path.read_bytes())

# object with id = 0 ???

with save.get('read').decompress('rw') as level:
    # level.module.objects.clear()
    for obj in level.module.objects:
        if isinstance(obj, gd.ItemEdit):
            obj.result = Timer.MainTime
        pprint(obj)
        # obj.id = 899
    level.module.objects.append(gd.GdObjectAnyId(1, x=15, y=75))

# pprint(save)
# if input('write? ') == 'y':
#     save_path.write_bytes(save.SaveToDAT())
#     print('saved')
