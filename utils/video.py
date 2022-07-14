from __future__ import annotations

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
    def _create_watermark(text, fontsize, opacity=0.5):
        path = "./assets/temp/png/watermark.png"
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

    def add_watermark(self, text, opacity=0.5, duration: int | float = 5, position: Tuple = (1, 100), fontsize=15):
        img_clip = self._create_watermark(text, opacity=opacity, fontsize=fontsize)
        img_clip = img_clip.set_opacity(opacity).set_duration(duration)
        img_clip = img_clip.set_position(("center","bottom"))  # set position doesn't work for some reason # todo fix

        # Overlay the img clip on the first video clip
        self.video = CompositeVideoClip([self.video, img_clip])
        return self.video
