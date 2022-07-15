import os
from os.path import exists


def _listdir(d):  # listdir with full path
    return [os.path.join(d, f) for f in os.listdir(d)]


def cleanup() -> int:
    """Deletes all temporary assets in assets/temp

    Returns:
        int: How many files were deleted
    """
    if exists("./assets/temp"):
        count = 0
        files = [f for f in os.listdir(".") if f.endswith(".mp4") and "temp" in f.lower()]
        count += len(files)
        for f in files:
            os.remove(f)
        REMOVE_DIRS = ["./assets/temp/mp3/", "./assets/temp/png/"]
        files_to_remove = list(map(_listdir, REMOVE_DIRS))
        for directory in files_to_remove:
            for file in directory:
                count += 1
                os.remove(file)
        return count

    return 0
