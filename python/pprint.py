from collections import deque

# TODO: REFACTOR THIS ABOMINATION

prepr_funcs = {}

def set_key(d, *keys):
    def dec(func):
        for key in keys:
            d[key] = func
        return func
    return dec

@set_key(prepr_funcs, list, deque)
def _(l: list, sets):
    if not l:
        return '[]'
    if sets.numerate:
        s = (f'{i}: {_prepr(v, sets)}' for i, v in enumerate(l))
    else:
        s = (_prepr(v, sets) for i, v in enumerate(l))
    return ('[\n' + ',\n'.join(s)).replace('\n', '\n'+sets.indent) + '\n]'

@set_key(prepr_funcs, tuple)
def _(l: tuple, sets):
    if not l:
        return '()'
    if sets.numerate:
        s = (f'{i}: {_prepr(v, sets)}' for i, v in enumerate(l))
    else:
        s = (_prepr(v, sets) for i, v in enumerate(l))
    return ('(\n' + ',\n'.join(s)).replace('\n', '\n'+sets.indent) + '\n)'

@set_key(prepr_funcs, dict)
def _(d: dict, sets):
    if not d:
        return '{}'
    return ('{\n' + ',\n'.join(f'{_prepr(k, sets)}: {_prepr(v, sets)}' for k, v in d.items())) \
    .replace('\n', '\n'+sets.indent) + '\n}'

@set_key(prepr_funcs, object)
def _(o: object, sets, *, fields=None):
    if not hasattr(o, '__dict__'):
        slots = set()
        for base in o.__class__.__mro__[::-1]:
            slots.update(getattr(base, '__slots__', ()))
        if fields is not None:
            slots &= fields
        s = ',\n'.join(f'{name} = {_prepr(getattr(o, name), sets)}' for name in slots)
        if s:
            s = ('\n' + s).replace('\n', '\n' + sets.indent) + '\n'
        return f'{o.__class__.__name__}({s})'
    keys = o.__dict__.keys()
    if fields is not None:
        keys &= fields
    s = ',\n'.join(f'{name} = {_prepr(o.__dict__[name], sets)}' for name in keys)
    if s:
        s = ('\n' + s).replace('\n', '\n'+sets.indent) + '\n'
    return f'{o.__class__.__name__}({s})'

from dataclasses import dataclass, field
import copy

@dataclass
class SetsClass:
    mem: set
    indent: str = '   '
    numerate: bool = False

def _prepr(obj, sets):
    if id(obj) in sets.mem:
        return '...'
    sets = copy.copy(sets)
    sets.mem = sets.mem.copy()
    sets.mem.add(id(obj))

    if hasattr(obj, '__prepr__'):
        return obj.__prepr__(sets)
    if type(obj) in prepr_funcs:
        return prepr_funcs[type(obj)](obj, sets)
    if obj.__repr__.__qualname__ == 'object.__repr__' or \
    hasattr(obj.__class__, '__dataclass_fields__') or \
    hasattr(obj.__class__, '__attrs_attrs__'):
        return prepr_funcs[object](obj, sets)
    return repr(obj)

def prepr(obj, *args, **kwargs):
    return _prepr(obj, SetsClass(set(), *args, **kwargs))

def pprint(*objs, **kwargs):
    for obj in objs:
        print(prepr(obj, **kwargs))
