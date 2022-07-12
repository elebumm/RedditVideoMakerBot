from __future__ import annotations

from moviepy.video.VideoClip import VideoClip, ImageClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

class Video:
    def __init__(self, video: VideoClip | VideoFileClip, *args, **kwargs):
        self.video: VideoClip = video
        self.fps = self.video.fps
        self.duration = self.video.duration

    @staticmethod
    def _create_watermark(text, path, fontsize=15, opacity=0.5):

        width = 500
        height = 200

        white = (255, 255, 255)
        transparent = (0, 0, 0, 0)

        font = ImageFont.load_default()
        wm = Image.new('RGBA', (width, height), transparent)
        im = Image.new('RGBA', (width, height), transparent)  # Change this line too.

        draw = ImageDraw.Draw(wm)
        w, h = draw.textsize(text, font)
        draw.text(((width - w) / 2, (height - h) / 2), text, white, font)
        en = ImageEnhance.Brightness(wm) # todo alow it to use the fontsize
        mask = en.enhance(1 - opacity)
        im.paste(wm, (25, 25), mask)
        im.save(path)

    def add_watermark(self, text, opacity=0.5):
        # add a watermark to the video clip with the given text and opacity without importing a new library
        from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
        from moviepy.video.compositing.concatenate import concatenate_videoclips
        path = './assets/temp/png/watermark.png'
        self._create_watermark(text, path, opacity=opacity)
        image_clips = []
        image_clips.insert(
            0,
            ImageClip(path)
            .set_duration(self.video.duration)
            #.resize(width=W - 100)
        )
        image_concat = concatenate_videoclips(image_clips).set_position((0.1, 0.1))
        self.video = CompositeVideoClip([self.video, image_concat])
        return self.video




if __name__ == '__main__': # todo delete
    Video._create_watermark('Background Video by Jason(example)', '../assets/temp/png/watermark.png')
