"""
YouTube Uploader - Upload video lên YouTube sử dụng YouTube Data API v3.

Yêu cầu:
- Google API credentials (OAuth2)
- YouTube Data API v3 enabled
- Scopes: https://www.googleapis.com/auth/youtube.upload
"""

import os
import json
import time
from typing import Optional

import requests

from uploaders.base_uploader import BaseUploader, VideoMetadata
from utils import settings
from utils.console import print_substep


class YouTubeUploader(BaseUploader):
    """Upload video lên YouTube."""

    platform_name = "YouTube"

    # YouTube API endpoints
    UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"
    VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"
    TOKEN_URL = "https://oauth2.googleapis.com/token"

    # Limits
    MAX_TITLE_LENGTH = 100
    MAX_DESCRIPTION_LENGTH = 5000
    MAX_TAGS = 500  # Total characters for all tags
    MAX_FILE_SIZE = 256 * 1024 * 1024 * 1024  # 256 GB

    def __init__(self):
        super().__init__()
        self.config = settings.config.get("uploaders", {}).get("youtube", {})
        self.access_token = None

    def authenticate(self) -> bool:
        """Xác thực với YouTube API sử dụng refresh token.

        Cấu hình cần có:
        - client_id
        - client_secret
        - refresh_token (lấy từ OAuth2 flow)

        Returns:
            True nếu xác thực thành công.
        """
        client_id = self.config.get("client_id", "")
        client_secret = self.config.get("client_secret", "")
        refresh_token = self.config.get("refresh_token", "")

        if not all([client_id, client_secret, refresh_token]):
            print_substep(
                "YouTube: Thiếu credentials (client_id, client_secret, refresh_token)",
                style="bold red",
            )
            return False

        try:
            response = requests.post(self.TOKEN_URL, data={
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            }, timeout=30)
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data["access_token"]
            self._authenticated = True
            print_substep("YouTube: Xác thực thành công! ✅", style="bold green")
            return True

        except Exception as e:
            print_substep(f"YouTube: Lỗi xác thực - {e}", style="bold red")
            return False

    def upload(self, metadata: VideoMetadata) -> Optional[str]:
        """Upload video lên YouTube.

        Args:
            metadata: VideoMetadata chứa thông tin video.

        Returns:
            URL video trên YouTube, hoặc None nếu thất bại.
        """
        if not self.access_token:
            return None

        title = metadata.title[:self.MAX_TITLE_LENGTH]
        description = self._build_description(metadata)
        tags = metadata.tags or []

        # Thêm hashtags vào description
        if metadata.hashtags:
            hashtag_str = " ".join(f"#{tag}" for tag in metadata.hashtags)
            description = f"{description}\n\n{hashtag_str}"

        # Video metadata
        video_metadata = {
            "snippet": {
                "title": title,
                "description": description[:self.MAX_DESCRIPTION_LENGTH],
                "tags": tags,
                "categoryId": self._get_category_id(metadata.category),
                "defaultLanguage": metadata.language,
                "defaultAudioLanguage": metadata.language,
            },
            "status": {
                "privacyStatus": metadata.privacy,
                "selfDeclaredMadeForKids": False,
            },
        }

        # Schedule publish time
        if metadata.schedule_time and metadata.privacy != "public":
            video_metadata["status"]["publishAt"] = metadata.schedule_time
            video_metadata["status"]["privacyStatus"] = "private"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        # Step 1: Initiate resumable upload
        params = {
            "uploadType": "resumable",
            "part": "snippet,status",
        }

        init_response = requests.post(
            self.UPLOAD_URL,
            headers=headers,
            params=params,
            json=video_metadata,
            timeout=30,
        )
        init_response.raise_for_status()

        upload_url = init_response.headers.get("Location")
        if not upload_url:
            print_substep("YouTube: Không thể khởi tạo upload session", style="bold red")
            return None

        # Step 2: Upload video file
        file_size = os.path.getsize(metadata.file_path)
        # Dynamic timeout: minimum 120s, add 60s per 100MB
        upload_timeout = max(120, 60 * (file_size // (100 * 1024 * 1024) + 1))
        with open(metadata.file_path, "rb") as video_file:
            upload_response = requests.put(
                upload_url,
                headers={
                    "Content-Type": "video/mp4",
                    "Content-Length": str(file_size),
                },
                data=video_file,
                timeout=upload_timeout,
            )
            upload_response.raise_for_status()

        video_data = upload_response.json()
        video_id = video_data.get("id", "")

        if not video_id:
            print_substep("YouTube: Upload thành công nhưng không lấy được video ID", style="bold yellow")
            return None

        # Step 3: Upload thumbnail if available
        if metadata.thumbnail_path and os.path.exists(metadata.thumbnail_path):
            self._upload_thumbnail(video_id, metadata.thumbnail_path)

        video_url = f"https://www.youtube.com/watch?v={video_id}"
        return video_url

    def _upload_thumbnail(self, video_id: str, thumbnail_path: str):
        """Upload thumbnail cho video."""
        try:
            url = f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set"
            with open(thumbnail_path, "rb") as thumb_file:
                response = requests.post(
                    url,
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    params={"videoId": video_id},
                    files={"media": thumb_file},
                    timeout=60,
                )
                response.raise_for_status()
                print_substep("YouTube: Đã upload thumbnail ✅", style="bold green")
        except Exception as e:
            print_substep(f"YouTube: Lỗi upload thumbnail - {e}", style="bold yellow")

    def _build_description(self, metadata: VideoMetadata) -> str:
        """Tạo description cho video YouTube."""
        parts = []
        if metadata.description:
            parts.append(metadata.description)
        parts.append("")
        parts.append("🎬 Video được tạo tự động bởi Threads Video Maker Bot")
        parts.append(f"🌐 Ngôn ngữ: Tiếng Việt")
        return "\n".join(parts)

    @staticmethod
    def _get_category_id(category: str) -> str:
        """Map category name to YouTube category ID."""
        categories = {
            "Entertainment": "24",
            "People & Blogs": "22",
            "Comedy": "23",
            "Education": "27",
            "Science & Technology": "28",
            "News & Politics": "25",
            "Gaming": "20",
            "Music": "10",
        }
        return categories.get(category, "24")
