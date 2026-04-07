"""
Facebook Uploader - Upload video lên Facebook sử dụng Graph API.

Yêu cầu:
- Facebook Developer App
- Page Access Token (cho Page upload) hoặc User Access Token
- Permissions: publish_video, pages_manage_posts
Docs: https://developers.facebook.com/docs/video-api/guides/publishing
"""

import json
import os
import time
from typing import Optional

import requests

from uploaders.base_uploader import BaseUploader, VideoMetadata
from utils import settings
from utils.console import print_substep


class FacebookUploader(BaseUploader):
    """Upload video lên Facebook Page/Profile."""

    platform_name = "Facebook"

    # Facebook API endpoints
    GRAPH_API_BASE = "https://graph.facebook.com/v21.0"

    # Limits
    MAX_DESCRIPTION_LENGTH = 63206
    MAX_TITLE_LENGTH = 255
    MAX_FILE_SIZE = 10 * 1024 * 1024 * 1024  # 10 GB

    def __init__(self):
        super().__init__()
        self.config = settings.config.get("uploaders", {}).get("facebook", {})
        self.access_token = None
        self.page_id = None

    def authenticate(self) -> bool:
        """Xác thực với Facebook Graph API.

        Sử dụng Page Access Token cho upload lên Page.

        Returns:
            True nếu xác thực thành công.
        """
        self.access_token = self.config.get("access_token", "")
        self.page_id = self.config.get("page_id", "")

        if not self.access_token:
            print_substep("Facebook: Thiếu access_token", style="bold red")
            return False

        if not self.page_id:
            print_substep("Facebook: Thiếu page_id", style="bold red")
            return False

        # Verify token
        try:
            response = requests.get(
                f"{self.GRAPH_API_BASE}/me",
                params={"access_token": self.access_token},
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()

            if "id" in data:
                self._authenticated = True
                print_substep(
                    f"Facebook: Xác thực thành công (Page: {data.get('name', self.page_id)}) ✅",
                    style="bold green",
                )
                return True
            else:
                print_substep("Facebook: Token không hợp lệ", style="bold red")
                return False

        except Exception as e:
            print_substep(f"Facebook: Lỗi xác thực - {e}", style="bold red")
            return False

    def upload(self, metadata: VideoMetadata) -> Optional[str]:
        """Upload video lên Facebook Page.

        Sử dụng Resumable Upload API cho file lớn.

        Args:
            metadata: VideoMetadata chứa thông tin video.

        Returns:
            URL video trên Facebook, hoặc None nếu thất bại.
        """
        if not self.access_token or not self.page_id:
            return None

        file_size = os.path.getsize(metadata.file_path)

        title = metadata.title[: self.MAX_TITLE_LENGTH]
        description = self._build_description(metadata)

        # Step 1: Initialize upload session
        try:
            init_response = requests.post(
                f"{self.GRAPH_API_BASE}/{self.page_id}/videos",
                data={
                    "upload_phase": "start",
                    "file_size": file_size,
                    "access_token": self.access_token,
                },
                timeout=30,
            )
            init_response.raise_for_status()
            init_data = init_response.json()

            upload_session_id = init_data.get("upload_session_id", "")
            video_id = init_data.get("video_id", "")

            if not upload_session_id:
                print_substep("Facebook: Không thể khởi tạo upload session", style="bold red")
                return None

        except Exception as e:
            print_substep(f"Facebook: Lỗi khởi tạo upload - {e}", style="bold red")
            return None

        # Step 2: Upload video chunks
        try:
            chunk_size = 4 * 1024 * 1024  # 4 MB chunks
            start_offset = 0

            with open(metadata.file_path, "rb") as video_file:
                while start_offset < file_size:
                    chunk = video_file.read(chunk_size)
                    transfer_response = requests.post(
                        f"{self.GRAPH_API_BASE}/{self.page_id}/videos",
                        data={
                            "upload_phase": "transfer",
                            "upload_session_id": upload_session_id,
                            "start_offset": start_offset,
                            "access_token": self.access_token,
                        },
                        files={"video_file_chunk": ("chunk", chunk, "application/octet-stream")},
                        timeout=120,
                    )
                    transfer_response.raise_for_status()
                    transfer_data = transfer_response.json()

                    start_offset = int(transfer_data.get("start_offset", file_size))
                    end_offset = int(transfer_data.get("end_offset", file_size))

                    if start_offset >= file_size:
                        break

        except Exception as e:
            print_substep(f"Facebook: Lỗi upload file - {e}", style="bold red")
            return None

        # Step 3: Finish upload
        try:
            finish_data = {
                "upload_phase": "finish",
                "upload_session_id": upload_session_id,
                "access_token": self.access_token,
                "title": title,
                "description": description[: self.MAX_DESCRIPTION_LENGTH],
            }

            if metadata.schedule_time:
                finish_data["scheduled_publish_time"] = metadata.schedule_time
                finish_data["published"] = "false"

            if metadata.thumbnail_path and os.path.exists(metadata.thumbnail_path):
                with open(metadata.thumbnail_path, "rb") as thumb:
                    finish_response = requests.post(
                        f"{self.GRAPH_API_BASE}/{self.page_id}/videos",
                        data=finish_data,
                        files={"thumb": thumb},
                        timeout=60,
                    )
            else:
                finish_response = requests.post(
                    f"{self.GRAPH_API_BASE}/{self.page_id}/videos",
                    data=finish_data,
                    timeout=60,
                )

            finish_response.raise_for_status()
            finish_result = finish_response.json()

            if finish_result.get("success", False):
                video_url = f"https://www.facebook.com/{self.page_id}/videos/{video_id}"
                return video_url
            else:
                print_substep("Facebook: Upload hoàn tất nhưng không thành công", style="bold red")
                return None

        except Exception as e:
            print_substep(f"Facebook: Lỗi kết thúc upload - {e}", style="bold red")
            return None

    def _build_description(self, metadata: VideoMetadata) -> str:
        """Tạo description cho video Facebook."""
        parts = []
        if metadata.description:
            parts.append(metadata.description)

        if metadata.hashtags:
            hashtag_str = " ".join(f"#{tag}" for tag in metadata.hashtags)
            parts.append(hashtag_str)

        parts.append("")
        parts.append("🎬 Video được tạo tự động bởi Threads Video Maker Bot")

        return "\n".join(parts)
