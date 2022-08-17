import requests

from os import makedirs
from fileinput import filename
from utils.console import print_step, print_substep
from utils import settings
from pathlib import Path

# Checks if suboverlay is a thing, if not it downloads the file
# Uses Google Drive Direct Link to store the file
# Source of the animation https://fortatelier.com/free-youtube-subscribe-animation-overlays/
def download_suboverlay():
    if settings.config["settings"]["sub_overlay"]:
        if Path(f"assets/subOverlay/subOverlayClip.mov").is_file():
            return

        #Generate path and folders
        makedirs(f'assets/subOverlay')

        URL = "https://drive.google.com/u/0/uc?id=16ajH0maciiWgWNgA-PNh29GZe9xqZmZR&export=download"

        print_step("We need to download the subscribe overlay, this only needs to be done once!")
        print_substep("Downloading subscribe overlay please wait....")

        subOverlayFile = requests.get(URL, verify=False)
        open(f'assets/subOverlay/subOverlayClip.mov', 'wb').write(subOverlayFile.content)

        print_substep("Subscribe overlay has been downloaded!", style="bold green")
