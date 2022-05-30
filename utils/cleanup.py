import os
import glob
from utils.console import print_step, print_substep


def cleanup():
    """
    Deletes all files that was used to create the final file.
    """
    print_step("Cleaning up working files... 🗑")
    files = glob.glob("assets/mp3/*")
    for f in files:
        os.remove(f)

    files = glob.glob("assets/png/*")
    for f in files:
        os.remove(f)

    os.remove("assets/mp4/clip.mp4")

    print_substep("Done! 🎉")
