import classes
from classes.save import Save
from pathlib import Path
from python.pprint import pprint

save_path = Path.home() / r"AppData\Local\GeometryDash\CCLocalLevels.dat"

save = Save.LoadFromDAT(save_path.read_bytes())

with save.get('read').decompress('r') as level:
    for obj in level.module.objects:
        pprint(obj)

# pprint(save)
# if input('write?') == 'y':
#     save_path.write_bytes(save.SaveToDAT())
