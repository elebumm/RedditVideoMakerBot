# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Reddit Video Maker Bot - Manual Pipeline**

This project creates short-form videos from manually captured screenshots of social media posts (Reddit, Threads, X/Twitter, or any platform). The workflow is:

1. **Capture**: User manually screenshots posts and comments
2. **Organize**: Place screenshots in structured folders with text files
3. **Process**: Bot generates TTS audio from text files
4. **Render**: Bot assembles screenshots + audio + background into final video

**Key Philosophy**: No API access required. Works with any platform. User controls content selection.

## Tech Stack

- **Python**: 3.10, 3.11, or 3.12 (strict requirement)
- **FFmpeg**: Video processing and encoding (libx264 CPU encoder by default)
- **MoviePy**: Video/audio manipulation
- **TTS Engines**: Multiple providers (OhFreeMe, Crikk, GoogleTranslate, ElevenLabs, AWS Polly, OpenAI, TikTok)
- **Configuration**: TOML format (config.toml)
- **Dependencies**: See requirements.txt

## Development Commands

### Setup
```bash
# Create virtual environment
python3 -m venv ./venv
source ./venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright (for screenshot tools if needed)
python -m playwright install
python -m playwright install-deps
```

### Manual Pipeline Commands

```bash
# Create a new post folder with template files
python manual_main.py init <post_id> [--platform reddit|threads|x|other]

# Render a single post into video
python manual_main.py render <post_id>

# Render all unrendered posts
python manual_main.py render --all

# Re-render even if already done
python manual_main.py render <post_id> --force

# List all posts and their status
python manual_main.py list
```

### Testing Individual Modules

```bash
# Test TTS processor (after creating a post folder with text files)
python -c "from manual.scanner import PostScanner; from manual.tts_processor import ManualTTSProcessor; scanner = PostScanner(); post = scanner.scan_one('test_post'); tts = ManualTTSProcessor(post); tts.process()"

# Test scanner validation
python -c "from manual.scanner import PostScanner; scanner = PostScanner(); print(scanner.list_status())"
```

## Architecture: manual_main.py Workflow

### Entry Point: manual_main.py

**Purpose**: CLI entry point for the manual screenshot-to-video pipeline.

**Key Functions**:
- `load_config()`: Loads config.toml and sets up settings.config globally for TTS engines
- `cmd_init()`: Creates new post folder with template structure
- `cmd_render()`: Orchestrates the render pipeline (TTS → Video)
- `cmd_list()`: Lists all posts with status (ready/incomplete/empty)

**Configuration Strategy**:
1. Starts with built-in defaults (so TTS engines always have required config)
2. Deep-merges config.toml on top of defaults
3. Extracts `[manual]` section for manual-specific settings
4. Sets `settings.config` globally so shared modules (TTS, backgrounds) work

### Pipeline Flow

```
User Input (Screenshots + Text)
         ↓
    PostScanner (manual/scanner.py)
         ↓ validates & builds post_object
    ManualTTSProcessor (manual/tts_processor.py)
         ↓ text → MP3 audio files
    ManualVideoBuilder (manual/video_builder.py)
         ↓ screenshots + audio + background → MP4
    Final Video (manual_results/)
```

### Module: manual/scanner.py

**Class**: `PostScanner`

**Responsibilities**:
- Scans `manual_posts/` directory for post folders
- Validates folder structure (naming convention, required files)
- Builds unified `post_object` dict for downstream processing

**File Naming Convention**:
```
<number>_<type>.<ext>

Examples:
0_title.png      # Screenshot of post title (required)
0_title.txt      # Text for TTS (required if no .mp3)
0_title.mp3      # Pre-recorded audio (optional, skips TTS if present)
1_comment.png    # Screenshot of comment 1
1_comment.txt    # Text for TTS
2_comment.png    # Screenshot of comment 2
2_comment.txt    # Text for TTS
```

**meta.json Format** (Optional):

The `meta.json` file provides optional metadata about the post. It's created automatically by `python manual_main.py init` with a template structure.

```json
{
    "platform": "reddit",
    "post_id": "my_post_001",
    "title": "What's the most underrated life hack?",
    "author": "u/username",
    "url": "https://reddit.com/r/AskReddit/comments/...",
    "created_at": "2026-05-26",
    "tags": ["life_hacks", "tips"],
    "notes": "High engagement post, good for shorts"
}
```

