from __future__ import annotations

from typing import Tuple

from moviepy.video.VideoClip import VideoClip, TextClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip


class Video:
    def __init__(self, video: VideoClip | VideoFileClip, *args, **kwargs):
        self.video: VideoClip = video
        self.fps = self.video.fps
        self.duration = self.video.duration

    @staticmethod
    def _create_watermark(text, fontsize, opacity=0.5):
        txt_clip = TextClip(text, fontsize=fontsize, color='black').set_opacity(opacity)
        return txt_clip

    def add_watermark(self, text, opacity=0.5, position: Tuple = (0.95, 0.95), fontsize=15):
        txt_clip = self._create_watermark(text, opacity=opacity, fontsize=fontsize)
        txt_clip = txt_clip.set_pos(position).set_duration(10)

        # Overlay the text clip on the first video clip
        self.video = CompositeVideoClip([self.video, txt_clip])
        return self.video
