import os
from utils import settings

from moviepy.editor import VideoFileClip, concatenate_videoclips

def make_meme_video():
    if not os.path.exists("./clipped"):
        os.mkdir("./clipped")
    directory = f'./results/{settings.config["reddit"]["thread"]["subreddit"]}'

    # Get a list of all MP4 files in the directory
    mp4_files = [f for f in os.listdir(directory) if f.endswith('.mp4')]

    # Create a list of VideoFileClip objects
    clips = [VideoFileClip(os.path.join(directory, f)) for f in mp4_files]

    # Concatenate the clips into a single video
    final_clip = concatenate_videoclips(clips)

    # Write the final video to a file
    output_file = './clipped/output.mp4'
    final_clip.write_videofile(output_file)

    # Close the video clips
    for clip in clips:
        clip.close()

    # Delete the individual MP4 files
    for f in mp4_files:
        os.remove(os.path.join(directory, f))
