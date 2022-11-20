from __future__ import annotations

import re
from typing import Tuple

from PIL import ImageFont, Image, ImageDraw, ImageEnhance
from moviepy.video.VideoClip import VideoClip, ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip


class Video:
    def __init__(self, video: VideoClip, *args, **kwargs):
        self.video: VideoClip = video
        self.fps = self.video.fps
        self.duration = self.video.duration

    @staticmethod
    def _create_watermark(text, redditid, fontsize, opacity=0.5):
        id = re.sub(r"[^\w\s-]", "", redditid["thread_id"])
        path = f"./assets/temp/{id}/png/watermark.png"
        width = int(fontsize * len(text))
        height = int(fontsize * len(text) / 2)
        white = (255, 255, 255)
        transparent = (0, 0, 0, 0)

        font = ImageFont.load_default()
        wm = Image.new("RGBA", (width, height), transparent)
        im = Image.new("RGBA", (width, height), transparent)  # Change this line too.

        draw = ImageDraw.Draw(wm)
        w, h = draw.textsize(text, font)
        draw.text(((width - w) / 2, (height - h) / 2), text, white, font)
        en = ImageEnhance.Brightness(wm)  # todo allow it to use the fontsize
        mask = en.enhance(1 - opacity)
        im.paste(wm, (25, 25), mask)
        im.save(path)
        return ImageClip(path)

    def add_watermark(
        self,
        text,
        redditid,
        opacity=0.5,
        duration: int | float = 5,
        position: Tuple = (0.7, 0.9),
        fontsize=15,
    ):
        compensation = round(
            (
                position[0]
                / ((len(text) * (fontsize / 5) / 1.5) / 100 + position[0] * position[0])
            ),
            ndigits=2,
        )
        position = (compensation, position[1])
        # print(f'{compensation=}')
        # print(f'{position=}')
        img_clip = self._create_watermark(
            text, redditid, fontsize=fontsize, opacity=opacity
        )
        img_clip = img_clip.set_opacity(opacity).set_duration(duration)
        img_clip = img_clip.set_position(
            position, relative=True
        )  # todo get dara from utils/CONSTANTS.py and adapt position accordingly

        # Overlay the img clip on the first video clip
        self.video = CompositeVideoClip([self.video, img_clip])
        return self.video
