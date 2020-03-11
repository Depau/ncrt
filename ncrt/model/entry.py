import posixpath
from abc import ABC
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class EntryType(Enum):
    DIRECTORY = auto()
    SESSION = auto()


@dataclass
class Entry(ABC):
    full_path: str
    name: str
    parent: Optional["DirectoryEntry"]
    entry_type: EntryType = None


@dataclass
class DirectoryEntry(Entry):
    entry_type = EntryType.DIRECTORY

    # noinspection PyShadowingBuiltins
    def child(self, pathname: str, name: str, type: EntryType) -> Entry:
        assert '/' not in pathname
        assert '/' not in name
        new_path = posixpath.join(self.full_path, pathname)

        if type == EntryType.DIRECTORY:
            cls = DirectoryEntry
        elif type == EntryType.SESSION:
            cls = SessionEntry
        else:
            raise ValueError(f"Invalid entry type: {type}")

        # noinspection PyArgumentList
        return cls(new_path, name, self, type)

    @staticmethod
    def root():
        return DirectoryEntry('/', '', None)

    @staticmethod
    def get(path: str):
        if path == '/':
            return DirectoryEntry.root()
        return DirectoryEntry(
            path,
            posixpath.basename(path),
            DirectoryEntry.get(posixpath.dirname(path)),
            EntryType.DIRECTORY
        )


@dataclass
class SessionEntry(Entry):
    user: str = None
    host: str = None
    type: str = None
    port: int = 22
    password: str = None
    password_v2: str = None

    entry_type = EntryType.SESSION

    def __post_init__(self):
        value = lambda line: line.strip().split("=", 1)[1] or None
        hex_val = lambda line: int(value(line), 16)

        # TODO: move fs_path to a better place
        from ncrt.controller.controller import NCRTController
        fs_path = NCRTController.fs_path(self.full_path)
        # TODO: remove parsing from here and create SessionReader/SessionWriter/.load()/.dump()
        with open(fs_path) as f:
            f.seek(3)  # Skip nasty 'ef bb bf' header
            for line in f.readlines():
                if line.startswith('S:"Username"='):
                    self.user = value(line)
                elif line.startswith('S:"Hostname"='):
                    self.host = value(line)
                elif line.startswith('S:"Protocol Name"='):
                    self.type = value(line)
                elif line.startswith('S:"Password"='):
                    self.password = value(line)
                elif line.startswith('S:"Password V2"='):
                    self.password_v2 = value(line)
                elif line.startswith('D:"[SSH2] Port"='):
                    self.port = hex_val(line)

        if self.user is None or self.host is None or self.type is None:
            raise ValueError(f"File is not a valid session: '{self.full_path}'")
