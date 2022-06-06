# Main
from utils.console import print_markdown
from utils.console import print_step
from utils.console import print_substep
from rich.console import Console
import time
from reddit.subreddit import get_subreddit_threads
from video_creation.background import download_background, chop_background_video
from video_creation.voices import save_text_to_mp3
from video_creation.screenshot_downloader import download_screenshots_of_reddit_posts
from video_creation.final_video import make_final_video
from utils.loader import Loader
from dotenv import load_dotenv

console = Console()
from dotenv import load_dotenv
import os, time, shutil

configured = True
REQUIRED_VALUES = [
    "REDDIT_CLIENT_ID",
    "REDDIT_CLIENT_SECRET",
    "REDDIT_USERNAME",
    "REDDIT_PASSWORD",
    "OPACITY",
]


print_markdown(
    "### Thanks for using this tool! [Feel free to contribute to this project on GitHub!](https://lewismenelaws.com) If you have any questions, feel free to reach out to me on Twitter or submit a GitHub issue."
)

"""

Load .env file if exists. If it doesnt exist, print a warning and launch the setup wizard.
If there is a .env file, check if the required variables are set. If not, print a warning and launch the setup wizard.

"""

client_id = os.getenv("REDDIT_CLIENT_ID")
client_secret = os.getenv("REDDIT_CLIENT_SECRET")
username = os.getenv("REDDIT_USERNAME")
password = os.getenv("REDDIT_PASSWORD")
reddit2fa = os.getenv("REDDIT_2FA")

load_dotenv()

console.log("[bold green]Checking environment variables...")
time.sleep(1)


if not os.path.exists(".env"):
    configured = False
    console.log("[red] Your .env file is invalid, or was never created. Standby.")

for val in REQUIRED_VALUES:
    #print(os.getenv(val))
    if val not in os.environ or not os.getenv(val):
        console.log(f'[bold red]Missing Variable: "{val}"')
        configured = False
        console.log(
            "[red]Looks like you need to set your Reddit credentials in the .env file. Please follow the instructions in the README.md file to set them up."
        )
        time.sleep(0.5)
        console.log(
            "[red]We can also launch the easy setup wizard. type yes to launch it, or no to quit the program."
        )
        setup_ask = input("Launch setup wizard? > ")
        if setup_ask == "yes":
            console.log("[bold green]Here goes nothing! Launching setup wizard...")
            time.sleep(0.5)
            os.system("python3 setup.py")

        elif setup_ask == "no":
            console.print("[red]Exiting...")
            time.sleep(0.5)
            exit()
        else:
            console.print("[red]I don't understand that. Exiting...")
            time.sleep(0.5)
            exit()
try:
    float(os.getenv("OPACITY"))
except:
    console.log(
        f"[red]Please ensure that OPACITY is set between 0 and 1 in your .env file"
    )
    configured = False
    exit()
console.log("[bold green]Enviroment Variables are set! Continuing...")

if configured:
    reddit_object = get_subreddit_threads()
    length, number_of_comments = save_text_to_mp3(reddit_object)
    download_screenshots_of_reddit_posts(
        reddit_object, number_of_comments, os.getenv("THEME", "light")
    )
    download_background()
    chop_background_video(length)
    final_video = make_final_video(number_of_comments)
