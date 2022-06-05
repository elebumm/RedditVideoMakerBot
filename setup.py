"""

Setup Script for RedditVideoMakerBot

"""

# Imports
import os
import time
from utils.console import print_markdown
from utils.console import print_step
from utils.console import print_substep
from rich.console import Console
from utils.loader import Loader
from os.path import exists
console = Console()

setup_done = exists(".setup-done-before")

if setup_done == True:
	console.log("[red]Setup was already completed! Please make sure you have to run this script again. If you have to, please delete the file .setup-done-before")
	exit()

# These lines ensure the user:
# - knows they are in setup mode
# - knows that they are about to erase any other setup files/data.

print_step("Setup Assistant")

print_markdown(
	"### You're in the setup wizard. Ensure you're supposed to be here, then type yes to continue. If you're not sure, type no to quit."
)

# This Input is used to ensure the user is sure they want to continue.
ensureSetupIsRequired = input("Are you sure you want to continue? > ").casefold()
if ensureSetupIsRequired != "yes":
	console.print("[red]Exiting...")
	time.sleep(0.5)
	exit()
else:
	# Again, let them know they are about to erase all other setup data.
	console.print("[bold red] This will overwrite your current settings. Are you sure you want to continue? [bold green]yes/no")
	overwriteSettings = input("Are you sure you want to continue? > ").casefold()
	if overwriteSettings != "yes":
		console.print("[red]Abort mission! Exiting...")
		time.sleep(0.5)
		exit()
	else:
		# Once they confirm, move on with the script.
		console.print("[bold green]Alright! Let's get started!")
		time.sleep(1)

console.log("Ensure you have the following ready to enter:")
console.log("[bold green]Reddit Client ID")
console.log("[bold green]Reddit Client Secret")
console.log("[bold green]Reddit Username")
console.log("[bold green]Reddit Password")
console.log("[bold green]Reddit 2FA (yes or no)")
console.log("[bold green]Opacity (range of 0-1, decimals are OK)")
console.log("[bold green]Subreddit (without r/ or /r/)")
console.log("[bold green]Theme (light or dark)")
time.sleep(0.5)
console.print("[green]If you don't have these, please follow the instructions in the README.md file to set them up.")
console.print("[green]If you do have these, type yes to continue. If you dont, go ahead and grab those quickly and come back.")
confirmUserHasCredentials = input("Are you sure you have the credentials? > ").casefold()
if confirmUserHasCredentials != "yes":
	console.print("[red]I don't understand that.")
	console.print("[red]Exiting...")
	exit()
else:
	console.print("[bold green]Alright! Let's get started!")
	time.sleep(1)

"""

Begin the setup process.

"""

console.log("Enter your credentials now.")
cliID = input("Client ID > ")
cliSec = input("Client Secret > ")
user = input("Username > ")
passw = input("Password > ")
twofactor = input("2fa Enabled? (yes/no) > ")
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

with open('.setup-done-before', 'a') as f:
	f.write("This file blocks the setup assistant from running again. Delete this file to run setup again.")

loader.stop()

console.log("[bold green]Setup Complete! Returning...")

# Post-Setup: send message and try to run main.py again.
os.system("python3 main.py")
