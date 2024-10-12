from attrs import field, define as attrs_init_only, define as define_gd  # trick PyCharm
from functools import partial

attrs_init_only = partial(
    attrs_init_only,
    repr=False,
    unsafe_hash=False,
    hash=False,
    init=True,
    slots=False,
    eq=False,
    getstate_setstate=False,
    match_args=False
)

define_gd = partial(
    define_gd,
    slots=False
)
