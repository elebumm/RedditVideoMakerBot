import requests

from os import makedirs
from os import path
from fileinput import filename
from utils.console import print_step, print_substep
from utils import settings
from pathlib import Path

# Checks if suboverlay is a thing, if not it downloads the file
# Uses Google Drive Direct Link to store the file
def download_suboverlay():
    if settings.config["settings"]["sub_overlay"]:
        URL = "https://drive.google.com/u/0/uc?id=16ajH0maciiWgWNgA-PNh29GZe9xqZmZR&export=download"
        fileName = "youtube"

        if settings.config["settings"]["sub_overlay_name"] == "tiktok":
            URL = "https://drive.google.com/u/0/uc?id=1N7tmEacL5GSUpVukxwza7OL7ihfAdShq&export=download"
            fileName = "tiktok"

        if settings.config["settings"]["sub_overlay_name"] == "instagram":
            URL = "https://drive.google.com/u/0/uc?id=19Yvuuojba8ixIP8whs0QEqw9gTer4T20&export=download"
            fileName = "instagram"

        if Path(f"assets/subOverlay/{fileName}.mov").is_file():
            return

        #Generate path and folders
        if not path.isdir(f'assets/subOverlay'):
            makedirs(f'assets/subOverlay')

        print_step("We need to download the subscribe overlay, this only needs to be done once!")
        print_substep("Downloading subscribe overlay please wait....")

        subOverlayFile = requests.get(URL, verify=False)
        open(f'assets/subOverlay/{fileName}.mov', 'wb').write(subOverlayFile.content)

        print_substep("Subscribe overlay has been downloaded!", style="bold green")
