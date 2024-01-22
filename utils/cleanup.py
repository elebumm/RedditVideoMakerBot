import os
import shutil
from os.path import exists


def _listdir(d):  # listdir with full path
    return [os.path.join(d, f) for f in os.listdir(d)]


def cleanup(reddit_id) -> int:
    """Deletes all temporary assets in assets/temp

    Returns:
        int: How many files were deleted
    """
    directory = f"assets/temp/{reddit_id}/"
    deleted_files_count = 0

    if exists(directory):
        # Count the number of files before deleting
        for root, dirs, files in os.walk(directory):
            deleted_files_count += len(files)

        shutil.rmtree(directory)

        return deleted_files_count
