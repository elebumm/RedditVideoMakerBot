import requests

from utils.console import print_step


def checkversion(__VERSION__):
    response = requests.get("https://api.github.com/repos/elebumm/RedditVideoMakerBot/releases/latest")
    latestversion = response.json()["tag_name"]
    if __VERSION__ == latestversion:
        print_step(f"You are using the newest version ({__VERSION__}) of the bot")
        return True
    else:
        print_step(
            f"You are using an older version ({__VERSION__}) of the bot. Download the newest version ({latestversion}) from https://github.com/elebumm/RedditVideoMakerBot/releases/latest"
        )
