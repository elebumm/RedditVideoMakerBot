# 🇻🇳 Threads Video Maker Bot - Phiên Bản Việt Nam 🎥

Tạo video tự động từ nội dung **Threads (Meta)** và đăng lên **TikTok**, **YouTube**, **Facebook**.

Được phát triển dựa trên nền tảng Reddit Video Maker Bot, tối ưu hóa cho thị trường Việt Nam.

## Tính Năng Chính ✨

- 📱 **Threads Integration**: Lấy nội dung tự động từ Threads (Meta) thay vì Reddit
- 🎙️ **TTS Tiếng Việt**: Hỗ trợ đọc tiếng Việt qua Google Translate TTS, OpenAI, và nhiều engine khác
- 📤 **Auto-Upload**: Tự động đăng video lên TikTok, YouTube, Facebook
- ⏰ **Lên Lịch Tự Động**: Cron-based scheduling với múi giờ Việt Nam
- 🎬 **Video Chất Lượng**: Background gaming, nhạc nền lofi, subtitle overlay
- 🔄 **Pipeline Hoàn Chỉnh**: Từ lấy nội dung → TTS → Screenshot → Video → Upload

## Cài Đặt 🛠️

### Yêu Cầu
- Python 3.10, 3.11 hoặc 3.12
- FFmpeg
- Tài khoản Threads Developer (Meta)

### Bước 1: Clone và cài đặt
```bash
git clone https://github.com/thaitien280401-stack/RedditVideoMakerBot.git
cd RedditVideoMakerBot
pip install -r requirements.txt
```

### Bước 2: Cấu hình
Chạy lần đầu để tạo file `config.toml`:
```bash
python main.py
```

Hoặc copy từ template:
```bash
cp utils/.config.template.toml config.toml
```

### Bước 3: Điền thông tin API
Chỉnh sửa `config.toml`:

```toml
[threads.creds]
access_token = "YOUR_THREADS_ACCESS_TOKEN"
user_id = "YOUR_THREADS_USER_ID"

[settings.tts]
voice_choice = "googletranslate"  # Hỗ trợ tiếng Việt tốt nhất
```

## Sử Dụng 🚀

### Chế độ Manual (Mặc định)
```bash
python main.py
```

### Chế độ Auto (Tạo + Upload)
```bash
python main.py --mode auto
```

### Chế độ Scheduled (Lên lịch tự động)
```bash
python main.py --mode scheduled
```

### Legacy Reddit Mode
```bash
python main.py --reddit
```

## Cấu Hình Upload 📤

### YouTube
```toml
[uploaders.youtube]
enabled = true
client_id = "YOUR_GOOGLE_CLIENT_ID"
client_secret = "YOUR_GOOGLE_CLIENT_SECRET"
refresh_token = "YOUR_GOOGLE_REFRESH_TOKEN"
```

### TikTok
```toml
[uploaders.tiktok]
enabled = true
client_key = "YOUR_TIKTOK_CLIENT_KEY"
client_secret = "YOUR_TIKTOK_CLIENT_SECRET"
refresh_token = "YOUR_TIKTOK_REFRESH_TOKEN"
```

### Facebook
```toml
[uploaders.facebook]
enabled = true
page_id = "YOUR_FACEBOOK_PAGE_ID"
access_token = "YOUR_FACEBOOK_PAGE_ACCESS_TOKEN"
```

## Cấu Hình Scheduler ⏰

```toml
[scheduler]
enabled = true
cron = "0 8,14,20 * * *"  # Chạy lúc 8h, 14h, 20h hàng ngày
timezone = "Asia/Ho_Chi_Minh"
max_videos_per_day = 4
```

## Kiến Trúc Hệ Thống 🏗️

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Threads API   │────▶│   Video Engine   │────▶│  Upload Manager │
│  (Meta Graph)   │     │  TTS + FFmpeg    │     │  YT/TT/FB APIs  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
   threads/            video_creation/            uploaders/
   threads_client.py   threads_screenshot.py      youtube_uploader.py
                       voices.py                  tiktok_uploader.py
                       final_video.py             facebook_uploader.py
                                                  upload_manager.py
                              │
                              ▼
                       scheduler/
                       pipeline.py (APScheduler)
