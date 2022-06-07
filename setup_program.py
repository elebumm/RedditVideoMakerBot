import os
from os.path import exists

from utils.console import print_markdown, print_substep


def setup():
    if exists(".setup-done-before"):
        print_substep(
            "Setup was already done before! Please make sure you have "
            + "to run this script again.", style_="bold red"
        )
        # to run the setup script again, but in better and more convenient manner.
        if str(input("\033[1mRun the script again? [y/N] > \033[0m")).strip() not in ["y", "Y"]:
            print_substep("Permission denied!", style_="bold red")
            raise SystemExit()

    print_markdown(
        "### You're in the setup wizard. Ensure you're supposed to be here, "
        + "then type yes to continue. If you're not sure, type no to quit."
    )

    # This Input is used to ensure the user is sure they want to continue.
    # Again, let them know they are about to erase all other setup data.
    print_substep(
        "Ensure you have the following ready to enter:\n"
        + "[bold green]Reddit Client ID\n"
        + "Reddit Client Secret\n"
        + "Reddit Username\n"
        + "Reddit Password\n"
        + "Reddit 2FA (yes or no)\n"
        + "Opacity (range of 0-1, decimals are accepted.)\n"
        + "Subreddit (without r/ or /r/)\n"
        + "Theme (light or dark)[/bold green]"
        + "[bold]If you don't have these, please follow the instructions in the README.md "
        + "set them up.\nIf you do have these, type y or Y to continue. If you don't, "
        + "go ahead and grab those quickly and come back.[/bold]"
    )

    # Begin the setup process.

    cliID = input("Client ID > ")
    cliSec = input("Client Secret > ")
    user = input("Username > ")
    passw = input("Password > ")
    twofactor = input("2FA Enabled? (yes/no) > ")
    opacity = input("Opacity? (range of 0-1) > ")
    subreddit = input("Subreddit (without r/) > ")
    theme = input("Theme? (light or dark) > ")

    if exists(".env"):
        os.remove(".env")

    with open(".env", "a", encoding="utf-8") as f:
        f.write(
            f'REDDIT_CLIENT_ID="{cliID}"\n'
            + f'REDDIT_CLIENT_SECRET="{cliSec}"\n'
            + f'REDDIT_USERNAME="{user}"\n'
            + f'REDDIT_PASSWORD="{passw}"\n'
            + f'REDDIT_2FA="{twofactor}"\n'
            + f'THEME="{theme}"\n'
            + f'SUBREDDIT="{subreddit}"\n'
            + f'OPACITY="{opacity}"\n'
        )

    with open(".setup-done-before", "a", encoding="utf-8") as f:
        f.write("This file will stop the setup assistant from running again.")

    print_substep("[bold green]Setup Complete![/bold green]")
