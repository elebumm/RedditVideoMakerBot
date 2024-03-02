import requests

from utils.console import print_step


def checkversion(__VERSION__: str):
    response = requests.get(
        "https://api.github.com/repos/elebumm/RedditVideoMakerBot/releases/latest"
    )
    if response.status_code == 403:  # Rate limit
        print(
            f"Skipping script version check because we exceeded GitHub's rate limit. Using version ({__VERSION__})."
        )
        return
    latestversion = response.json()["tag_name"]
    if __VERSION__ == latestversion:
        print_step(f"You are using the newest version ({__VERSION__}) of the bot")
        return True
    elif __VERSION__ < latestversion:
        print_step(
            f"You are using an older version ({__VERSION__}) of the bot. Download the newest version ({latestversion}) from https://github.com/elebumm/RedditVideoMakerBot/releases/latest"
        )
    else:
        print_step(
            f"Welcome to the test version ({__VERSION__}) of the bot. Thanks for testing and feel free to report any bugs you find."
        )
