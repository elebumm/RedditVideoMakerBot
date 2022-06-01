from utils.cleanup import cleanup
from utils.console import print_markdown
import time
from reddit.subreddit import get_subreddit_threads
from video_creation.background import download_background, chop_background_video
from video_creation.voices import save_text_to_mp3
from video_creation.screenshot_downloader import download_screenshots_of_reddit_posts
from video_creation.final_video import make_final_video

print_markdown(
    "### Thanks for using this tool! 😊 [Feel free to contribute to this project on GitHub!](https://lewismenelaws.com). If you have any questions, feel free to reach out to me on Twitter or submit a GitHub issue."
)

time.sleep(2)


def main():
    cleanup()

    def get_obj():
        reddit_obj = get_subreddit_threads()
        for comment in (reddit_obj["comments"]):
            if len(comment) > 250:
                print(comment)
                reddit_obj["comments"].remove(comment)
                print(reddit_obj["comments"])
        return reddit_obj

    reddit_object = get_obj()
    length, number_of_comments = save_text_to_mp3(reddit_object)
    download_screenshots_of_reddit_posts(reddit_object, number_of_comments)
    download_background()
    chop_background_video(length)
    final_video = make_final_video(number_of_comments)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print_markdown("## Clearing temp files")
        cleanup()
        exit()
