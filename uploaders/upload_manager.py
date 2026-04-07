"""
Upload Manager - Quản lý upload video lên nhiều platform cùng lúc.
"""

import os
from typing import Dict, List, Optional

from uploaders.base_uploader import BaseUploader, VideoMetadata
from uploaders.facebook_uploader import FacebookUploader
from uploaders.tiktok_uploader import TikTokUploader
from uploaders.youtube_uploader import YouTubeUploader
from utils import settings
from utils.console import print_step, print_substep


class UploadManager:
    """Quản lý upload video lên nhiều platform."""

    PLATFORM_MAP = {
        "youtube": YouTubeUploader,
        "tiktok": TikTokUploader,
        "facebook": FacebookUploader,
    }

    def __init__(self):
        self.uploaders: Dict[str, BaseUploader] = {}
        self._init_uploaders()

    def _init_uploaders(self):
        """Khởi tạo uploaders dựa trên cấu hình."""
        upload_config = settings.config.get("uploaders", {})

        for platform_name, uploader_class in self.PLATFORM_MAP.items():
            platform_config = upload_config.get(platform_name, {})
            if platform_config.get("enabled", False):
                self.uploaders[platform_name] = uploader_class()
                print_substep(f"Đã kích hoạt uploader: {platform_name}", style="bold blue")

    def upload_to_all(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: Optional[List[str]] = None,
        hashtags: Optional[List[str]] = None,
        thumbnail_path: Optional[str] = None,
        schedule_time: Optional[str] = None,
        privacy: str = "public",
    ) -> Dict[str, Optional[str]]:
        """Upload video lên tất cả platform đã cấu hình.

        Args:
            video_path: Đường dẫn file video.
            title: Tiêu đề video.
            description: Mô tả video.
            tags: Danh sách tags.
            hashtags: Danh sách hashtags.
            thumbnail_path: Đường dẫn thumbnail.
            schedule_time: Thời gian lên lịch (ISO 8601).
            privacy: Quyền riêng tư (public/private/unlisted).

        Returns:
            Dict mapping platform name -> video URL (hoặc None nếu thất bại).
        """
        if not self.uploaders:
            print_substep("Không có uploader nào được kích hoạt!", style="bold yellow")
            return {}

        metadata = VideoMetadata(
            file_path=video_path,
            title=title,
            description=description,
            tags=tags or [],
            hashtags=hashtags or self._default_hashtags(),
            thumbnail_path=thumbnail_path,
            schedule_time=schedule_time,
            privacy=privacy,
            language="vi",
        )

        results = {}
        print_step(f"Đang upload video lên {len(self.uploaders)} platform...")

        for platform_name, uploader in self.uploaders.items():
            print_step(f"📤 Đang upload lên {platform_name}...")
            url = uploader.safe_upload(metadata)
            results[platform_name] = url

        # Summary
        print_step("📊 Kết quả upload:")
        success_count = 0
        for platform, url in results.items():
            if url:
                print_substep(f"  ✅ {platform}: {url}", style="bold green")
                success_count += 1
            else:
                print_substep(f"  ❌ {platform}: Thất bại", style="bold red")

        print_substep(
            f"Upload hoàn tất: {success_count}/{len(results)} platform thành công",
            style="bold blue",
        )

        return results

    def upload_to_platform(
        self,
        platform_name: str,
        metadata: VideoMetadata,
    ) -> Optional[str]:
        """Upload video lên một platform cụ thể.

        Args:
            platform_name: Tên platform.
            metadata: VideoMetadata chứa thông tin video.

        Returns:
            URL video, hoặc None nếu thất bại.
        """
        if platform_name not in self.uploaders:
            print_substep(f"Platform '{platform_name}' chưa được kích hoạt!", style="bold red")
            return None

        return self.uploaders[platform_name].safe_upload(metadata)

    @staticmethod
    def _default_hashtags() -> List[str]:
        """Hashtags mặc định cho thị trường Việt Nam."""
        return [
            "threads",
            "viral",
            "vietnam",
            "trending",
            "foryou",
            "fyp",
            "threadsvn",
        ]
