import copy
from collections import deque
from typing import TypeVar, Iterator, Literal

from attrs import define, field
from contextlib import contextmanager

from context import Contextable, SimpleContext
from ignore_default import IgnoreDefault
from python.named_const import Missed
from serializing import SerializingFamily
import tools.decompressing
import tools.plist

from classes.gd_module import GdModule

S = SerializingFamily.get('save')

T = TypeVar('T')

__all__ = ('LevelInfo', 'LevelSettings', 'Level', 'Save')


@define(slots=False)
class LevelInfo(IgnoreDefault):
    name: str = field()
    data: str = field()
    revision: int = field(default=0)
    description: str = field(default='')

    @classmethod
    def LoadFromGMD(cls, data: bytes) -> 'LevelInfo':
        json_data = tools.plist.plist_to_json(data)
        return S[LevelInfo].analyze(json_data)

    def SaveToGMD(self) -> bytes:
        json_data = S[LevelInfo].compile(self)
        return tools.plist.json_to_plist(json_data)

    def decompress(self, mode: Literal['r', 'w', 'rw'] = 'rw') -> 'Iterator[Level]':
        read, write = {'r': (True, False), 'w': (False, True), 'rw': (True, True)}[mode]
        if 'data' not in self.__dict__ or not read:  # get empty level
            raise NotImplementedError()
        else:
            level: Level = S[Level].analyze(self)
        with level:
            yield level
        if write:
            self.data = S[Level].compile(level)

    decompress = contextmanager(decompress)

    def clone(self, new_name: str | None = None) -> 'LevelInfo':
        level = copy.deepcopy(self)
        if new_name is not None:
            level.name = new_name
        return level


@define(slots=False)
class LevelSettings:
    ...


@define(slots=False)
class Level(Contextable, SimpleContext):
    info: LevelInfo
    settings: LevelSettings
    module: GdModule

    @contextmanager
    def __context__(self):
        with super().__context__(), self.module:
            yield self


def _extract_name_revision(name: str | tuple[str, int]):
    if isinstance(name, str):
        return name, None
    name, revision = name
    return name, revision


@define(slots=False)
class Save:
    levels: deque[LevelInfo] = field(factory=deque, converter=deque)

    def __attrs_post_init__(self):
        self.levels = deque(self.levels)

    @classmethod
    def LoadFromDAT(cls, data: bytes) -> 'Save':
        xml_data = tools.decompressing.decrypt_save_xml(data)
        json_data = tools.plist.plist_to_json(xml_data)
        return S[Save].analyze(json_data)

    def SaveToDAT(self, ios_mode: bool = False) -> bytes:
        json_data = S[Save].compile(self)
        xml_data = tools.plist.json_to_plist(json_data)
        return tools.decompressing.encrypt_save_xml(xml_data, ios_mode)

    def has(self, name: str | tuple[str, int]) -> bool:
        name, revision = _extract_name_revision(name)
        for level in self.levels:
            if level.name != name:
                continue
            if revision is None or level.revision == revision:
                return True
        return False

    def get(self, name: str | tuple[str, int], default: T = Missed) -> LevelInfo | T:
        name_, revision = _extract_name_revision(name)
        for level in self.levels:
            if level.name != name_:
                continue
            if revision is None or level.revision == revision:
                return level
        if default is not Missed:
            return default
        raise KeyError(name)

    def add(self, level: LevelInfo):
        while self.has((level.name, level.revision)):
            level.revision += 1
        self.levels.appendleft(level)

    def clone(self, name: str | tuple[str, int], new_name: str | None = None) -> LevelInfo:
        level = self.get(name)
        new_level = level.clone(new_name)
        self.add(new_level)
        return new_level
