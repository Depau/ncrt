import ntpath
import posixpath
import subprocess

from ncrt.utils.platform import Platform

_win_env_cache = {}


def win_path_to_wsl(path: str) -> str:
    path = ntpath.normcase(path)
    if path.startswith(r"\\") or path.startswith(r'\?'):
        raise NotImplementedError(f"Network or Object Manager paths on WSL are not supported: '{path}'")

    if not path.startswith('\\') and path[1:2] != ":\\":
        raise NotImplementedError(f"Relative Windows paths on WSL are not supported: '{path}'")

    if path.startswith('\\'):
        letter = win_env('SystemDrive')[0]
    else:
        letter, path = path.split(":", 1)

    letter = letter.lower()
    path = path.replace('\\', '/')
    unixpath = f'/mnt/{letter}/{path}'

    return posixpath.normpath(unixpath)


def win_env(var: str, wsl_path=False) -> str:
    assert Platform.get() == Platform.WSL
    var = var.upper()

    if var not in _win_env_cache:
        percvar = f'%{var}%'
        p = subprocess.run(['cmd.exe', '/C', 'ECHO', percvar], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                           encoding="utf-8")

        value = p.stdout.strip()

        if value == percvar or value == '':
            value = None

        _win_env_cache[var] = value

    output = _win_env_cache[var]

    if wsl_path:
        output = win_path_to_wsl(output)

    return output
