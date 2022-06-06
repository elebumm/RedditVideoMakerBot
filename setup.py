# Imports
import os
import time
from os.path import exists

from rich.console import Console

from utils.console import print_markdown
from utils.console import print_step

from utils.loader import Loader


console = Console()


def setup():
    if exists(".setup-done-before"):
        console.log(
            "[bold red]Setup was already done before! Please"
            + " make sure you have to run this script again.[/bold red]"
        )
        # to run the setup script again, but in better and more convenient manner.
        if input("\033[1mRun the script again? [y/N] > \033[0m") not in ["y", "Y"]:
            raise SystemExit()


    print_step("Setup Assistant")
    print_markdown(
        "### You're in the setup wizard. Ensure you're supposed to be here, "
        + "then type yes to continue. If you're not sure, type no to quit."
    )

    # This Input is used to ensure the user is sure they want to continue.
    # Again, let them know they are about to erase all other setup data.
    console.log(
        "Ensure you have the following ready to enter:\n"
        + "[bold green]Reddit Client ID\n"
        + "Reddit Client Secret\n"
        + "Reddit Username\n"
        + "Reddit Password\n"
        + "Reddit 2FA (yes or no)\n"
        + "Opacity (range of 0-1, decimals are accepted.)\n"
        + "Subreddit (without r/ or /r/)\n"
        + "Theme (light or dark)[/bold green]"
    )
    console.print(
        "[bold]If you don't have these, please follow the instructions in the README.md file to "
        + "set them up.\n If you do have these, type yes to continue. If you don't, go ahead and "
        + "grab those quickly and come back.[/bold]"
    )

    """Begin the setup process."""

    cliID = input("Client ID > ")
    cliSec = input("Client Secret > ")
    user = input("Username > ")
    passw = input("Password > ")
    twofactor = input("2FA Enabled? (yes/no) > ")
    opacity = input("Opacity? (range of 0-1) > ")
    subreddit = input("Subreddit (without r/) > ")
    theme = input("Theme? (light or dark) > ")
    console.log("Attempting to save your credentials...")

    loader = Loader("Saving Credentials...", "Done!").start()
    # you can also put a while loop here, e.g. while VideoIsBeingMade == True: ...
    time.sleep(0.5)
    console.log("Removing old .env file...")
    os.remove(".env")
    time.sleep(0.5)
    console.log("Creating new .env file...")
    with open('.env', 'a') as f:
        f.write(f'REDDIT_CLIENT_ID="{cliID}"\n')
        time.sleep(0.5)
        f.write(f'REDDIT_CLIENT_SECRET="{cliSec}"\n')
        time.sleep(0.5)
        f.write(f'REDDIT_USERNAME="{user}"\n')
        time.sleep(0.5)
        f.write(f'REDDIT_PASSWORD="{passw}"\n')
        time.sleep(0.5)
        f.write(f'REDDIT_2FA="{twofactor}"\n')
        time.sleep(0.5)
        f.write(f'THEME="{theme}"\n')
        time.sleep(0.5)
        f.write(f'SUBREDDIT="{subreddit}"\n')
        time.sleep(0.5)
        f.write(f'OPACITY="{opacity}"\n')

    with open(".setup-done-before", "a", encoding="utf-8") as f:
        f.write(
            "This file will stop the setup assistant from running again."
        )

    loader.stop()

    console.log("[bold green]Setup Complete![/bold green]")
