from gtts import gTTS
from pathlib import Path
from mutagen.mp3 import MP3
from utils.console import print_step, print_substep
from rich.progress import track

CURRENT_MAX_COMMENTS_IN_FINAL_VIDEO = 50

def save_text_to_mp3(reddit_obj):
    """Saves Text to MP3 files.

    Args:
        reddit_obj : The reddit object you received from the reddit API in the askreddit.py file.
    """
    print_step("Saving Text to MP3 files...")
    create_folder_for_mp3_files()

    
    length = create_mp3_file_from_text(comment=reddit_obj["thread_title"], path="assets/mp3/title.mp3")

    for idx, comment in track(enumerate(reddit_obj["comments"]), description="Saving..."):
        # ! Stop creating mp3 files if the length is greater than 50 seconds. This can be longer, but this is just a good starting point
        if length > CURRENT_MAX_COMMENTS_IN_FINAL_VIDEO:
            break
        
        length += create_mp3_file_from_text(comment=comment["comment_body"], path=f"assets/mp3/{idx}.mp3")
    print_substep("Saved Text to MP3 files successfully.", style="bold green")
    # ! Return the index so we know how many screenshots of comments we need to make.
    return length, idx

def create_folder_for_mp3_files():
    Path("assets/mp3").mkdir(parents=True, exist_ok=True)
    
def create_mp3_file_from_text(**file_props):
    comment_text, file_path_to_save = file_props.pop("comment"), file_props.pop("path")
    if not comment_text or not file_path_to_save:
        raise ValueError("you must send object with structure of: { comment: str, path: str }")
    # fileProps structure : { 'dynamic {text to parse for speech}': 'dynamic {path to save}'  }
    tts = gTTS(text=comment_text, lang="en", slow=False)
    tts.save(file_path_to_save) 
    return MP3(file_path_to_save).info.length