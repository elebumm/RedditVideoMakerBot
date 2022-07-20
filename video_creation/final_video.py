#!/usr/bin/env python3
import multiprocessing
import os
import re
from os.path import exists
from typing import Tuple, Any, Union

from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    ImageClip,
    CompositeAudioClip,
    CompositeVideoClip,
)
from rich.console import Console
from rich.progress import track
from attr import attrs

from utils.cleanup import cleanup
from utils.console import print_step, print_substep
from utils.video import Video
from utils.videos import save_data
from utils import settings
from video_creation.background import download_background, chop_background_video


@attrs
class FinalVideo:
    video_duration: int = 0
    console = Console()

    def __attrs_post_init__(self):
        self.W: int = int(settings.config["settings"]["video_width"])
        self.H: int = int(settings.config["settings"]["video_height"])

        if not self.W or not self.H:
            self.W, self.H = 1080, 1920

        self.vertical_video: bool = self.W < self.H

        self.max_length: int = int(settings.config["settings"]["video_length"])
        self.time_before_first_picture: float = settings.config["settings"]["time_before_first_picture"]
        self.time_before_tts: float = settings.config["settings"]["time_before_tts"]
        self.time_between_pictures: float = settings.config["settings"]["time_between_pictures"]
        self.delay_before_end: float = settings.config["settings"]["delay_before_end"]

        self.opacity = settings.config["settings"]["opacity"]
        self.opacity = 1 if self.opacity is None or self.opacity >= 1 else self.opacity
        self.transition = settings.config["settings"]["transition"]
        self.transition = 0 if self.transition is None or self.transition > 2 else self.transition

    @staticmethod
    def name_normalize(
            name: str
    ) -> str:
        name = re.sub(r'[?\\"%*:|<>]', "", name)
        name = re.sub(r"( [w,W]\s?/\s?[oO0])", r" without", name)
        name = re.sub(r"( [w,W]\s?/)", r" with", name)
        name = re.sub(r"(\d+)\s?/\s?(\d+)", r"\1 of \2", name)
        name = re.sub(r"(\w+)\s?/\s?(\w+)", r"\1 or \2", name)
        name = re.sub(r"/", "", name)

        lang = settings.config["reddit"]["thread"]["post_lang"]
        translated_name = None
        if lang:
            import translators as ts

            print_substep("Translating filename...")
            translated_name = ts.google(name, to_language=lang)
        return translated_name[:30] if translated_name else name[:30]

    @staticmethod
    def create_audio_clip(
            clip_title: Union[str, int],
            clip_start: float,
    ) -> AudioFileClip:
        return (
            AudioFileClip(f"assets/temp/mp3/{clip_title}.mp3")
            .set_start(clip_start)
        )

    def create_image_clip(
            self,
            image_title: Union[str, int],
            audio_start: float,
            audio_duration: float,
            clip_position: str,
    ) -> ImageClip:
        return (
            ImageClip(f"assets/temp/png/{image_title}.png")
            .set_start(audio_start - self.time_before_tts)
            .set_duration(self.time_before_tts * 2 + audio_duration)
            .set_opacity(self.opacity)
            .set_position(clip_position)
            .resize(
                width=self.W - self.W / 20 if self.vertical_video else None,
                height=self.H - self.H / 5 if not self.vertical_video else None,
                )
            .crossfadein(self.transition)
            .crossfadeout(self.transition)
        )

    def make(
            self,
            indexes_of_clips: list,
            reddit_obj: dict,
            background_config: Tuple[str, str, str, Any],
    ) -> None:
        """Gathers audio clips, gathers all screenshots, stitches them together and saves the final video to assets/temp
        Args:
            indexes_of_clips (list): Indexes of voiced comments
            reddit_obj (dict): The reddit object that contains the posts to read.
            background_config (Tuple[str, str, str, Any]): The background config to use.
        """
        # try:  # if it isn't found (i.e you just updated and copied over config.toml) it will throw an error
        #    VOLUME_MULTIPLIER = settings.config["settings"]['background']["background_audio_volume"]
        # except (TypeError, KeyError):
        #    print('No background audio volume found in config.toml. Using default value of 1.')
        #    VOLUME_MULTIPLIER = 1
        print_step("Creating the final video 🎥")
        VideoFileClip.reW = lambda clip: clip.resize(width=self.W)
        VideoFileClip.reH = lambda clip: clip.resize(width=self.H)

        # Gather all audio clips
        audio_clips = list()
        correct_audio_offset = self.time_before_tts * 2 + self.time_between_pictures

        audio_title = self.create_audio_clip(
            "title",
            self.time_before_first_picture + self.time_before_tts,
        )
        self.video_duration += audio_title.duration + self.time_before_first_picture + self.time_before_tts
        audio_clips.append(audio_title)
        indexes_for_videos = list()

        for audio_title in track(
                indexes_of_clips,
                description="Gathering audio clips...",
                total=indexes_of_clips.__len__()
        ):
            temp_audio_clip = self.create_audio_clip(
                audio_title,
                correct_audio_offset + self.video_duration,
            )
            if self.video_duration + temp_audio_clip.duration + \
                    correct_audio_offset + self.delay_before_end <= self.max_length:
                self.video_duration += temp_audio_clip.duration + correct_audio_offset
                audio_clips.append(temp_audio_clip)
                indexes_for_videos.append(audio_title)

        self.video_duration += self.delay_before_end + self.time_before_tts

        # Can't use concatenate_audioclips here, it resets clips' start point
        audio_composite = CompositeAudioClip(audio_clips)

        self.console.log("[bold green] Video Will Be: %.2f Seconds Long" % self.video_duration)

        # Gather all images
        image_clips = list()

        # Accounting for title and other stuff if audio_clips
        index_offset = 1

        image_clips.append(
            self.create_image_clip(
                "title",
                audio_clips[0].start,
                audio_clips[0].duration,
                background_config[3],
            )
        )

        for idx, photo_idx in track(
                enumerate(
                    indexes_for_videos,
                    start=index_offset,
                ),
                description="Gathering audio clips...",
                total=indexes_for_videos.__len__()
        ):
            image_clips.append(
                self.create_image_clip(
                    f"comment_{photo_idx}",
                    audio_clips[idx].start,
                    audio_clips[idx].duration,
                    background_config[3],
                )
            )

        # if os.path.exists("assets/mp3/posttext.mp3"):
        #    image_clips.insert(
        #        0,
        #        ImageClip("assets/png/title.png")
        #        .set_duration(audio_clips[0].duration + audio_clips[1].duration)
        #        .set_position("center")
        #        .resize(width=W - 100)
        #        .set_opacity(float(opacity)),
        #    )
        # else: story mode stuff

        # Can't use concatenate_videoclips here, it resets clips' start point

        download_background(background_config)
        chop_background_video(background_config, self.video_duration)
        background_clip = (
            VideoFileClip("assets/temp/background.mp4")
            .set_start(0)
            .set_end(self.video_duration)
            .without_audio()
            .resize(height=self.H)
        )

        back_video_width, back_video_height = background_clip.size

        # Fix for crop with vertical videos
        if back_video_width < self.H:
            background_clip = (
                background_clip
                .resize(width=self.W)
            )
            back_video_width, back_video_height = background_clip.size
            background_clip = background_clip.crop(
                x1=0,
                x2=back_video_width,
                y1=back_video_height / 2 - self.H / 2,
                y2=back_video_height / 2 + self.H / 2
            )
        else:
            background_clip = background_clip.crop(
                x1=back_video_width / 2 - self.W / 2,
                x2=back_video_width / 2 + self.W / 2,
                y1=0,
                y2=back_video_height
            )

        final = CompositeVideoClip([background_clip, *image_clips])
        final.audio = audio_composite

        title = re.sub(r"[^\w\s-]", "", reddit_obj["thread_title"])
        idx = re.sub(r"[^\w\s-]", "", reddit_obj["thread_id"])

        filename = f"{self.name_normalize(title)}.mp4"
        subreddit = str(settings.config["reddit"]["thread"]["subreddit"])

        if not exists(f"./results/{subreddit}"):
            print_substep("The results folder didn't exist so I made it")
            os.makedirs(f"./results/{subreddit}")

        # if (
        #         settings.config["settings"]['background']["background_audio"] and
        #         exists(f"assets/backgrounds/background.mp3")
        # ):
        #     audioclip = (
        #         AudioFileClip(f"assets/backgrounds/background.mp3")
        #         .set_duration(final.duration)
        #         .volumex(0.2)
        #     )
        #     final_audio = CompositeAudioClip([final.audio, audioclip])
        #     # lowered_audio = audio_background.multiply_volume(  # TODO get this to work
        #     #    VOLUME_MULTIPLIER)  # lower volume by background_audio_volume, use with fx
        #     final.set_audio(final_audio)

        final = Video(final).add_watermark(
            text=f"Background credit: {background_config[2]}", opacity=0.4
        )

        final.write_videofile(
            "assets/temp/temp.mp4",
            fps=30,
            audio_codec="aac",
            audio_bitrate="192k",
            verbose=False,
            threads=multiprocessing.cpu_count(),
        )
        # Moves file in subreddit folder and renames it
        os.rename(
            "assets/temp/temp.mp4",
            f"results/{subreddit}/{filename}",
        )
        save_data(subreddit, filename, title, idx, background_config[2])
        print_step("Removing temporary files 🗑")
        cleanups = cleanup()
        print_substep(f"Removed {cleanups} temporary files 🗑")
        print_substep("See result in the results folder!")

        print_step(
            f'Reddit title: {reddit_obj["thread_title"]} \n Background Credit: {background_config[2]}'
        )
