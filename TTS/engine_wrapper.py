import os
import re
import ffmpeg
from pathlib import Path
from typing import Tuple

import numpy as np
import translators
from moviepy.audio.AudioClip import AudioClip
from moviepy.audio.fx.volumex import volumex
# from moviepy.editor import AudioFileClip
from rich.progress import track

from utils import settings
from utils.console import print_step, print_substep
from utils.ffmpeg import get_duration # , ffmpeg_progress_run
from utils.voice import sanitize_text

from pydub import AudioSegment


DEFAULT_MAX_LENGTH: int = (
    50  # Video length variable, edit this on your own risk. It should work, but it's not supported
)


class TTSEngine:

    """Calls the given TTS engine to reduce code duplication and allow multiple TTS engines.

    Args:
        tts_module            : The TTS module. Your module should handle the TTS itself and saving to the given path under the run method.
        reddit_object         : The reddit object that contains the posts to read.
        path (Optional)       : The unix style path to save the mp3 files to. This must not have leading or trailing slashes.
        max_length (Optional) : The maximum length of the mp3 files in total.

    Notes:
        tts_module must take the arguments text and filepath.
    """

    def __init__(
        self,
        tts_module,
        reddit_object: dict,
        path: str = "assets/temp/",
        max_length: int = DEFAULT_MAX_LENGTH,
        last_clip_length: int = 0,
    ):
        self.tts_module = tts_module()
        self.reddit_object = reddit_object

        self.redditid = re.sub(r"[^\w\s-]", "", reddit_object["thread_id"])
        self.path = path + self.redditid + "/mp3"
        self.max_length = max_length
        self.length = 0
        self.last_clip_length = last_clip_length

    def add_periods(
        self,
    ):  # adds periods to the end of paragraphs (where people often forget to put them) so tts doesn't blend sentences
        for comment in self.reddit_object["comments"]:
            # remove links
            regex_urls = r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"
            comment["comment_body"] = re.sub(regex_urls, " ", comment["comment_body"])
            comment["comment_body"] = comment["comment_body"].replace("\n", ". ")
            comment["comment_body"] = re.sub(r"\bAI\b", "A.I", comment["comment_body"])
            comment["comment_body"] = re.sub(r"\bAGI\b", "A.G.I", comment["comment_body"])
            if comment["comment_body"][-1] != ".":
                comment["comment_body"] += "."
            comment["comment_body"] = comment["comment_body"].replace(". . .", ".")
            comment["comment_body"] = comment["comment_body"].replace(".. . ", ".")
            comment["comment_body"] = comment["comment_body"].replace(". . ", ".")
            comment["comment_body"] = re.sub(r'\."\.', '".', comment["comment_body"])

    def run(self) -> Tuple[int, int]:
        Path(self.path).mkdir(parents=True, exist_ok=True)
        # print_step("Saving Text to MP3 files...")

        self.add_periods()
        self.call_tts("title", process_text(self.reddit_object["thread_title"]))
        # processed_text = ##self.reddit_object["thread_post"] != ""
        idx = 0

        if settings.config["settings"]["storymode"]:
            if settings.config["settings"]["storymodemethod"] == 0:
                if len(self.reddit_object["thread_post"]) > self.tts_module.max_chars:
                    self.split_post(self.reddit_object["thread_post"], "postaudio")
                else:
                    self.call_tts("postaudio", process_text(self.reddit_object["thread_post"]))
            elif settings.config["settings"]["storymodemethod"] == 1:
                for idx, text in track(enumerate(self.reddit_object["thread_post"]), "🎶 Creating audio from text...", total=len(self.reddit_object["thread_post"])):
                    self.call_tts(f"postaudio-{idx}", process_text(text))

        else:
            for idx, comment in track(enumerate(self.reddit_object["comments"]), "💾 Saving...", total=len(self.reddit_object["comments"])):
                # ! Stop creating mp3 files if the length is greater than max length.
                if self.length > self.max_length and idx > 1:
                    self.length -= self.last_clip_length
                    idx -= 1
                    break
                if (
                    len(comment["comment_body"]) > self.tts_module.max_chars
                ):  # Split the comment if it is too long
                    self.split_post(comment["comment_body"], idx)  # Split the comment
                else:  # If the comment is not too long, just call the tts engine
                    self.call_tts(f"{idx}", process_text(comment["comment_body"]))

        print_substep("Created audio from text successfully!", style="bold green")
        return self.length, idx

    def split_post(self, text: str, idx):
        split_files = []
        split_text = [
            x.group().strip()
            for x in re.finditer(
                r" *(((.|\n){0," + str(self.tts_module.max_chars) + "})(\.|.$))", text
            )
        ]
        self.create_silence_mp3()

        idy = None
        for idy, text_cut in enumerate(split_text):
            newtext = process_text(text_cut)
            # print(f"{idx}-{idy}: {newtext}\n")

            if not newtext or newtext.isspace():
                print("newtext was blank because sanitized split text resulted in none")
                continue
            else:
                self.call_tts(f"{idx}-{idy}.part", newtext)
                concat_parts=[]
                # with open(f"{self.path}/list.txt", "w") as f:
                for idz in range(0, len(split_text)):
                        # f.write("file " + f"'{idx}-{idz}.part.mp3'" + "\n")
                    concat_parts.append(ffmpeg.input(f"{idx}-{idz}.part.mp3"))
                split_files.append(str(f"{self.path}/{idx}-{idy}.part.mp3"))
                    # f.write("file " + f"'silence.mp3'" + "\n")
                concat_parts.append('silence.mp3')
                # concat_parts_length = sum([
                #     get_duration(post_audio_file)
                #     for post_audio_file in track(concat_parts, "Calculating the audio file durations...")
                # ])
                # ffmpeg_progress_run(
                ffmpeg.concat(*concat_parts).output(f"{self.path}/{idx}.mp3").overwrite_output().global_args('-y -hide_banner -loglevel panic -safe 0').run(quiet=True)
                #     concat_parts_length
                # )
                # os.system(
                #     "ffmpeg -f concat -y -hide_banner -loglevel panic -safe 0 "
                #     + "-i "
                #     + f"{self.path}/list.txt "
                #     + "-c copy "
                #     + f"{self.path}/{idx}.mp3"
                # )
        try:
            for i in range(0, len(split_files)):
                os.unlink(split_files[i])
        except FileNotFoundError as e:
            print("File not found: " + e.filename)
        except OSError:
            print("OSError")

    def call_tts(self, filename: str, text: str):
        mp3_filepath = f"{self.path}/{filename}.mp3"
        # mp3_duration = get_duration(mp3_filepath)
        audio_speed = settings.config["settings"]["tts"]["speed"]
        mp3_speed_changed_filepath = f"{self.path}/{filename}-speed-{audio_speed}.mp3"
        self.tts_module.run(
            text,
            filepath=mp3_filepath,
            random_voice=settings.config["settings"]["tts"]["random_voice"],
        )
        if audio_speed != 1:
            # ffmpeg_progress_run(
            ffmpeg.input(mp3_filepath).filter("atempo", audio_speed).output(mp3_speed_changed_filepath).overwrite_output().run(quiet=True)
                # mp3_duration*(1/audio_speed)
            # )
            os.replace(mp3_speed_changed_filepath, mp3_filepath)

        # try:
        #     self.length += MP3(mp3_filepath).info.length
        # except (MutagenError, HeaderNotFoundError):
        #     self.length += sox.file_info.duration(mp3_filepath)
        try:
            clip = AudioSegment.from_mp3(mp3_filepath)
            self.last_clip_length = clip.duration_seconds
            self.length += clip.duration_seconds
            # clip = AudioFileClip(mp3_filepath)
            # self.last_clip_length = clip.duration
            # self.length += clip.duration
            # clip.close()
            
        except:
            self.length = 0

    def create_silence_mp3(self):
        silence_duration = settings.config["settings"]["tts"]["silence_duration"]
        silence = AudioClip(
            make_frame=lambda t: np.sin(440 * 2 * np.pi * t),
            duration=silence_duration,
            fps=44100,
        )
        silence = volumex(silence, 0)
        silence.write_audiofile(f"{self.path}/silence.mp3", fps=44100, verbose=False, logger=None)


def process_text(text: str, clean: bool = True):
    lang = settings.config["reddit"]["thread"]["post_lang"]
    new_text = sanitize_text(text) if clean else text
    if lang:
        print_substep("Translating Text...")
        translated_text = translators.translate_text(text, translator="google", to_language=lang)
        new_text = sanitize_text(translated_text)
    return new_text
