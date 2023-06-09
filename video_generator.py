import os, shutil
from moviepy.editor import concatenate_videoclips, VideoFileClip
from main import run

# This class must be run from the top level, not from inside the containing directory

class VideoGenerator():
    def __init__(self, config):
        self.config = config
    
    def _concatenate_videos(self, video_paths, output_path):
        video_clips = []
        
        for path in video_paths:
            video_clip = VideoFileClip(path)
            video_clips.append(video_clip)
            
        final_clip = concatenate_videoclips(video_clips)
        final_clip.write_videofile(output_path, codec="libx264", fps=24)
    
    def generate_shorts(self, num_of_shorts, remove_past_results=True):
        if remove_past_results:
            if os.path.exists("results"):
                shutil.rmtree("results")

        for _ in range(num_of_shorts):
            print("="*50)
            run(self.config)
        
        print(f"Videos have been made!")
    
    def generate_long_video(self, num_of_videos_to_be_conc, remove_past_results=True):
        if remove_past_results:
            if os.path.exists("results"):
                shutil.rmtree("results")
            
            if os.path.exists("long_form_videos_results"):
                shutil.rmtree("long_form_videos_results")

        for _ in range(num_of_videos_to_be_conc):
            print("="*50)
            run(self.config)
        
        print("Concatinating videos...")
        videos = []
        subreddit = self.config["reddit"]["thread"]["subreddit"]
        videos_folder = f"results/{subreddit}"
        for video in os.listdir(videos_folder):
            videos.append(os.path.join(videos_folder, video))
        
        if not os.path.exists("long_form_videos_results"):
            os.mkdir("long_form_videos_results")

        output_filename = f"long_form_videos_results{videos[0].split('/')[-1].split('.')[0]} + other threads from {subreddit}!.mp4"
        self._concatenate_videos(videos, output_filename)

        print("Done!")