**Fields**:
- `platform`: Source platform (reddit, threads, x, other) - used in post_object
- `post_id`: Post identifier - should match folder name
- `title`: Post title - used if 0_title.txt is empty or missing
- `author`: Original author - used in post_object for tracking
- `url`: Source URL - used in post_object for reference
- `created_at`: Original post date - for your records
- `tags`: List of tags - for organization/filtering
- `notes`: Free-form notes - for your records

**Usage**:
- All fields are optional (scanner provides defaults)
- `platform`, `title`, `author`, `url` are read by scanner and included in post_object
- `created_at`, `tags`, `notes` are for your organization only (not used by pipeline)
- If `title` is empty, scanner uses first 100 chars of 0_title.txt
- If `platform` is empty, defaults to "other"

**Validation Rules**:
- At least 1 image file must exist
- Title image (0_title.png) is required
- Each image must have corresponding .mp3 OR .txt file
- .mp3 takes priority over .txt (if both exist, TTS is skipped)
- .txt files must not be empty (if no .mp3 exists)

**post_object Structure**:
```python
{
    "post_id": str,           # Folder name
    "platform": str,          # From meta.json or "reddit" default
    "title": str,             # From meta.json or extracted from 0_title.txt
    "author": str,            # From meta.json or "unknown"
    "url": str,               # From meta.json or ""
    "post_dir": str,          # Absolute path to post folder
    "screenshots": [
        {
            "index": int,                # 0, 1, 2, ...
            "type": "title"|"comment",   # From filename
            "image_path": str,           # Absolute path to .png
            "text_path": str|None,       # Absolute path to .txt (if exists)
            "audio_path": str|None,      # Absolute path to .mp3 (if exists)
            "text": str|None,            # Text content (loaded from .txt)
            "audio_duration": float|None # Set by TTS processor
        },
        ...
    ]
}
```

### Module: manual/tts_processor.py

**Class**: `ManualTTSProcessor`

**Responsibilities**:
- Converts text files to MP3 audio using configured TTS engine
- Skips TTS if pre-recorded .mp3 already exists
- Respects max_video_length by truncating clips
- Updates post_object with audio_path and audio_duration

**TTS Engine Selection**:
- Reads from `settings.config["settings"]["tts"]["voice_choice"]`
- Supported engines: ohfreeme, crikk, googletranslate, elevenlabs, aws_polly, openai, tiktok, pyttsx
- Falls back to GoogleTranslate if config missing (no API key needed)

