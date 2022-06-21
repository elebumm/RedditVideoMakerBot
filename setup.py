#!/usr/bin/env python3
# Setup Script for RedditVideoMakerBot


# Imports
import os
import subprocess
import re
from utils.console import print_markdown
from utils.console import print_step
from rich.console import Console
from utils.loader import Loader
from utils.console import handle_input

console = Console()


if os.path.isfile(".setup-done-before"):
    console.print(
        "[red]WARNING: Setup was already completed! Please make sure you have to run this script again. If that is such, delete the file .setup-done-before"
    )
    exit()

# These lines ensure the user:
# - knows they are in setup mode
# - knows that they are about to erase any other setup files/data.

print_step("Setup Assistant")
print_markdown(
    "### You're in the setup wizard. Ensure you're supposed to be here, then type yes to continue. If you're not sure, type no to quit."
)


# This Input is used to ensure the user is sure they want to continue.
if input("Are you sure you want to continue? > ").strip().casefold() != "yes":
    console.print("[red]Exiting...")
    exit()
# This code is inaccessible if the prior check fails, and thus an else statement is unnecessary


# Again, let them know they are about to erase all other setup data.
console.print(
    "[bold red] This will overwrite your current settings. Are you sure you want to continue? [bold green]yes/no"
)


if input("Are you sure you want to continue? > ").strip().casefold() != "yes":
    console.print("[red]Abort mission! Exiting...")
    exit()
# This is once again inaccessible if the prior checks fail
# Once they confirm, move on with the script.
console.print("[bold green]Alright! Let's get started!")

print()
console.print("Ensure you have the following ready to enter:")
console.print("[bold green]Reddit Client ID")
console.print("[bold green]Reddit Client Secret")
console.print("[bold green]Reddit Username")
console.print("[bold green]Reddit Password")
console.print("[bold green]Reddit 2FA (yes or no)")
console.print("[bold green]Opacity (range of 0-1, decimals are OK)")
console.print("[bold green]Subreddit (without r/ or /r/)")
console.print("[bold green]Theme (light or dark)")
console.print(
    "[green]If you don't have these, please follow the instructions in the README.md file to set them up."
)
console.print(
    "[green]If you do have these, type yes to continue. If you dont, go ahead and grab those quickly and come back."
)
print()


if input("Are you sure you have the credentials? > ").strip().casefold() != "yes":
    console.print("[red]I don't understand that.")
    console.print("[red]Exiting...")
    exit()


console.print("[bold green]Alright! Let's get started!")

# Begin the setup process.

console.print("Enter your credentials now.")
client_id = handle_input(
    "Client ID > ",
    False,
    "[-a-zA-Z0-9._~+/]+=*",
    "That is somehow not a correct ID, try again.",
    12,
    30,
    "The ID should be over 12 and under 30 characters, double check your input.",
)
client_sec = handle_input(
    "Client Secret > ",
    False,
    "[-a-zA-Z0-9._~+/]+=*",
    "That is somehow not a correct secret, try again.",
    20,
    40,
    "The secret should be over 20 and under 40 characters, double check your input.",
)
user = handle_input(
    "Username > ",
    False,
    r"[_0-9a-zA-Z]+",
    "That is not a valid user",
    3,
    20,
    "A username HAS to be between 3 and 20 characters",
)
passw = handle_input("Password > ", False, ".*", "", 8, None, "Password too short")
twofactor = handle_input(
    "2fa Enabled? (yes/no) > ",
    False,
    r"(yes)|(no)",
    "You need to input either yes or no",
)
opacity = handle_input(
    "Opacity? (range of 0-1) > ",
    float,
    ".*",
    "You need to input a number between 0 and 1",
    0,
    1,
    "Your number is not between 0 and 1",
)
subreddit = handle_input(
    "Subreddit (without r/) > ",
    False,
    r"[_0-9a-zA-Z]+",
    "This subreddit cannot exist, make sure you typed it in correctly and removed the r/ (or /r/).",
    3,
    20,
    "A subreddit name HAS to be between 3 and 20 characters",
)
theme = handle_input(
    "Theme? (light or dark) > ",
    False,
    r"(light)|(dark)",
    "You need to input 'light' or 'dark'",
)
loader = Loader("Attempting to save your credentials...", "Done!").start()
# you can also put a while loop here, e.g. while VideoIsBeingMade == True: ...
console.print("Writing to the .env file...")
with open(".env", "w") as f:
    f.write(
        f"""REDDIT_CLIENT_ID="{client_id}"
REDDIT_CLIENT_SECRET="{client_sec}"
REDDIT_USERNAME="{user}"
REDDIT_PASSWORD="{passw}"
REDDIT_2FA="{twofactor}"
THEME="{theme}"
SUBREDDIT="{subreddit}"
OPACITY={opacity}
"""
    )

with open(".setup-done-before", "w") as f:
    f.write(
        "This file blocks the setup assistant from running again. Delete this file to run setup again."
    )

loader.stop()

console.print("[bold green]Setup Complete! Returning...")

# Post-Setup: send message and try to run main.py again.
subprocess.call("python3 main.py", shell=True)
