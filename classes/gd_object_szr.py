from serializing import *
import recognizing as R
import classes.gd_object as gd_object

serializers = SerializingFamily.register('gd_object')


serializers[gd_object.GdObjectBase] =