**Processing Flow**:
1. Filter screenshots that need TTS (have text_path, no audio_path)
2. For each screenshot:
   - Load text from .txt file
   - Strip comments (lines starting with #)
   - Call TTS engine to generate MP3
   - Probe audio duration with ffmpeg
   - Update screenshot dict with audio_path and audio_duration
3. Check total duration against max_video_length
4. Truncate if needed (keeps title + as many comments as fit)

**Key Methods**:
- `process()`: Main entry point, returns updated post_object
- `_load_text()`: Loads text from .txt file, strips comments
- `_generate_audio()`: Calls TTS engine wrapper
- `_get_audio_duration()`: Uses ffmpeg.probe to get duration

### Module: manual/video_builder.py

**Class**: `ManualVideoBuilder`

**Responsibilities**:
- Downloads/selects background video and audio
- Chops backgrounds to match video length
- Overlays screenshots onto background with timing
- Applies watermark (if enabled)
- Renders final MP4 video

**Video Assembly Pipeline**:
1. **Background Selection**:
   - Scans local directories (assets/backgrounds/video, assets/backgrounds/audio)
   - If local files exist: picks random
   - If no local files: downloads from YouTube (via background_options)
   
2. **Background Preparation**:
   - Chops video/audio to match total TTS duration
   - Crops video to aspect ratio (W:H from config)
   - Removes audio from background video (will be mixed later)

3. **Audio Track Assembly**:
   - Concatenates all TTS audio clips in order
   - Mixes with background audio at configured volume
   - Outputs final audio track

4. **Video Overlay**:
   - Scales background to final resolution (W×H)
   - For each screenshot:
     - Scales to screenshot_width_percent of video width
     - Applies opacity
     - Overlays at center position
     - Enables only during its audio duration
   - Overlays watermark (if enabled) at position (0,0)

5. **Rendering**:
   - Uses FFmpeg with configured encoder (libx264 default)
   - Shows progress bar during render
   - Saves to output_dir with normalized filename
   - Records to video_creation/data/videos.json (prevents re-rendering)

**Key Configuration**:
- `encoder`: Video encoder (libx264 for CPU, h264_nvenc for NVIDIA GPU)
- `resolution_w`, `resolution_h`: Output video dimensions (1080×1920 default)
- `opacity`: Screenshot overlay opacity (0.0-1.0)
- `screenshot_width_percent`: Screenshot width as % of video width (85 default)
- `background_audio_volume`: Background audio volume (0.0-1.0, 0 = disabled)
- `watermark_enabled`: Enable/disable watermark overlay
- `watermark_path`: Path to watermark PNG (must be 1080×1920 with alpha transparency)

**Background Priority**:
1. Local files in `background_video_dir` / `background_audio_dir`
2. YouTube download (if config specifies name and no local files)
3. Random selection if config = "random"

### Module: TTS/engine_wrapper.py

**Class**: `TTSEngine`

**Purpose**: Unified wrapper for all TTS engines. Used by both manual and automated workflows.

**Key Methods**:
- `run()`: Main entry point, generates MP3 files for all text
- `call_tts()`: Calls specific TTS module with text and filepath
- `split_post()`: Splits long text into chunks if exceeds max_chars
- `add_periods()`: Normalizes text (adds periods, removes URLs)

**TTS Module Interface**:
Each TTS module (TTS/OhFreeMe.py, TTS/Crikk.py, etc.) must implement:
```python
class TTSModule:
    max_chars: int  # Maximum characters per request
    
    def run(self, text: str, filepath: str, random_voice: bool = False):
        # Generate TTS audio and save to filepath
        pass
```

## Configuration: config.toml

### Manual Pipeline Section

```toml
[manual]
input_dir = "manual_posts"                    # Input folder for post folders
output_dir = "manual_results"                 # Output folder for rendered videos
encoder = "libx264"                           # Video encoder (libx264 or h264_nvenc)
resolution_w = 1080                           # Video width
resolution_h = 1920                           # Video height (portrait)
opacity = 0.9                                 # Screenshot overlay opacity
background_video = "random"                   # "random" or specific name
background_audio = "random"                   # "random" or specific name
background_audio_volume = 0.15                # 0.0 = disabled, 1.0 = full volume
max_video_length = 120                        # Max video duration in seconds
screenshot_width_percent = 85                 # Screenshot width as % of video width
watermark_enabled = true                      # Enable watermark overlay
watermark_path = "assets/backgrounds/transparent-bg.png"  # Watermark PNG path
background_video_dir = "assets/backgrounds/video"         # Local video files
background_audio_dir = "assets/backgrounds/audio"         # Local audio files
```

### TTS Configuration (Shared)

```toml
[settings.tts]
voice_choice = "ohfreeme"                     # TTS engine to use
random_voice = false                          # Randomize voice per clip
silence_duration = 0.3                        # Silence between clips (seconds)
no_emojis = false                             # Strip emojis from text

# OhFreeMe TTS (Vietnamese support)
ohfreeme_lang = "vi"                          # Language code
ohfreeme_gender = "random"                    # "male", "female", or "random"
ohfreeme_rate = 1                             # Speech rate (0.5-2.0)
ohfreeme_pitch = 0                            # Pitch adjustment (-10 to 10)
ohfreeme_enhance = false                      # Audio enhancement

# Crikk TTS
# (API key loaded from environment variable CRIKK_API_KEY)

# ElevenLabs TTS
elevenlabs_voice_name = "Bella"
elevenlabs_api_key = ""                       # Or use ELEVEN_API_KEY env var

# OpenAI TTS
openai_api_url = "https://api.openai.com/v1/"
openai_api_key = ""                           # Or use OPENAI_API_KEY env var
openai_voice_name = "alloy"
openai_model = "tts-1"

# AWS Polly TTS
aws_polly_voice = "Matthew"

# TikTok TTS
tiktok_voice = "en_us_001"
tiktok_sessionid = ""                         # Required for TikTok TTS
```

### Resolution and Aspect Ratio

```toml
[settings]
resolution_w = 1080                           # Also used by manual pipeline if not in [manual]
resolution_h = 1920                           # Also used by manual pipeline if not in [manual]
opacity = 0.9                                 # Also used by manual pipeline if not in [manual]
```

## Environment Variables

Some TTS engines load configuration from environment variables via a `.env` file in the project root. The project uses `python-dotenv` to load these variables.

**TTS Engines Using Environment Variables**:
- **OhFreeMe**: Requires API URL, base URL, and JWT token
- **Crikk**: Requires API URL and base URL
- **ElevenLabs**: Can use `ELEVEN_API_KEY` (alternative to config.toml)
- **OpenAI**: Can use `OPENAI_API_KEY` (alternative to config.toml)

**Priority**: Environment variables take precedence over config.toml values for API keys.

**Security Note**: The `.env` file should be added to `.gitignore` and never committed to version control.

## Common Development Patterns

### Adding a New Post

```bash
# 1. Create folder structure
python manual_main.py init my_post_001 --platform reddit

# 2. Add screenshots and text files
# - Capture screenshots from social media
# - Save as 0_title.png, 1_comment.png, 2_comment.png, ...
# - Edit corresponding .txt files with text for TTS

# 3. Render video
python manual_main.py render my_post_001

# 4. Check output
ls manual_results/my_post_001.mp4
```

### Using Pre-recorded Audio

If you have pre-recorded audio (e.g., from a professional voice actor):

```bash
# Place .mp3 files alongside .txt files
manual_posts/my_post/
├── 0_title.png
├── 0_title.mp3      # Pre-recorded audio (TTS will be skipped)
├── 0_title.txt      # Optional, for reference
├── 1_comment.png
├── 1_comment.mp3    # Pre-recorded audio
└── 1_comment.txt    # Optional
```

The scanner prioritizes .mp3 over .txt. TTS is only called if .mp3 is missing.

### Debugging TTS Issues

```bash
# 1. Check which TTS engine is configured
grep "voice_choice" config.toml

# 2. Test TTS engine directly
python -c "from TTS.OhFreeMe import OhFreeMe; tts = OhFreeMe(); tts.run('Test text', 'test.mp3')"

# 3. Check TTS output files
ls assets/temp/<post_id>/mp3/

# 4. Verify audio duration
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 assets/temp/<post_id>/mp3/0_title.mp3
```

### Debugging Video Rendering Issues

```bash
# 1. Check FFmpeg installation
ffmpeg -version

# 2. Test encoder (libx264 should always work)
ffmpeg -f lavfi -i testsrc=duration=1:size=1080x1920:rate=30 -c:v libx264 test.mp4

# 3. Check background files
ls assets/backgrounds/video/
ls assets/backgrounds/audio/

# 4. Check temp files during render
ls assets/temp/<post_id>/
# Should contain: background.mp4, background.mp3, background_noaudio.mp4, audio.mp3

# 5. Check watermark file
ls assets/backgrounds/transparent-bg.png
```

### Changing Video Encoder

For faster rendering with NVIDIA GPU:

```toml
[manual]
encoder = "h264_nvenc"  # Requires NVIDIA GPU with NVENC support
```

Test if NVENC is available:
```bash
ffmpeg -encoders | grep nvenc
```

### Batch Processing Multiple Posts

```bash
# Create multiple posts
for id in post_001 post_002 post_003; do
    python manual_main.py init $id
done

# After adding screenshots and text, render all
python manual_main.py render --all
```

## File Structure

```
RedditVideoMakerBot/
├── manual_main.py              # CLI entry point for manual pipeline
├── config.toml                 # Configuration file
├── requirements.txt            # Python dependencies
│
├── manual/                     # Manual pipeline modules
│   ├── __init__.py
│   ├── scanner.py              # Folder scanner & validator
│   ├── tts_processor.py        # TTS text → MP3
│   └── video_builder.py        # Video assembly & rendering
│
├── TTS/                        # TTS engine implementations
│   ├── engine_wrapper.py       # Unified TTS wrapper
│   ├── OhFreeMe.py             # OhFreeMe TTS (Vietnamese)
│   ├── Crikk.py                # Crikk TTS
│   ├── GTTS.py                 # Google Translate TTS
│   ├── elevenlabs.py           # ElevenLabs TTS
│   ├── aws_polly.py            # AWS Polly TTS
│   ├── openai_tts.py           # OpenAI TTS
│   ├── TikTok.py               # TikTok TTS
│   └── pyttsx.py               # pyttsx3 TTS (offline)
│
├── video_creation/             # Shared video utilities
│   ├── background.py           # Background download & chopping
│   ├── final_video.py          # (Not used by manual pipeline)
│   ├── screenshot_downloader.py # (Not used by manual pipeline)
│   └── voices.py               # (Not used by manual pipeline)
│
├── utils/                      # Shared utilities
│   ├── settings.py             # Config loader
│   ├── console.py              # Rich console output
│   ├── ffmpeg_install.py       # FFmpeg checker
│   ├── voice.py                # Text sanitization
│   └── ...
│
├── manual_posts/               # Input: User-created post folders
│   └── <post_id>/
│       ├── meta.json           # Optional metadata
│       ├── 0_title.png         # Required: Title screenshot
│       ├── 0_title.txt         # Required: Title text for TTS
│       ├── 1_comment.png       # Optional: Comment screenshots
│       ├── 1_comment.txt       # Optional: Comment text for TTS
│       └── ...
│
├── manual_results/             # Output: Rendered videos
│   └── <post_id>.mp4
│
├── assets/
│   ├── backgrounds/
│   │   ├── video/              # Local background videos
│   │   ├── audio/              # Local background audio
│   │   └── transparent-bg.png  # Watermark overlay
│   └── temp/                   # Temporary files during render
│       └── <post_id>/
│           ├── mp3/            # TTS audio files
│           ├── background.mp4  # Chopped background video
│           ├── background.mp3  # Chopped background audio
│           └── ...
│
└── video_creation/data/
    └── videos.json             # Tracking of rendered videos (prevents re-render)
```

## Important Notes

### Python Version Requirement

The project strictly requires Python 3.10, 3.11, or 3.12. This is checked at startup in manual_main.py:

```python
if sys.version_info.major != 3 or sys.version_info.minor not in [10, 11, 12]:
    print("This program requires Python 3.10, 3.11, or 3.12.")
    sys.exit(1)
```

### FFmpeg Requirement

FFmpeg must be installed on the system. The bot checks for FFmpeg at startup via `ffmpeg_install()` and will attempt to install it if missing (on some platforms).

### Config.toml Can Be Empty

The manual pipeline has built-in defaults for all settings. If config.toml is missing or empty, the bot will use GoogleTranslate TTS (no API key needed) and default video settings.

### Watermark Overlay

The watermark feature overlays a PNG image on top of the entire video. The watermark file must:
- Be 1080×1920 pixels (matching video resolution)
- Have alpha transparency (transparent areas show video underneath)
- Be placed at `assets/backgrounds/transparent-bg.png` (or custom path in config)

The watermark is overlaid at position (0,0) and spans the entire video duration.

### Video Tracking

Rendered videos are tracked in `video_creation/data/videos.json` to prevent re-rendering. This file is shared between manual and automated workflows. To force re-render:

```bash
python manual_main.py render <post_id> --force
```

Or manually remove the entry from videos.json.

### Background Video/Audio Sources

**Priority**:
1. Local files in `assets/backgrounds/video/` and `assets/backgrounds/audio/`
2. YouTube download (if no local files and config specifies a name)

**Local Files**:
- Drop .mp4/.mkv/.webm files into `assets/backgrounds/video/`
- Drop .mp3/.wav/.ogg files into `assets/backgrounds/audio/`
- Bot will randomly select from available files

**YouTube Download**:
- Defined in `video_creation/background.py` → `background_options` dict
- Downloads on first use, cached for future renders
- Requires internet connection

### TTS Engine Selection

The manual pipeline uses the same TTS engines as the automated workflow. Engine is selected via `settings.config["settings"]["tts"]["voice_choice"]`.

**Recommended for Vietnamese**: `ohfreeme` or `crikk`
**Recommended for English**: `elevenlabs`, `openai`, or `googletranslate`
**No API Key Required**: `googletranslate` (default fallback)

### Text File Format

Text files (.txt) support comments:
```
# This is a comment and will be ignored by TTS
This text will be read by TTS.

# Another comment
More text to be read.
```

Lines starting with `#` are stripped before TTS processing.

### Error Handling

The manual pipeline validates post folders before rendering:
- Missing required files → Error message with specific missing files
- Empty text files → Error message
- Invalid naming convention → Files are ignored

Use `python manual_main.py list` to check status of all posts before rendering.
