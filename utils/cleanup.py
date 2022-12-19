import os
from os.path import exists


def _listdir(d):  # listdir with full path
    return [os.path.join(d, f) for f in os.listdir(d)]


def cleanup(id) -> int:
    """Deletes all temporary assets in assets/temp

    Returns:
        int: How many files were deleted
    """
    if exists(f"../assets/temp/{id}/"):
        count = 0
        files = [f for f in os.listdir(f"../assets/temp/{id}/") if f.endswith(".mp4")]
        count += len(files)
        for f in files:
            os.remove(f"../assets/temp/{id}/{f}")
        REMOVE_DIRS = [f"../assets/temp/{id}/mp3/", f"../assets/temp/{id}/png/"]
        for d in REMOVE_DIRS:
            if exists(d):
                count += len(_listdir(d))
                for f in _listdir(d):
                    os.remove(f)
                os.rmdir(d)
        os.rmdir(f"../assets/temp/{id}/")
        return count
