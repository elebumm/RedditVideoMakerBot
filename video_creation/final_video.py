from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    ImageClip,
    concatenate_videoclips,
    concatenate_audioclips,
    CompositeAudioClip,
    CompositeVideoClip,
)
import reddit.subreddit 
import re
from utils.console import print_step
from dotenv import load_dotenv
import os
from pathlib import Path

W, H = 1080, 1920



def make_final_video(number_of_clips):
    """Generates and saves final video to assets/generated-videos

    Args:
        number_of_clips (int): The index of clips(comments) to go up to 
    """
    # Calls opacity from the .env
    load_dotenv()
    opacity = os.getenv('OPACITY')
    
    print_step("Creating the final video...")

    VideoFileClip.reW = lambda clip: clip.resize(width=W)
    VideoFileClip.reH = lambda clip: clip.resize(width=H)

    background_clip = (
        VideoFileClip("assets/mp4/clip.mp4")
        .without_audio()
        .resize(height=H)
        .crop(x1=1166.6, y1=0, x2=2246.6, y2=1920)
    )

    audio_clips, audio_composite = gatherAudioClips(number_of_clips)

    image_clips = gatherImages(number_of_clips, opacity, audio_clips)


    if Path(f"assets/mp3/posttext.mp3").is_file():
        image_clips.insert(
            0,
            ImageClip(f"assets/png/title.png")
            .set_duration(audio_clips[0].duration + audio_clips[1].duration)
            .set_position("center")
            .resize(width=W - 100)
            .set_opacity(float(opacity)),
            )
    else:
        image_clips.insert(
            0,
            ImageClip(f"assets/png/title.png")
            .set_duration(audio_clips[0].duration)
            .set_position("center")
            .resize(width=W - 100)
            .set_opacity(float(opacity)),
            )
    image_concat = concatenate_videoclips(image_clips).set_position(
        ("center", "center")
    )
    image_concat.audio = audio_composite
    final = CompositeVideoClip([background_clip, image_concat])

    saveVideo(final)

def saveVideo(final):
    """Writes video to assets/generated videos

    Args:
        final (CompositeVideoClip): Final video object
    """


    if not Path("assets/generated-videos").is_dir():
        Path.mkdir("assets/generated-videos")

    raw_filename = Path("assets", "generated-videos") / (reddit.subreddit.submission.title + ".mp4")
    cleaned_filename = (re.sub('[?\"%*:|<>]', '', str(raw_filename)))
    final.write_videofile(cleaned_filename, fps=30, audio_codec="aac", audio_bitrate="192k")

def gatherImages(number_of_clips, opacity, audio_clips):
    """Gathers thread screenshots from assets/png

    Args:
        number_of_clips (int): number of screenshots to be put into the video
        opacity (float): how clear the comment is going to be in the video
        audio_clips (list[AudioFileClip]): TTS of the thread

    Returns:
        list[ImageClip]: all the comments with TTS over it
    """
    image_clips = []
    for i in range(0, number_of_clips):
        image_clips.append(
            ImageClip(f"assets/png/comment_{i}.png")
            .set_duration(audio_clips[i + 1].duration)
            .set_position("center")
            .resize(width=W - 100)
            .set_opacity(float(opacity)),
        )
        
    return image_clips

def gatherAudioClips(number_of_clips):
    """Gathers all audio clips

    Args:
        number_of_clips (int): Which index to go to in the list of audio files

    Returns:
        tuple[list,CompositeAudioClip]: First index is the list of audio clips, second is all the audio clips put together
    """    
    audio_clips = []
    for i in range(0, number_of_clips):
        audio_clips.append(AudioFileClip(f"assets/mp3/{i}.mp3"))
    audio_clips.insert(0, AudioFileClip(f"assets/mp3/title.mp3"))
    try:
        audio_clips.insert(1, AudioFileClip(f"assets/mp3/posttext.mp3"))
    except:
        OSError()
    audio_concat = concatenate_audioclips(audio_clips)
    audio_composite = CompositeAudioClip([audio_concat])
    return audio_clips,audio_composite