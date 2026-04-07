import json
import time

from utils import settings
from utils.console import print_step


def check_done(
    redditobj,
):
    # don't set this to be run anyplace that isn't subreddit.py bc of inspect stack
    """Checks if the chosen post has already been generated

    Args:
        redditobj: Reddit/Threads submission object

    Returns:
        The object if not done, None if already done
    """
    with open("./video_creation/data/videos.json", "r", encoding="utf-8") as done_vids_raw:
        done_videos = json.load(done_vids_raw)
    for video in done_videos:
        if video["id"] == str(redditobj):
            # Check both threads and reddit config for post_id
            post_id = ""
            if "threads" in settings.config and "thread" in settings.config["threads"]:
                post_id = settings.config["threads"]["thread"].get("post_id", "")
            if not post_id and "reddit" in settings.config and "thread" in settings.config["reddit"]:
                post_id = settings.config["reddit"]["thread"].get("post_id", "")
            if post_id:
                print_step(
                    "Video đã được tạo trước đó nhưng được chỉ định cụ thể trong config, tiếp tục..."
                )
                return redditobj
            print_step("Đang lấy bài viết mới vì bài này đã được tạo video")
            return None
    return redditobj


def save_data(subreddit: str, filename: str, reddit_title: str, reddit_id: str, credit: str):
    """Saves the videos that have already been generated to a JSON file in video_creation/data/videos.json

    Args:
        filename (str): The finished video title name
        @param subreddit:
        @param filename:
        @param reddit_id:
        @param reddit_title:
    """
    with open("./video_creation/data/videos.json", "r+", encoding="utf-8") as raw_vids:
        done_vids = json.load(raw_vids)
        if reddit_id in [video["id"] for video in done_vids]:
            return  # video already done but was specified to continue anyway in the config file
        payload = {
            "subreddit": subreddit,
            "id": reddit_id,
            "time": str(int(time.time())),
            "background_credit": credit,
            "reddit_title": reddit_title,
            "filename": filename,
        }
        done_vids.append(payload)
        raw_vids.seek(0)
        json.dump(done_vids, raw_vids, ensure_ascii=False, indent=4)