```
  you will then have to upload manually. This is for the sake of avoiding any sort of community guideline issues.

## Requirements

- Python 3.10
- Playwright (this should install automatically in installation)

## Installation 👩‍💻

1. Clone this repository:
    ```sh
    git clone https://github.com/elebumm/RedditVideoMakerBot.git
    cd RedditVideoMakerBot
    ```

2. Create and activate a virtual environment:
    - On **Windows**:
        ```sh
        python -m venv ./venv
        .\venv\Scripts\activate
        ```
    - On **macOS and Linux**:
        ```sh
        python3 -m venv ./venv
        source ./venv/bin/activate
        ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Install Playwright and its dependencies:
    ```sh
    python -m playwright install
    python -m playwright install-deps
    ```

---

**EXPERIMENTAL!!!!**

   - On macOS and Linux (Debian, Arch, Fedora, CentOS, and based on those), you can run an installation script that will automatically install steps 1 to 3. (requires bash)
   - `bash <(curl -sL https://raw.githubusercontent.com/elebumm/RedditVideoMakerBot/master/install.sh)`
   - This can also be used to update the installation

---

5. Run the bot:
    ```sh
    python main.py
    ```

6. Visit [the Reddit Apps page](https://www.reddit.com/prefs/apps), and set up an app that is a "script". Paste any URL in the redirect URL field, for example: `https://jasoncameron.dev`.

7. The bot will prompt you to fill in your details to connect to the Reddit API and configure the bot to your liking.

8. Enjoy 😎

9. If you need to reconfigure the bot, simply open the `config.toml` file and delete the lines that need to be changed. On the next run of the bot, it will help you reconfigure those options.

(Note: If you encounter any errors installing or running the bot, try using `python3` or `pip3` instead of `python` or `pip`.)

For a more detailed guide about the bot, please refer to the [documentation](https://reddit-video-maker-bot.netlify.app/).

## Video

https://user-images.githubusercontent.com/66544866/173453972-6526e4e6-c6ef-41c5-ab40-5d275e724e7c.mp4

## Contributing & Ways to improve 📈

In its current state, this bot does exactly what it needs to do. However, improvements can always be made!

I have tried to simplify the code so anyone can read it and start contributing at any skill level. Don't be shy :) contribute!

- [ ] Creating better documentation and adding a command line interface.
- [x] Allowing the user to choose background music for their videos.
- [x] Allowing users to choose a reddit thread instead of being randomized.
- [x] Allowing users to choose a background that is picked instead of the Minecraft one.
- [x] Allowing users to choose between any subreddit.
- [x] Allowing users to change voice.
- [x] Checks if a video has already been created
- [x] Light and Dark modes
- [x] NSFW post filter

Please read our [contributing guidelines](CONTRIBUTING.md) for more detailed information.

### For any questions or support join the [Discord](https://discord.gg/qfQSx45xCV) server

## Developers and maintainers.

Elebumm (Lewis#6305) - https://github.com/elebumm (Founder)

Jason Cameron - https://github.com/JasonLovesDoggo (Maintainer)

Simon (OpenSourceSimon) - https://github.com/OpenSourceSimon

CallumIO (c.#6837) - https://github.com/CallumIO

Verq (Verq#2338) - https://github.com/CordlessCoder

LukaHietala (Pix.#0001) - https://github.com/LukaHietala

Freebiell (Freebie#3263) - https://github.com/FreebieII

Aman Raza (electro199#8130) - https://github.com/electro199

Cyteon (cyteon) - https://github.com/cyteon


## LICENSE
[Roboto Fonts](https://fonts.google.com/specimen/Roboto/about) are licensed under [Apache License V2](https://www.apache.org/licenses/LICENSE-2.0)
