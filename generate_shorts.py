from pathlib import Path
from utils import settings
from video_generator import VideoGenerator
import sys

abs_directory = Path().absolute()
config = settings.check_toml(f"{abs_directory}/utils/.config.template.toml", f"{abs_directory}/config.toml")

num_of_shorts = input("\nHow many shorts would you like to be generated? ")
try:
    num_of_shorts = int(num_of_shorts)
except:
    print("Input could not be converted to integer, please enter a number!")
    sys.exit(400)

remove_past_results = input("Would you like to remove past results? (y/n) ")

if remove_past_results not in ["y", "n"]: print("Please enter a valid option (y/n)!"); sys.exit(400)
else:
    if remove_past_results == "y": remove_past_results = True
    if remove_past_results == "n": remove_past_results = False

config["settings"]["resolution_w"] = 1080
config["settings"]["resolution_h"] = 1920

video_gen = VideoGenerator(config)
video_gen.generate_shorts(num_of_shorts, remove_past_results)