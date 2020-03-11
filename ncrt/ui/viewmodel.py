from abc import ABC
from dataclasses import dataclass

from ncrt.model.entry import DirectoryEntry


@dataclass
class ViewModelBase(ABC):
    current_dir: DirectoryEntry = DirectoryEntry.root()
