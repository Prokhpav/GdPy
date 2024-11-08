from serializing import SerializingFamily

SerializingFamily.register('gd_object')
SerializingFamily.register('save')

from . import gd_module
from . import gd_id
from . import gd_object
from . import save

from . import gd_object_szr
from . import save_szr

