def pairs2dict(pairs):
    i = iter(pairs)
    return dict(zip(i, i))

def dict2pairs(d):
    return (x for pair in d.items() for x in pair)


def map_default(target_func, map_func):
    """ for all default values name=default in target_func replaces default to map_func(name, default) """
    pos_defaults = target_func.__defaults__
    kw_defaults = target_func.__kwdefaults__
    pos_defaults = pos_defaults if pos_defaults is not None else ()
    kw_defaults = kw_defaults if kw_defaults is not None else {}
    pos_default_names = target_func.__code__.co_varnames[-len(pos_defaults):target_func.__code__.co_argcount]
    pos_defaults = tuple(map_func(name, default) for name, default in zip(pos_default_names, pos_defaults))
    kw_defaults = {name: map_func(name, default) for name, default in kw_defaults.items()}
    target_func.__defaults__ = pos_defaults
    target_func.__kwdefaults__ = kw_defaults
