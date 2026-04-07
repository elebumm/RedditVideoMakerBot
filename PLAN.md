# 🇻🇳 Kế Hoạch Chuyển Đổi: Reddit Video Maker → Threads Vietnam Video Maker

## Tổng Quan
Chuyển đổi ứng dụng Reddit Video Maker Bot thành công cụ tự động tạo video từ nội dung Threads (Meta) cho thị trường Việt Nam, với khả năng tự động đăng lên TikTok, YouTube và Facebook.

---

## Giai Đoạn 1: Thay Thế Reddit bằng Threads API
### 1.1 Module `threads/` - Lấy nội dung từ Threads
- Tạo `threads/__init__.py`
- Tạo `threads/threads_client.py` - Client gọi Threads API (Meta Graph API)
  - Đăng nhập OAuth2 với Threads API
  - Lấy danh sách bài viết trending/hot
  - Lấy replies (comments) của bài viết
  - Lọc nội dung theo từ khóa, độ dài, ngôn ngữ
- Cấu trúc dữ liệu trả về tương tự reddit_object:
  ```python
  {
      "thread_url": "https://threads.net/@user/post/...",
      "thread_title": "Nội dung bài viết",
      "thread_id": "abc123",
      "thread_author": "@username",
      "is_nsfw": False,
      "thread_post": "Nội dung đầy đủ",
      "comments": [
          {
              "comment_body": "Nội dung reply",
              "comment_url": "permalink",
              "comment_id": "xyz789",
              "comment_author": "@user2"
          }
      ]
  }
  ```

### 1.2 Cập nhật Screenshot cho Threads
- Tạo `video_creation/threads_screenshot.py`
  - Render HTML template theo style Threads
  - Hỗ trợ giao diện dark/light mode
  - Hiển thị avatar, username, verified badge
  - Font hỗ trợ tiếng Việt (Unicode đầy đủ)

---

## Giai Đoạn 2: Tối Ưu Cho Thị Trường Việt Nam
### 2.1 Vietnamese TTS
- Sử dụng Google Translate TTS (gTTS) với ngôn ngữ `vi`
- Hỗ trợ giọng đọc tiếng Việt tự nhiên
- Cấu hình mặc định `post_lang = "vi"`

### 2.2 Xử Lý Văn Bản Tiếng Việt
- Cập nhật `utils/voice.py` cho tiếng Việt
- Xử lý dấu, ký tự Unicode Vietnamese
- Tối ưu ngắt câu cho TTS tiếng Việt

---

## Giai Đoạn 3: Auto-Posting - Đăng Tự Động
### 3.1 Module `uploaders/`
- `uploaders/__init__.py`
- `uploaders/base_uploader.py` - Base class
- `uploaders/tiktok_uploader.py` - Đăng lên TikTok
  - Sử dụng TikTok Content Posting API
  - Hỗ trợ set caption, hashtags
  - Schedule posting
- `uploaders/youtube_uploader.py` - Đăng lên YouTube
  - Sử dụng YouTube Data API v3
  - Upload video với title, description, tags
  - Set privacy (public/private/unlisted)
  - Schedule publishing
- `uploaders/facebook_uploader.py` - Đăng lên Facebook
  - Sử dụng Facebook Graph API
  - Upload video lên Page hoặc Profile
  - Set caption, scheduling

### 3.2 Upload Manager
- `uploaders/upload_manager.py`
  - Quản lý upload đồng thời nhiều platform
  - Retry logic khi upload thất bại
  - Logging và tracking trạng thái

---

## Giai Đoạn 4: Hệ Thống Lên Lịch Tự Động
### 4.1 Module `scheduler/`
- `scheduler/__init__.py`
- `scheduler/scheduler.py` - Lên lịch tạo và đăng video
  - Sử dụng APScheduler
  - Cron-style scheduling
  - Hỗ trợ múi giờ Việt Nam (Asia/Ho_Chi_Minh)
- `scheduler/pipeline.py` - Pipeline tự động
  - Fetch content → TTS → Screenshots → Video → Upload
  - Error handling và retry
  - Notification khi hoàn thành

---

## Giai Đoạn 5: Cập Nhật Cấu Hình & Entry Point
### 5.1 Config mới
- Cập nhật `utils/.config.template.toml` thêm sections:
  - `[threads.creds]` - Threads API credentials
  - `[uploaders.tiktok]` - TikTok config
  - `[uploaders.youtube]` - YouTube config
  - `[uploaders.facebook]` - Facebook config
  - `[scheduler]` - Scheduling config

### 5.2 Entry Point
- Cập nhật `main.py` cho workflow mới
- Hỗ trợ 3 modes: manual, auto, scheduled

---

## Dependencies Mới
```
google-api-python-client    # YouTube Data API
google-auth-oauthlib        # Google OAuth
apscheduler                 # Task scheduling
httpx                       # Async HTTP client (Threads API)
```
