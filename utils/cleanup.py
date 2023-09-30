import os
import shutil
from os.path import exists


def count_items_in_directory(directory):
    """Count all items (files and subdirectories) in a directory."""
    return sum([len(files) for _, _, files in os.walk(directory)])


def cleanup(reddit_id) -> int:
    """Deletes all temporary assets in temp/

    Returns:
        int: How many files were deleted
    """
    # Check current working directory
    cwd = os.getcwd()
    print("Current working directory:", cwd)

    directory = os.path.join(cwd, "assets", "temp", reddit_id)
    print("Target directory:", directory)

    if not exists(directory):
        print("Directory does not exist!")
        return 0

    count_before_delete = count_items_in_directory(directory)
    try:
        shutil.rmtree(directory)
        print(f"Successfully deleted the directory with {count_before_delete} items!")
        return count_before_delete
    except Exception as e:
        print(f"Error encountered while deleting: {e}")
        return 0
