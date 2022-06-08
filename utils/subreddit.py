from typings import List
def get_hottest_undone(submissions: List):
    """
    recursively checks if the top submission in the list was already done.
    """
    with open("./video_creation/data/videos.json", "r") as done_vids_raw:
        done_videos = json.load(done_vids_raw)
    for submission in submissions:
        if already_done(done_videos, submission):
            continue
        return submission
    return get_subreddit_undone(subreddit.top(time_filter="hour")) # all of the videos in hot have already been done

def already_done(done_videos: list, submission):

    for video in done_videos:
        if video["id"] == str(submission):
            return True
    return False
