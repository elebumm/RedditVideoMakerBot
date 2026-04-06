"""
Base Uploader - Lớp cơ sở cho tất cả uploaders.
"""

import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List

from utils.console import print_step, print_substep


@dataclass
class VideoMetadata:
    """Metadata cho video cần upload."""
    file_path: str
    title: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    thumbnail_path: Optional[str] = None
    schedule_time: Optional[str] = None  # ISO 8601 format
    privacy: str = "public"  # public, private, unlisted
    category: str = "Entertainment"
    language: str = "vi"  # Vietnamese


class BaseUploader(ABC):
    """Lớp cơ sở cho tất cả platform uploaders."""

    platform_name: str = "Unknown"

    def __init__(self):
        self._authenticated = False

    @abstractmethod
    def authenticate(self) -> bool:
        """Xác thực với platform API.

        Returns:
            True nếu xác thực thành công.
        """
        pass

    @abstractmethod
    def upload(self, metadata: VideoMetadata) -> Optional[str]:
        """Upload video lên platform.

        Args:
            metadata: VideoMetadata chứa thông tin video.

        Returns:
            URL của video đã upload, hoặc None nếu thất bại.
        """
        pass

    def validate_video(self, metadata: VideoMetadata) -> bool:
        """Kiểm tra video có hợp lệ trước khi upload.

        Args:
            metadata: VideoMetadata cần kiểm tra.

        Returns:
            True nếu hợp lệ.
        """
        if not os.path.exists(metadata.file_path):
            print_substep(f"[{self.platform_name}] File không tồn tại: {metadata.file_path}", style="bold red")
            return False

        file_size = os.path.getsize(metadata.file_path)
        if file_size == 0:
            print_substep(f"[{self.platform_name}] File rỗng: {metadata.file_path}", style="bold red")
            return False

        if not metadata.title:
            print_substep(f"[{self.platform_name}] Thiếu tiêu đề video", style="bold red")
            return False

        return True

    def safe_upload(self, metadata: VideoMetadata, max_retries: int = 3) -> Optional[str]:
        """Upload video với retry logic.

        Args:
            metadata: VideoMetadata chứa thông tin video.
            max_retries: Số lần thử lại tối đa.

        Returns:
            URL của video đã upload, hoặc None nếu thất bại.
        """
        if not self.validate_video(metadata):
            return None

        if not self._authenticated:
            print_step(f"Đang xác thực với {self.platform_name}...")
            if not self.authenticate():
                print_substep(f"Xác thực {self.platform_name} thất bại!", style="bold red")
                return None

        for attempt in range(1, max_retries + 1):
            try:
                print_step(f"Đang upload lên {self.platform_name} (lần {attempt}/{max_retries})...")
                url = self.upload(metadata)
                if url:
                    print_substep(
                        f"Upload {self.platform_name} thành công! URL: {url}",
                        style="bold green",
                    )
                    return url
            except Exception as e:
                print_substep(
                    f"[{self.platform_name}] Lỗi upload (lần {attempt}): {e}",
                    style="bold red",
                )
                if attempt < max_retries:
                    backoff = min(2 ** attempt, 60)  # Exponential backoff, max 60s
                    print_substep(f"Chờ {backoff}s trước khi thử lại...", style="bold yellow")
                    time.sleep(backoff)

        print_substep(f"Upload {self.platform_name} thất bại sau {max_retries} lần thử!", style="bold red")
        return None
