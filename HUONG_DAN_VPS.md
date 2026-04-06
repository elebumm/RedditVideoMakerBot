# 🇻🇳 HƯỚNG DẪN CÀI ĐẶT VÀ CHẠY TRÊN VPS

## Mục lục

1. [Yêu cầu hệ thống](#1-yêu-cầu-hệ-thống)
2. [Cài đặt trên VPS](#2-cài-đặt-trên-vps)
3. [Cấu hình bắt buộc](#3-cấu-hình-bắt-buộc-configtoml)
4. [Các chế độ chạy](#4-các-chế-độ-chạy)
5. [Chạy nền trên VPS](#5-chạy-nền-trên-vps-với-systemd)
6. [Chạy với Docker](#6-chạy-với-docker-tùy-chọn)
7. [Kiểm tra và khắc phục lỗi](#7-kiểm-tra-và-khắc-phục-lỗi)
8. [Bảng tóm tắt cấu hình](#8-bảng-tóm-tắt-cấu-hình-cần-cập-nhật)

---

## 1. Yêu cầu hệ thống

| Thành phần | Yêu cầu tối thiểu |
|---|---|
| **OS** | Ubuntu 20.04+ / Debian 11+ |
| **RAM** | 2 GB (khuyến nghị 4 GB) |
| **Disk** | 10 GB trống |
| **Python** | 3.10, 3.11 hoặc 3.12 |
| **FFmpeg** | Bắt buộc (cài tự động nếu thiếu) |

---

## 2. Cài đặt trên VPS

### Bước 1: Cập nhật hệ thống và cài đặt phụ thuộc

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv ffmpeg git
```

### Bước 2: Clone dự án

```bash
cd /opt
git clone https://github.com/thaitien280401-stack/RedditVideoMakerBot.git
cd RedditVideoMakerBot
```

### Bước 3: Tạo virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Bước 4: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### Bước 5: Cài đặt Playwright browser (cần cho chế độ screenshot)

```bash
python -m playwright install
python -m playwright install-deps
```

---

## 3. Cấu hình bắt buộc (`config.toml`)

Khi chạy lần đầu, chương trình sẽ tự tạo file `config.toml` và hỏi bạn nhập thông tin.
Bạn cũng có thể tạo trước file `config.toml` trong thư mục gốc dự án:

```toml
# ===== CẤU HÌNH BẮT BUỘC =====

[threads.creds]
access_token = "YOUR_THREADS_ACCESS_TOKEN"    # Lấy từ Meta Developer Portal
user_id = "YOUR_THREADS_USER_ID"              # Threads User ID

[threads.thread]
target_user_id = ""                           # Để trống = dùng user của bạn
post_id = ""                                  # Để trống = tự động chọn thread mới nhất
keywords = "viral, trending, hài hước"        # Từ khóa lọc (tùy chọn)
max_comment_length = 500
min_comment_length = 1
post_lang = "vi"
min_comments = 5
blocked_words = "spam, quảng cáo"
channel_name = "Threads Vietnam"

[settings]
allow_nsfw = false
theme = "dark"
times_to_run = 1
opacity = 0.9
resolution_w = 1080
resolution_h = 1920

[settings.background]
background_video = "minecraft"
background_audio = "lofi"
background_audio_volume = 0.15

[settings.tts]
voice_choice = "googletranslate"              # Tốt nhất cho tiếng Việt
silence_duration = 0.3
no_emojis = false

# ===== SCHEDULER (lên lịch tự động) =====

[scheduler]
enabled = true                                # BẬT lên lịch tự động
cron = "0 */3 * * *"                          # Mỗi 3 giờ tạo 1 video
timezone = "Asia/Ho_Chi_Minh"                 # Múi giờ Việt Nam
max_videos_per_day = 8                        # Tối đa 8 video/ngày

# ===== UPLOAD TỰ ĐỘNG (tùy chọn) =====

[uploaders.youtube]
enabled = false
client_id = ""
client_secret = ""
refresh_token = ""

[uploaders.tiktok]
enabled = false
client_key = ""
client_secret = ""
refresh_token = ""

[uploaders.facebook]
enabled = false
page_id = ""
access_token = ""
```

### Cách lấy Threads API credentials

1. Truy cập [Meta Developer Portal](https://developers.facebook.com/)
2. Tạo App mới → chọn "Business" type
3. Thêm product "Threads API"
4. Vào Settings → Basic → lấy **App ID**
5. Tạo Access Token cho Threads API
6. Lấy **User ID** từ Threads API endpoint: `GET /me?fields=id,username`

---

## 4. Các chế độ chạy

### 4.1. Manual (thủ công) — Mặc định
Tạo video 1 lần, không upload:
```bash
python main.py
```

### 4.2. Auto (tạo + upload)
Tạo video và tự động upload lên các platform đã cấu hình:
```bash
python main.py --mode auto
```

### 4.3. ⭐ Scheduled (lên lịch tự động) — KHUYẾN NGHỊ CHO VPS
Chạy liên tục trên VPS, tự động tạo video theo lịch trình:
```bash
python main.py --mode scheduled
```

**Mặc định:**
- Cron: `0 */3 * * *` → Tạo 1 video **mỗi 3 giờ**
- Lịch chạy: 00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00, 21:00 (giờ VN)
- **= 8 video/ngày**
- Timezone: `Asia/Ho_Chi_Minh`
- Tự động bỏ qua các chủ đề đã tạo video (title deduplication)
- Giới hạn tối đa `max_videos_per_day` video mỗi ngày

### Tùy chỉnh lịch chạy

Thay đổi `cron` trong `config.toml`:

| Cron Expression | Mô tả | Video/ngày |
|---|---|---|
| `0 */3 * * *` | Mỗi 3 giờ (mặc định) | 8 |
| `0 */4 * * *` | Mỗi 4 giờ | 6 |
| `0 */6 * * *` | Mỗi 6 giờ | 4 |
| `0 8,14,20 * * *` | Lúc 8h, 14h, 20h | 3 |
| `0 */2 * * *` | Mỗi 2 giờ | 12 |

---

## 5. Chạy nền trên VPS với systemd

### Bước 1: Tạo systemd service

```bash
sudo nano /etc/systemd/system/threads-video-bot.service
```

Dán nội dung sau:

```ini
[Unit]
Description=Threads Video Maker Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/RedditVideoMakerBot
ExecStart=/opt/RedditVideoMakerBot/venv/bin/python main.py --mode scheduled
Restart=always
RestartSec=30
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

### Bước 2: Kích hoạt và khởi động

```bash
sudo systemctl daemon-reload
sudo systemctl enable threads-video-bot
sudo systemctl start threads-video-bot
```

### Bước 3: Kiểm tra trạng thái

```bash
# Xem trạng thái
sudo systemctl status threads-video-bot

# Xem log realtime
sudo journalctl -u threads-video-bot -f

# Xem log gần nhất
sudo journalctl -u threads-video-bot --since "1 hour ago"

# Restart
sudo systemctl restart threads-video-bot

# Dừng
sudo systemctl stop threads-video-bot
```

---

## 6. Chạy với Docker (tùy chọn)

### Build image

```bash
cd /opt/RedditVideoMakerBot
docker build -t threads-video-bot .
```

### Chạy container

```bash
docker run -d \
  --name threads-bot \
  --restart unless-stopped \
  -v $(pwd)/config.toml:/app/config.toml \
  -v $(pwd)/results:/app/results \
  -v $(pwd)/video_creation/data:/app/video_creation/data \
  threads-video-bot python3 main.py --mode scheduled
```

### Xem log

```bash
docker logs -f threads-bot
```

---

## 7. Kiểm tra và khắc phục lỗi

### Kiểm tra trạng thái

```bash
# Service đang chạy?
sudo systemctl is-active threads-video-bot

# Xem lỗi gần nhất
sudo journalctl -u threads-video-bot --since "30 min ago" --no-pager

# Đếm video đã tạo
ls -la results/*/
```

### Lỗi thường gặp

| Lỗi | Nguyên nhân | Cách khắc phục |
|---|---|---|
| `ModuleNotFoundError` | Thiếu thư viện | `source venv/bin/activate && pip install -r requirements.txt` |
| `FileNotFoundError: ffmpeg` | Chưa cài FFmpeg | `sudo apt install ffmpeg` |
| `Threads API error 401` | Token hết hạn | Tạo access token mới từ Meta Developer Portal |
| `No suitable thread found` | Hết thread mới | Đợi có thread mới hoặc thay `target_user_id` |
| `playwright._impl._errors` | Thiếu browser | `python -m playwright install && python -m playwright install-deps` |
| `Đã đạt giới hạn X video/ngày` | Đã tạo đủ video | Bình thường, sẽ reset vào ngày hôm sau |

### Lịch sử title (tránh trùng lặp)

- File lưu: `video_creation/data/title_history.json`
- Xem title đã tạo: `cat video_creation/data/title_history.json | python -m json.tool`
- Reset (cho phép tạo lại tất cả): `echo "[]" > video_creation/data/title_history.json`

---

## 8. Bảng tóm tắt cấu hình cần cập nhật

### ⚠️ BẮT BUỘC phải thay đổi

| Mục | Key trong config.toml | Mô tả | Cách lấy |
|---|---|---|---|
| **Threads Token** | `threads.creds.access_token` | Access token API | [Meta Developer Portal](https://developers.facebook.com/) |
| **Threads User ID** | `threads.creds.user_id` | User ID Threads | API endpoint `/me?fields=id` |

### 📋 Nên tùy chỉnh

| Mục | Key | Mặc định | Gợi ý |
|---|---|---|---|
| Tên kênh | `threads.thread.channel_name` | "Threads Vietnam" | Tên kênh của bạn |
| Từ khóa | `threads.thread.keywords` | "" | "viral, trending, hài hước" |
| Từ bị chặn | `threads.thread.blocked_words` | "" | "spam, quảng cáo, 18+" |
| Lịch chạy | `scheduler.cron` | `0 */3 * * *` | Xem bảng ở mục 4 |
| Max video/ngày | `scheduler.max_videos_per_day` | 8 | Tùy chỉnh |

### 🔧 Tùy chọn: Upload tự động

| Platform | Keys cần cấu hình |
|---|---|
| **YouTube** | `uploaders.youtube.client_id`, `client_secret`, `refresh_token` |
| **TikTok** | `uploaders.tiktok.client_key`, `client_secret`, `refresh_token` |
| **Facebook** | `uploaders.facebook.page_id`, `access_token` |

---

## Tóm tắt nhanh

```bash
# 1. Cài đặt
cd /opt/RedditVideoMakerBot
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m playwright install && python -m playwright install-deps

# 2. Cấu hình
nano config.toml  # Nhập thông tin Threads API

# 3. Test thử 1 video
python main.py

# 4. Chạy tự động trên VPS (mỗi 3h = 8 video/ngày)
python main.py --mode scheduled

# 5. Hoặc chạy nền với systemd (khuyến nghị)
sudo systemctl enable --now threads-video-bot
```
