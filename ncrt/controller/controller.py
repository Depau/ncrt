import errno
import ntpath
import os
import posixpath
from os import PathLike
from typing import Iterable, Union, Generator, cast, Optional

from ncrt.config import config
from ncrt.controller.action import SessionActionBase
from ncrt.model.entry import DirectoryEntry, SessionEntry, Entry, EntryType
from ncrt.ui.viewmodel import ViewModelBase
from ncrt.utils.platform import Platform
from ncrt.utils.windows import posix_path_to_win


class NCRTController:
    def __init__(self, view_model: ViewModelBase):
        self.view_model = view_model

    @staticmethod
    def _cd_parent(old_path: DirectoryEntry) -> DirectoryEntry:
        if old_path.parent:
            return old_path.parent
        else:
            return old_path

    @staticmethod
    def fs_path(path) -> str:
        if Platform.get() == Platform.WIN:
            # [1:] : remove leading /
            win_path = posix_path_to_win(path[1:])
            return ntpath.join(config().sessions_path, win_path)
        else:
            return posixpath.join(config().sessions_path, path)

    def cd(self, path: Union[DirectoryEntry, bytes, str, PathLike]) -> DirectoryEntry:
        cwd = self.view_model.current_dir
        new_path = None
        if type(path) == DirectoryEntry:
            new_path = path
        elif type(path) in (bytes, str, PathLike):
            if path == "..":
                new_path = self._cd_parent(cwd)
            else:
                internal_path = posixpath.join(cwd.full_path, path)
                fs_path = self.fs_path(internal_path)

                if not os.path.exists(fs_path):
                    raise OSError(errno.ENOENT, os.strerror(errno.ENOENT), new_path)

                if not os.path.isdir(fs_path):
                    raise OSError(errno.ENOTDIR, os.strerror(errno.ENOTDIR), new_path)

                new_path = DirectoryEntry.get(internal_path)

        assert new_path
        self.view_model.current_dir = new_path
        return new_path

    @staticmethod
    def _get_session_for_file(parent_dir: DirectoryEntry, filename: str) -> Optional[SessionEntry]:
        pretty_name, ext = posixpath.splitext(filename)
        if ext.lower() != ".ini":
            return None
        try:
            return parent_dir.child(filename, pretty_name, EntryType.SESSION)
        except ValueError:
            return None

    async def ls(self, cwd: DirectoryEntry = None) -> Generator[Entry, None, None]:
        if cwd is None:
            cwd = self.view_model.current_dir

        fs_path = self.fs_path(cwd.full_path)

        # TODO: Consider switching to an async dir listing method if performance issues arise
        for dir_entry in os.scandir(fs_path):
            if dir_entry.is_dir():
                yield cwd.child(dir_entry.name, dir_entry.name, EntryType.DIRECTORY)
            elif dir_entry.is_file():
                session = self._get_session_for_file(cwd, dir_entry.name)
                if session:
                    yield session

    async def find(self, query: str, search_root: DirectoryEntry = None) -> Generator[Entry, None, None]:
        if search_root is None:
            search_root = self.view_model.current_dir

        fs_path = self.fs_path(search_root.full_path)

        for dir_entry in os.scandir(fs_path):
            if dir_entry.is_dir():
                child_dir = cast(DirectoryEntry, search_root.child(dir_entry.name, dir_entry.name, EntryType.DIRECTORY))
                if query in child_dir.name:
                    yield child_dir
                else:
                    async for i in self.find(query, child_dir):
                        yield i
            elif dir_entry.is_file():
                if query in dir_entry.name:
                    session = self._get_session_for_file(search_root, dir_entry.name)
                    if session:
                        yield session

    async def get_actions(self, path: SessionEntry) -> Iterable[SessionActionBase]:
        pass
