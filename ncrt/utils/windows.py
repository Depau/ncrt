def posix_path_to_win(path: str) -> str:
    return path.replace('/', '\\')
