#!/usr/bin/env python
"""
Threads Video Maker Bot - Tạo video tự động từ Threads (Meta) cho thị trường Việt Nam.

Hỗ trợ:
- Lấy nội dung từ Threads (Meta) thay vì Reddit
- TTS tiếng Việt (Google Translate, OpenAI, v.v.)
- Tự động upload lên TikTok, YouTube, Facebook
- Lên lịch tạo video tự động

Modes:
- manual: Tạo video thủ công (mặc định)
- auto: Tạo video và tự động upload
- scheduled: Lên lịch tạo video tự động

Usage:
    python main.py                  # Chế độ manual
    python main.py --mode auto      # Tạo + upload
    python main.py --mode scheduled # Lên lịch tự động
    python main.py --reddit         # Legacy Reddit mode
"""

import math
import sys
from os import name
from pathlib import Path
from subprocess import Popen
from typing import Dict, NoReturn

from utils import settings
from utils.cleanup import cleanup
from utils.console import print_markdown, print_step, print_substep
from utils.ffmpeg_install import ffmpeg_install
from utils.id import extract_id

__VERSION__ = "4.0.0"

print("""
████████╗██╗  ██╗██████╗ ███████╗ █████╗ ██████╗ ███████╗    ██╗   ██╗██╗██████╗ ███████╗ ██████╗
╚══██╔══╝██║  ██║██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔════╝    ██║   ██║██║██╔══██╗██╔════╝██╔═══██╗
   ██║   ███████║██████╔╝█████╗  ███████║██║  ██║███████╗    ██║   ██║██║██║  ██║█████╗  ██║   ██║
   ██║   ██╔══██║██╔══██╗██╔══╝  ██╔══██║██║  ██║╚════██║    ╚██╗ ██╔╝██║██║  ██║██╔══╝  ██║   ██║
   ██║   ██║  ██║██║  ██║███████╗██║  ██║██████╔╝███████║     ╚████╔╝ ██║██████╔╝███████╗╚██████╔╝
   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝ ╚══════╝      ╚═══╝  ╚═╝╚═════╝ ╚══════╝ ╚═════╝

   ███╗   ███╗ █████╗ ██╗  ██╗███████╗██████╗     🇻🇳  VIETNAM EDITION
   ████╗ ████║██╔══██╗██║ ██╔╝██╔════╝██╔══██╗
   ██╔████╔██║███████║█████╔╝ █████╗  ██████╔╝    Powered by Threads (Meta)
   ██║╚██╔╝██║██╔══██║██╔═██╗ ██╔══╝  ██╔══██╗    Auto-post: TikTok | YouTube | Facebook
   ██║ ╚═╝ ██║██║  ██║██║  ██╗███████╗██║  ██║
   ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
""")
print_markdown(
    "### 🇻🇳 Threads Video Maker Bot - Phiên bản Việt Nam\n"
    "Tạo video tự động từ nội dung Threads và đăng lên TikTok, YouTube, Facebook.\n"
    "Tài liệu: https://github.com/thaitien280401-stack/RedditVideoMakerBot"
)

thread_id: str
thread_object: Dict[str, str | list]


def main_threads(POST_ID=None) -> None:
    """Pipeline chính: Lấy nội dung từ Threads → Tạo video."""
    global thread_id, thread_object

    from threads.threads_client import get_threads_posts
    from video_creation.background import (
        chop_background,
        download_background_audio,
        download_background_video,
        get_background_config,
    )
    from video_creation.final_video import make_final_video
    from video_creation.threads_screenshot import get_screenshots_of_threads_posts
    from video_creation.voices import save_text_to_mp3

    thread_object = get_threads_posts(POST_ID)
    thread_id = extract_id(thread_object)
    print_substep(f"Thread ID: {thread_id}", style="bold blue")

    length, number_of_comments = save_text_to_mp3(thread_object)
    length = math.ceil(length)

    get_screenshots_of_threads_posts(thread_object, number_of_comments)

    bg_config = {
        "video": get_background_config("video"),
        "audio": get_background_config("audio"),
    }
    download_background_video(bg_config["video"])
    download_background_audio(bg_config["audio"])
    chop_background(bg_config, length, thread_object)
    make_final_video(number_of_comments, length, thread_object, bg_config)

    # Lưu title vào lịch sử để tránh tạo trùng lặp
    from utils.title_history import save_title

    title = thread_object.get("thread_title", "")
    tid = thread_object.get("thread_id", "")
    if title:
        save_title(title=title, thread_id=tid, source="threads")


def main_threads_with_upload(POST_ID=None) -> None:
    """Pipeline đầy đủ: Threads → Video → Upload lên các platform."""
    from scheduler.pipeline import run_pipeline

    run_pipeline(POST_ID)


def main_reddit(POST_ID=None) -> None:
    """Legacy mode: Sử dụng Reddit làm nguồn nội dung."""
    from reddit.subreddit import get_subreddit_threads
    from video_creation.background import (
        chop_background,
        download_background_audio,
        download_background_video,
        get_background_config,
    )
    from video_creation.final_video import make_final_video
    from video_creation.screenshot_downloader import get_screenshots_of_reddit_posts
    from video_creation.voices import save_text_to_mp3

    global thread_id, thread_object
    thread_object = get_subreddit_threads(POST_ID)
    thread_id = extract_id(thread_object)
    print_substep(f"Thread ID: {thread_id}", style="bold blue")
    length, number_of_comments = save_text_to_mp3(thread_object)
    length = math.ceil(length)
    get_screenshots_of_reddit_posts(thread_object, number_of_comments)
    bg_config = {
        "video": get_background_config("video"),
        "audio": get_background_config("audio"),
    }
    download_background_video(bg_config["video"])
    download_background_audio(bg_config["audio"])
    chop_background(bg_config, length, thread_object)
    make_final_video(number_of_comments, length, thread_object, bg_config)


