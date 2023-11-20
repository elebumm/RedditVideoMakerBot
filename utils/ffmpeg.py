import ffmpeg
from pydub import AudioSegment
from tqdm import tqdm

from utils.ffmpeg_progress import ProgressFfmpeg

def get_duration(filename):
    if filename.lower().endswith('.mp3'):
        return float(AudioSegment.from_mp3(filename).duration_seconds)
    probe_info=ffmpeg.probe(filename)
    return float(probe_info["format"]["duration"])

def ffmpeg_progress_run(ffmpeg_cmd, length):
    pbar = tqdm(total=100, desc="Progress: ", bar_format="{l_bar}{bar}", unit=" %", dynamic_ncols=True, leave=False)
    def progress_tracker(progress) -> None:
        status = round(progress * 100, 2)
        old_percentage = pbar.n
        pbar.update(status - old_percentage)
    with ProgressFfmpeg(length, progress_tracker) as progress:
        ffmpeg_cmd.global_args("-progress", progress.output_file.name).run(
            quiet=True,
            overwrite_output=True,
            capture_stdout=False,
            capture_stderr=False,
        )
    old_percentage = pbar.n
    pbar.update(100 - old_percentage)
    pbar.close()