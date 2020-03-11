from abc import ABC
from dataclasses import dataclass


@dataclass
class SessionActionBase(ABC):
    name: str
