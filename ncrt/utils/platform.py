import os
import platform
from enum import Enum


class Platform(Enum):
    POSIX = "posix"
    WSL = "wsl"
    WIN = "win32"
    UNKNOWN = None

    @staticmethod
    def get() -> "Platform":
        if os.name == "nt":
            plat = Platform.WIN
        elif os.name == "posix":
            if platform.uname().release.endswith("Microsoft"):
                plat = Platform.WSL
            plat = Platform.POSIX
        else:
            plat = Platform.UNKNOWN

        return plat
