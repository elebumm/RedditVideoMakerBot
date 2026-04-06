"""
TikTok Uploader - Upload video lên TikTok sử dụng Content Posting API.

Yêu cầu:
- TikTok Developer App
- Content Posting API access
- OAuth2 access token
Docs: https://developers.tiktok.com/doc/content-posting-api-get-started
"""

import json
import os
import time
from typing import Optional

import requests

from uploaders.base_uploader import BaseUploader, VideoMetadata
from utils import settings
from utils.console import print_substep


class TikTokUploader(BaseUploader):
    """Upload video lên TikTok."""

    platform_name = "TikTok"

    # TikTok API endpoints
    API_BASE = "https://open.tiktokapis.com/v2"
    TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"

    # Limits
    MAX_CAPTION_LENGTH = 2200
    MAX_FILE_SIZE = 4 * 1024 * 1024 * 1024  # 4 GB
    MIN_DURATION = 3  # seconds
    MAX_DURATION = 600  # 10 minutes

    def __init__(self):
        super().__init__()
        self.config = settings.config.get("uploaders", {}).get("tiktok", {})
        self.access_token = None

    def authenticate(self) -> bool:
        """Xác thực với TikTok API sử dụng refresh token.

        Returns:
            True nếu xác thực thành công.
        """
        client_key = self.config.get("client_key", "")
        client_secret = self.config.get("client_secret", "")
        refresh_token = self.config.get("refresh_token", "")

        if not all([client_key, client_secret, refresh_token]):
            print_substep(
                "TikTok: Thiếu credentials (client_key, client_secret, refresh_token)",
                style="bold red",
            )
            return False

        try:
            response = requests.post(self.TOKEN_URL, json={
                "client_key": client_key,
                "client_secret": client_secret,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            }, timeout=30)
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data.get("data", {}).get("access_token", "")

            if self.access_token:
                self._authenticated = True
                print_substep("TikTok: Xác thực thành công! ✅", style="bold green")
                return True
            else:
                print_substep("TikTok: Không lấy được access token", style="bold red")
                return False

        except Exception as e:
            print_substep(f"TikTok: Lỗi xác thực - {e}", style="bold red")
            return False

    def upload(self, metadata: VideoMetadata) -> Optional[str]:
        """Upload video lên TikTok sử dụng Content Posting API.

        Flow:
        1. Initialize upload → get upload_url
        2. Upload video file to upload_url
        3. Publish video

        Args:
            metadata: VideoMetadata chứa thông tin video.

        Returns:
            URL video trên TikTok, hoặc None nếu thất bại.
        """
        if not self.access_token:
            return None

        file_size = os.path.getsize(metadata.file_path)
        if file_size > self.MAX_FILE_SIZE:
            print_substep(f"TikTok: File quá lớn ({file_size} bytes)", style="bold red")
            return None

        # Build caption
        caption = self._build_caption(metadata)

        # Step 1: Initialize upload
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        }

        init_body = {
            "post_info": {
                "title": caption,
                "privacy_level": self._map_privacy(metadata.privacy),
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False,
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": file_size,
                "chunk_size": file_size,  # Single chunk upload
                "total_chunk_count": 1,
            },
        }

        if metadata.schedule_time:
            init_body["post_info"]["schedule_time"] = metadata.schedule_time

        try:
            init_response = requests.post(
                f"{self.API_BASE}/post/publish/inbox/video/init/",
                headers=headers,
                json=init_body,
                timeout=30,
            )
            init_response.raise_for_status()
            init_data = init_response.json()

            publish_id = init_data.get("data", {}).get("publish_id", "")
            upload_url = init_data.get("data", {}).get("upload_url", "")

            if not upload_url:
                print_substep("TikTok: Không lấy được upload URL", style="bold red")
                return None

        except Exception as e:
            print_substep(f"TikTok: Lỗi khởi tạo upload - {e}", style="bold red")
            return None

        # Step 2: Upload video file
        try:
            with open(metadata.file_path, "rb") as video_file:
                upload_headers = {
                    "Content-Type": "video/mp4",
                    "Content-Length": str(file_size),
                    "Content-Range": f"bytes 0-{file_size - 1}/{file_size}",
                }
                upload_response = requests.put(
                    upload_url,
                    headers=upload_headers,
                    data=video_file,
                    timeout=600,
                )
                upload_response.raise_for_status()

        except Exception as e:
            print_substep(f"TikTok: Lỗi upload file - {e}", style="bold red")
            return None

        # Step 3: Check publish status
        status_url = f"{self.API_BASE}/post/publish/status/fetch/"
        for attempt in range(10):
            try:
                status_response = requests.post(
                    status_url,
                    headers=headers,
                    json={"publish_id": publish_id},
                    timeout=30,
                )
                status_data = status_response.json()
                status = status_data.get("data", {}).get("status", "")

                if status == "PUBLISH_COMPLETE":
                    print_substep("TikTok: Upload thành công! ✅", style="bold green")
                    return f"https://www.tiktok.com/@user/video/{publish_id}"
                elif status == "FAILED":
                    reason = status_data.get("data", {}).get("fail_reason", "Unknown")
                    print_substep(f"TikTok: Upload thất bại - {reason}", style="bold red")
                    return None

                time.sleep(5)  # Wait 5 seconds before checking again
            except Exception:
                time.sleep(5)

        print_substep("TikTok: Upload timeout", style="bold yellow")
        return None

    def _build_caption(self, metadata: VideoMetadata) -> str:
        """Tạo caption cho video TikTok."""
        parts = []
        if metadata.title:
            parts.append(metadata.title)
        if metadata.hashtags:
            hashtag_str = " ".join(f"#{tag}" for tag in metadata.hashtags)
            parts.append(hashtag_str)
        caption = " ".join(parts)
        return caption[:self.MAX_CAPTION_LENGTH]

    @staticmethod
    def _map_privacy(privacy: str) -> str:
        """Map privacy setting to TikTok format."""
        mapping = {
            "public": "PUBLIC_TO_EVERYONE",
            "private": "SELF_ONLY",
            "friends": "MUTUAL_FOLLOW_FRIENDS",
            "unlisted": "SELF_ONLY",
        }
        return mapping.get(privacy, "PUBLIC_TO_EVERYONE")
