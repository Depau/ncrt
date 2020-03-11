import os
import sys
from pathlib import Path

import confuse

from ncrt.utils import wsl
from ncrt.utils.platform import Platform

_template = {
    'sessions_path': confuse.String(default=(
            Platform.get() == Platform.POSIX and f"{Path.home()}/.vandyke/SecureCRT/Config/Sessions" or
            Platform.get() == Platform.WSL and f"{wsl.win_env('APPDATA', wsl_path=True)}\\VanDyke\\Config\\Sessions" or
            Platform.get() == Platform.WIN and f"{os.environ['APPDATA']}\\VanDyke\\Config\\Sessions" or
            confuse.REQUIRED
    ))
}
_config = confuse.LazyConfig('ncrt', __name__)


def config(template=None):
    if template is None:
        template = _template

    return _config.get(template)


def ensure_valid(template=None):
    try:
        config(template)
    except confuse.ConfigError as err:
        print("Configuration is not valid:", file=sys.stderr)
        print("=>", str(err), file=sys.stderr)
        sys.exit(1)
