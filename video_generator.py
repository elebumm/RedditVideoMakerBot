import os, shutil
import ffmpeg
from utils.console import print_markdown
from main import run

class VideoGenerator():
    def __init__(self, config):
        self.config = config
    
    def _concatenate_videos(self, video_list, output_file):
        concat_file = 'concat.txt'

        # Create a temporary file containing the list of videos
        with open(concat_file, 'w') as file:
            for video in video_list:
                file.write(f"file '{video}'\n")

        # Run ffmpeg to concatenate the videos
        ffmpeg.input(concat_file, format='concat', safe=0).output(output_file, c='copy').run()

        # Clean up temporary file
        os.remove(concat_file)
    
    def generate_shorts(self, num_of_shorts, remove_past_results=True):
        if remove_past_results:
            if os.path.exists("results"):
                shutil.rmtree("results")

        for i in range(num_of_shorts):
            print_markdown(f"# Iteration {i+1}")
            run(self.config)
        
        print(f"Videos have been made!")
    
    def generate_long_video(self, num_of_videos_to_be_conc, remove_past_results=True):
        if remove_past_results:            
            if os.path.exists("long_form_videos_results"):
                shutil.rmtree("long_form_videos_results")

        subreddit = self.config["reddit"]["thread"]["subreddit"]
        videos_folder = f"results/{subreddit}"
        videos_to_be_conc = []
        for i in range(num_of_videos_to_be_conc):
            print_markdown(f"# Iteration {i+1}")
            run(self.config)
            videos_to_be_conc.append(os.listdir(videos_folder)[-1])
        
        print_markdown("# Concatinating videos...")
        videos = []
        for video in videos_to_be_conc:
            videos.append(os.path.join(videos_folder, video))
        
        if not os.path.exists("long_form_videos_results"):
            os.mkdir("long_form_videos_results")

        output_filename = f"long_form_videos_results/{videos[0].split('/')[-1].split('.')[0]} + other threads from {subreddit}!.mp4"
        self._concatenate_videos(videos, output_filename)

        print("Done!")