from collections.abc import Callable
from functools import partial
from typing import Any, TYPE_CHECKING
import inspect

from python.pprint import pprint
from serializing import *
from tools.funcs import nothing, args_to_kwargs

S = SerializingFamily.register('test')

S['test'] = WrapKeys(
    WrapKeyInfo('k1', 'foo', Func(int, str), '0'),
    WrapKeyInfo('k2', None, Func(int, str), '1', optimize_key=False),
    WrapKeyInfo('k3', 'bar', Func(int, str), default_value=42, optimize_key=False),
    WrapKeyInfo(..., 'unused', Func(nothing, nothing), '2'),
)

data = {
    'k1': '11',
    'k2': '12',
    'k10': '43'
}

value = S['test'].analyze(data)
pprint(value)
data2 = S['test'].compile(value)
pprint(data2)

# -----------------------------------------------------------------------

from maker import Maker

key = Maker(WrapKeyInfo)
key.setup(optimize_key=True)
key(int).setup(serializer=Func(int, str), default_data='0')

S['test2'] = WrapKeys(
    key[int]('k1', 'foo'),
    key[int]('K2', None, optimize_key=False),
    key[int]('k3', 'bar', default_data=None, default_value=42, optimize_key=False),
)