def run_many(times, use_reddit=False) -> None:
    """Chạy nhiều lần tạo video."""
    main_func = main_reddit if use_reddit else main_threads
    for x in range(1, times + 1):
        print_step(f"Đang tạo video {x}/{times}...")
        main_func()
        Popen("cls" if name == "nt" else "clear", shell=True).wait()


def shutdown() -> NoReturn:
    if "thread_id" in globals():
        print_markdown("## Đang dọn dẹp file tạm...")
        cleanup(thread_id)

    print("Thoát...")
    sys.exit()


def parse_args():
    """Parse command line arguments."""
    import argparse

    parser = argparse.ArgumentParser(description="Threads Video Maker Bot - Vietnam Edition")
    parser.add_argument(
        "--mode",
        choices=["manual", "auto", "scheduled"],
        default="manual",
        help="Chế độ chạy: manual (mặc định), auto (tạo + upload), scheduled (lên lịch)",
    )
    parser.add_argument(
        "--reddit",
        action="store_true",
        help="Sử dụng Reddit thay vì Threads (legacy mode)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    if sys.version_info.major != 3 or sys.version_info.minor not in [10, 11, 12]:
        print("Ứng dụng yêu cầu Python 3.10, 3.11 hoặc 3.12. Vui lòng cài đặt phiên bản phù hợp.")
        sys.exit()

    args = parse_args()
    ffmpeg_install()
    directory = Path().absolute()
    config = settings.check_toml(
        f"{directory}/utils/.config.template.toml", f"{directory}/config.toml"
    )
    config is False and sys.exit()

    # Kiểm tra TikTok TTS session
    if (not settings.config["settings"]["tts"].get("tiktok_sessionid", "")) and config["settings"][
        "tts"
    ]["voice_choice"] == "tiktok":
        print_substep(
            "TikTok TTS cần sessionid! Xem tài liệu để biết cách lấy.",
            "bold red",
        )
        sys.exit()

    try:
        if args.mode == "scheduled":
            # Chế độ lên lịch tự động
            print_step("🕐 Khởi động chế độ lên lịch tự động...")
            from scheduler.pipeline import run_scheduled

            run_scheduled()

        elif args.mode == "auto":
            # Chế độ tự động: tạo + upload
            print_step("🚀 Khởi động chế độ tự động (tạo + upload)...")
            if args.reddit:
                # Legacy Reddit mode
                main_reddit()
            else:
                thread_config = config.get("threads", {}).get("thread", {})
                post_id = thread_config.get("post_id", "")
                if post_id:
                    for index, pid in enumerate(post_id.split("+")):
                        index += 1
                        print_step(f"Đang xử lý thread {index}/{len(post_id.split('+'))}...")
                        main_threads_with_upload(pid)
                        Popen("cls" if name == "nt" else "clear", shell=True).wait()
                elif config["settings"]["times_to_run"]:
                    for i in range(config["settings"]["times_to_run"]):
                        print_step(f"Đang tạo video {i + 1}/{config['settings']['times_to_run']}...")
                        main_threads_with_upload()
                else:
                    main_threads_with_upload()

        else:
            # Chế độ manual (mặc định)
            if args.reddit:
                # Legacy Reddit mode
                from prawcore import ResponseException

                try:
                    if config["reddit"]["thread"]["post_id"]:
                        for index, post_id in enumerate(
                            config["reddit"]["thread"]["post_id"].split("+")
                        ):
                            index += 1
                            print_step(f"Đang xử lý post {index}...")
                            main_reddit(post_id)
                            Popen("cls" if name == "nt" else "clear", shell=True).wait()
                    elif config["settings"]["times_to_run"]:
                        run_many(config["settings"]["times_to_run"], use_reddit=True)
                    else:
                        main_reddit()
                except ResponseException:
                    print_markdown("## Thông tin đăng nhập Reddit không hợp lệ")
                    print_markdown("Vui lòng kiểm tra config.toml")
                    shutdown()
            else:
                # Threads mode (mặc định)
                thread_config = config.get("threads", {}).get("thread", {})
                post_id = thread_config.get("post_id", "")
                if post_id:
                    for index, pid in enumerate(post_id.split("+")):
                        index += 1
                        print_step(f"Đang xử lý thread {index}/{len(post_id.split('+'))}...")
                        main_threads(pid)
                        Popen("cls" if name == "nt" else "clear", shell=True).wait()
                elif config["settings"]["times_to_run"]:
                    run_many(config["settings"]["times_to_run"])
                else:
                    main_threads()

    except KeyboardInterrupt:
        shutdown()
    except Exception as err:
        # Redact sensitive values
        try:
            config["settings"]["tts"]["tiktok_sessionid"] = "REDACTED"
            config["settings"]["tts"]["elevenlabs_api_key"] = "REDACTED"
            config["settings"]["tts"]["openai_api_key"] = "REDACTED"
            if "threads" in config and "creds" in config["threads"]:
                config["threads"]["creds"]["access_token"] = "REDACTED"
            if "uploaders" in config:
                for platform in config["uploaders"]:
                    for key in ["access_token", "client_secret", "refresh_token"]:
                        if key in config["uploaders"][platform]:
                            config["uploaders"][platform][key] = "REDACTED"
        except (KeyError, TypeError):
            pass

        print_step(
            f"Đã xảy ra lỗi! Vui lòng thử lại hoặc báo lỗi trên GitHub.\n"
            f"Phiên bản: {__VERSION__}\n"
            f"Lỗi: {err}\n"
            f'Config: {config.get("settings", {})}'
        )
        raise err
