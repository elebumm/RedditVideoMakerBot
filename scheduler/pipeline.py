"""
Scheduler - Hệ thống lên lịch tự động tạo và đăng video.

Sử dụng APScheduler để lên lịch các tác vụ tự động.
"""

import math
import os
import sys
from datetime import datetime
from os import name
from pathlib import Path
from subprocess import Popen
from typing import Optional

from utils import settings
from utils.cleanup import cleanup
from utils.console import print_markdown, print_step, print_substep
from utils.id import extract_id
from utils.title_history import save_title


def run_pipeline(post_id: Optional[str] = None) -> Optional[str]:
    """Chạy toàn bộ pipeline tạo video từ Threads.

    Pipeline:
    1. Lấy nội dung từ Threads
    2. Tạo TTS audio
    3. Tạo screenshots
    4. Tải background video/audio
    5. Ghép video cuối cùng
    6. Upload lên các platform (nếu được cấu hình)

    Args:
        post_id: ID cụ thể của thread (optional).

    Returns:
        Đường dẫn file video đã tạo, hoặc None nếu thất bại.
    """
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

    print_step("🚀 Bắt đầu pipeline tạo video...")

    try:
        # Step 1: Lấy nội dung từ Threads
        print_step("📱 Bước 1: Lấy nội dung từ Threads...")
        thread_object = get_threads_posts(post_id)
        thread_id = extract_id(thread_object)
        print_substep(f"Thread ID: {thread_id}", style="bold blue")

        # Step 2: Tạo TTS audio
        print_step("🎙️ Bước 2: Tạo audio TTS...")
        length, number_of_comments = save_text_to_mp3(thread_object)
        length = math.ceil(length)

        # Step 3: Tạo screenshots
        print_step("📸 Bước 3: Tạo hình ảnh...")
        get_screenshots_of_threads_posts(thread_object, number_of_comments)

        # Step 4: Background
        print_step("🎬 Bước 4: Xử lý background...")
        bg_config = {
            "video": get_background_config("video"),
            "audio": get_background_config("audio"),
        }
        download_background_video(bg_config["video"])
        download_background_audio(bg_config["audio"])
        chop_background(bg_config, length, thread_object)

        # Step 5: Ghép video cuối cùng
        print_step("🎥 Bước 5: Tạo video cuối cùng...")
        make_final_video(number_of_comments, length, thread_object, bg_config)

        # Tìm file video đã tạo
        subreddit = settings.config.get("threads", {}).get("thread", {}).get("channel_name", "threads")
        results_dir = f"./results/{subreddit}"
        video_path = None
        if os.path.exists(results_dir):
            files = sorted(
                [f for f in os.listdir(results_dir) if f.endswith(".mp4")],
                key=lambda x: os.path.getmtime(os.path.join(results_dir, x)),
                reverse=True,
            )
            if files:
                video_path = os.path.join(results_dir, files[0])

        # Step 6: Upload (nếu cấu hình)
        upload_config = settings.config.get("uploaders", {})
        has_uploaders = any(
            upload_config.get(p, {}).get("enabled", False)
            for p in ["youtube", "tiktok", "facebook"]
        )

        if has_uploaders and video_path:
            print_step("📤 Bước 6: Upload video lên các platform...")
            from uploaders.upload_manager import UploadManager

            manager = UploadManager()
            title = thread_object.get("thread_title", "Threads Video")[:100]
            description = thread_object.get("thread_post", "")[:500]

            # Tìm thumbnail nếu có
            thumbnail_path = None
            thumb_candidate = f"./assets/temp/{thread_id}/thumbnail.png"
            if os.path.exists(thumb_candidate):
                thumbnail_path = thumb_candidate

            results = manager.upload_to_all(
                video_path=video_path,
                title=title,
                description=description,
                thumbnail_path=thumbnail_path,
            )

            print_step("📊 Kết quả upload:")
            for platform, url in results.items():
                if url:
                    print_substep(f"  ✅ {platform}: {url}", style="bold green")
                else:
                    print_substep(f"  ❌ {platform}: Thất bại", style="bold red")

        print_step("✅ Pipeline hoàn tất!")

        # Lưu title vào lịch sử để tránh tạo trùng lặp
        title = thread_object.get("thread_title", "")
        tid = thread_object.get("thread_id", "")
        if title:
            save_title(title=title, thread_id=tid, source="threads")

        return video_path

    except Exception as e:
        print_substep(f"❌ Lỗi pipeline: {e}", style="bold red")
        raise


def run_scheduled():
    """Chạy pipeline theo lịch trình đã cấu hình.

    Sử dụng APScheduler để lên lịch.
    """
    try:
        from apscheduler.schedulers.blocking import BlockingScheduler
        from apscheduler.triggers.cron import CronTrigger
    except ImportError:
        print_substep(
            "Cần cài đặt APScheduler: pip install apscheduler",
            style="bold red",
        )
        return

    scheduler_config = settings.config.get("scheduler", {})
    enabled = scheduler_config.get("enabled", False)

    if not enabled:
        print_substep("Scheduler chưa được kích hoạt trong config!", style="bold yellow")
        return

    timezone = scheduler_config.get("timezone", "Asia/Ho_Chi_Minh")
    cron_expression = scheduler_config.get("cron", "0 */3 * * *")  # Mặc định mỗi 3 giờ (8 lần/ngày: 00, 03, 06, 09, 12, 15, 18, 21h)
    max_videos_per_day = scheduler_config.get("max_videos_per_day", 8)

    # Parse cron expression
    cron_parts = cron_expression.split()
    if len(cron_parts) != 5:
        print_substep("Cron expression không hợp lệ! Format: minute hour day month weekday", style="bold red")
        return

    scheduler = BlockingScheduler(timezone=timezone)

    videos_today = {"count": 0, "date": datetime.now().strftime("%Y-%m-%d")}

    def scheduled_job():
        """Job được chạy theo lịch."""
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Reset counter nếu sang ngày mới
        if current_date != videos_today["date"]:
            videos_today["count"] = 0
            videos_today["date"] = current_date

        if videos_today["count"] >= max_videos_per_day:
            print_substep(
                f"Đã đạt giới hạn {max_videos_per_day} video/ngày. Bỏ qua.",
                style="bold yellow",
            )
            return

        print_step(f"⏰ Scheduler: Bắt đầu tạo video lúc {datetime.now().strftime('%H:%M:%S')}...")
        try:
            result = run_pipeline()
            if result:
                videos_today["count"] += 1
                print_substep(
                    f"Video #{videos_today['count']}/{max_videos_per_day} ngày hôm nay",
                    style="bold blue",
                )
        except Exception as e:
            print_substep(f"Scheduler job thất bại: {e}", style="bold red")

    trigger = CronTrigger(
        minute=cron_parts[0],
        hour=cron_parts[1],
        day=cron_parts[2],
        month=cron_parts[3],
        day_of_week=cron_parts[4],
        timezone=timezone,
    )

    scheduler.add_job(scheduled_job, trigger, id="video_pipeline", replace_existing=True)

    print_step(f"📅 Scheduler đã khởi động!")
    print_substep(f"  Cron: {cron_expression}", style="bold blue")
    print_substep(f"  Timezone: {timezone}", style="bold blue")
    print_substep(f"  Max videos/ngày: {max_videos_per_day}", style="bold blue")
    print_substep("  Nhấn Ctrl+C để dừng", style="bold yellow")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print_step("Scheduler đã dừng.")
