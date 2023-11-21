import ffmpeg
from pydub import AudioSegment
from moviepy.editor import VideoFileClip, AudioFileClip
# from tqdm import tqdm
from rich.progress import Progress

from utils.ffmpeg_progress import ProgressFfmpeg

def get_duration(filename):
    ffmpeg_cmd = ffmpeg.input(filename).output('/dev/null', f="null", progress='/dev/stdout')
    ffmpeg_stdout, ffmpeg_stderr = ffmpeg_cmd.run(capture_stdout=True, capture_stderr=True)
    stdout=ffmpeg_stdout.decode('UTF-8')
    stdout_lines=stdout.splitlines()
    for line in stdout_lines:
        if "out_time_ms" in line:
            out_time_ms_str = line.split("=")[1].strip()
            if out_time_ms_str.isnumeric():
                return float(out_time_ms_str) / 1000000.0
    stderr=ffmpeg_stderr.decode('UTF-8')
    stderr_lines=stderr.splitlines()
    stream_durations=[]
    for line in stderr_lines:
        if "Duration:" in line:
            timestamp = line.split("Duration:")[1].strip().split(',')[0].strip()
            h, m, s_ms = timestamp.split(':')
            s, ms = s_ms.split('.')
            stream_durations.append(int(h) * 3600 + int(m) * 60 + int(s) + float(f".{ms}"))
    if len(stream_durations) > 0:
        return max(stream_durations)
    if filename.lower().endswith('.mp3'):
        try:
            return float(AudioSegment.from_mp3(filename).duration_seconds)
        except:
            pass
        try:
            return float(AudioFileClip(filename).duration)
        except:
            pass
    if filename.lower().endswith('.mp4'):
        try:
            return float(VideoFileClip(filename).duration)
        except:
            pass
    probe_info=ffmpeg.probe(filename)
    return float(probe_info["format"]["duration"])

def ffmpeg_progress_run(ffmpeg_cmd, length):
    with Progress() as progress_bar:
        # pbar = tqdm(total=100, desc="Progress: ", bar_format="{l_bar}{bar}", unit=" %", dynamic_ncols=True, leave=False)
        task = progress_bar.add_task("Rendering...", total=100)
        def progress_tracker(progress) -> None:
            new_progress=progress*100
            if new_progress >= progress_bar._tasks[task].completed:
                progress_bar.update(task, completed=new_progress)
            # status = round(progress * 100, 2)
            # old_percentage = pbar.n
            # pbar.update(status - old_percentage)
        with ProgressFfmpeg(length, progress_tracker) as progress:
            progress_bar.start_task(task)
            ffmpeg_cmd.global_args("-progress", progress.output_file.name).run(
                quiet=True,
                overwrite_output=True,
                capture_stdout=False,
                capture_stderr=False,
            )
        # old_percentage = pbar.n
        # pbar.update(100 - old_percentage)
        # pbar.close()
        progress_bar.update(task, completed=100)