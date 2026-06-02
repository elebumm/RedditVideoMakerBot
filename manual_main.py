#!/usr/bin/env python
"""
Manual Screenshot → Video Pipeline — Entry Point

Create videos from manually captured screenshots and text files,
without requiring any social media API access.

Supports screenshots from: Reddit, Threads (Meta), X (Twitter), or any platform.

Usage:
    python manual_main.py init <post_id> [--platform reddit|threads|x|other]
    python manual_main.py render <post_id>
    python manual_main.py render --all
    python manual_main.py list
"""

import argparse
import json
import shutil
import sys
from os.path import exists
from pathlib import Path

import toml

from utils import settings
from utils.console import print_markdown, print_step, print_substep
from utils.ffmpeg_install import ffmpeg_install
from manual.scanner import PostScanner
from manual.tts_processor import ManualTTSProcessor
from manual.video_builder import ManualVideoBuilder

__VERSION__ = "1.0.0"


# ────────────────────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────────────────────

# Default config for manual pipeline (used when [manual] section not in config.toml)
MANUAL_DEFAULTS = {
    "input_dir": "manual_posts",
    "output_dir": "manual_results",
    "encoder": "libx264",
    "resolution_w": 1080,
    "resolution_h": 1920,
    "opacity": 1,
    "background_video": "random",
    "background_audio": "random",
    "background_video_dir": "assets/backgrounds/video",
    "background_audio_dir": "assets/backgrounds/audio",
    "background_audio_volume": 0.1,
    "max_video_length": 120,
    "screenshot_width_percent": 85,
    "watermark_enabled": True,
    "watermark_path": "assets/backgrounds/transparent-bg.png",
}

# Full default settings.config that TTS engines and shared modules expect.
# This ensures the manual flow works even if config.toml is empty or missing sections.
_BASE_SETTINGS_DEFAULTS = {
    "reddit": {
        "creds": {
            "client_id": "",
            "client_secret": "",
            "username": "",
            "password": "",
            "2fa": False,
        },
        "thread": {
            "subreddit": "",
            "post_id": "",
            "max_comment_length": 500,
            "min_comment_length": 1,
            "post_lang": "vi",
            "min_comments": 20,
            "blocked_words": "",
        },
    },
    "ai": {
        "ai_similarity_enabled": False,
        "ai_similarity_keywords": "",
    },
    "settings": {
        "allow_nsfw": False,
        "theme": "dark",
        "times_to_run": 1,
        "opacity": 0.9,
        "storymode": False,
        "storymodemethod": 1,
        "storymode_max_length": 1000,
        "resolution_w": 1080,
        "resolution_h": 1920,
        "zoom": 1,
        "channel_name": "Reddit Tales",
        "background": {
            "background_video": "minecraft",
            "background_audio": "lofi",
            "background_audio_volume": 0.1,
            "enable_extra_audio": False,
            "background_thumbnail": False,
            "background_thumbnail_font_family": "arial",
            "background_thumbnail_font_size": 96,
            "background_thumbnail_font_color": "255,255,255",
        },
        "tts": {
            "voice_choice": "zall",
            "random_voice": False,
            "elevenlabs_voice_name": "Bella",
            "elevenlabs_api_key": "",
            "aws_polly_voice": "Matthew",
            "streamlabs_polly_voice": "Matthew",
            "tiktok_voice": "en_us_001",
            "tiktok_sessionid": "",
            "python_voice": "1",
            "py_voice_num": "2",
            "silence_duration": 0.3,
            "no_emojis": False,
            "openai_api_url": "https://api.openai.com/v1/",
            "openai_api_key": "",
            "openai_voice_name": "alloy",
            "openai_model": "tts-1",
            "zall_lang": "vi",
            "zall_gender": "random",
            "zall_rate": 1,
            "zall_pitch": 0,
            "zall_natural_voice": True,
            "zall_enable_brand_keywords": False,
        },
    },
}


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge two dicts. Values in 'override' take priority."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config() -> dict:
    """Load config and set up settings.config for TTS engines and backgrounds.

    Strategy:
    1. Start with full default config (so TTS engines always have what they need)
    2. If config.toml exists and has content, deep-merge on top of defaults
    3. Extract [manual] section for manual-specific settings
    4. Set settings.config globally so shared modules (TTS, background, etc.) work

    Returns:
        dict: Manual-specific config merged with defaults
    """
    # Start with complete defaults
    config = _deep_merge({}, _BASE_SETTINGS_DEFAULTS)

    # Try to load config.toml and merge on top
    config_path = Path("config.toml")
    if config_path.exists():
        try:
            file_config = toml.load(str(config_path))
            if file_config:  # Not empty
                config = _deep_merge(config, file_config)
                print_substep("Loaded config from config.toml", style="dim")
        except Exception as e:
            print_substep(f"Warning: Could not parse config.toml: {e}", style="yellow")
    else:
        print_substep(
            "config.toml not found — using built-in defaults. "
            "TTS will use GoogleTranslate (no API key needed).",
            style="yellow",
        )

    # Set global settings.config so TTS engines and shared modules work
    settings.config = config

    # Build manual-specific config: defaults + [manual] section from config.toml
    manual_config = {**MANUAL_DEFAULTS}
    if "manual" in config:
        manual_config.update(config["manual"])

    return manual_config


# ────────────────────────────────────────────────────────────────
# Commands
# ────────────────────────────────────────────────────────────────


def cmd_init(args, manual_config):
    """Create a new post folder with template files."""
    from manual.scanner import create_post_folder

    post_id = args.post_id
    platform = getattr(args, "platform", "reddit")

    input_dir = manual_config["input_dir"]
    post_dir = create_post_folder(input_dir, post_id, platform)

    print_markdown(f"### Post folder created: `{post_dir}`")


def cmd_render(args, manual_config):
    """Render one or all posts into videos."""

    scanner = PostScanner(input_dir=manual_config["input_dir"])

    if args.all:
        # Render all ready posts
        posts = scanner.scan_all()
        if not posts:
            print_substep("No valid posts found in the input directory.", style="red")
            return

        # Filter out already rendered
        posts_to_render = []
        for post in posts:
            if _is_already_done(post["post_id"]):
                print_substep(f"  ⏭ {post['post_id']} — already rendered, skipping", style="blue")
            else:
                posts_to_render.append(post)

        if not posts_to_render:
            print_substep("All posts have already been rendered!", style="green")
            return

        print_step(f"📋 Rendering {len(posts_to_render)} posts...")
        for i, post in enumerate(posts_to_render):
            print_markdown(
                f"### [{i+1}/{len(posts_to_render)}] Rendering: {post['post_id']}"
            )
            _render_single(post, manual_config, force=args.force)
    else:
        # Render single post
        if not args.post_id:
            print_substep("Please specify a post_id or use --all", style="red")
            return

        post = scanner.scan_one(args.post_id)
        if post is None:
            return  # Error already printed by scanner

        if _is_already_done(post["post_id"]) and not args.force:
            print_substep(
                f"Post '{post['post_id']}' already rendered. Use --force to re-render.",
                style="yellow",
            )
            return

        _render_single(post, manual_config, force=args.force)


def _render_single(post_object: dict, manual_config: dict, force: bool = False):
    """Render a single post into a video.

    Pipeline:
    1. TTS: Convert text → MP3 audio files
    2. Video: Assemble screenshots + audio + background → MP4
    """
    post_id = post_object["post_id"]

    if force:
        temp_path = Path(f"assets/temp/{post_id}")
        if temp_path.exists():
            try:
                shutil.rmtree(temp_path)
                print_substep("🗑️ Cleaned temp folder (--force mode)", style="dim")
            except Exception as e:
                print_substep(f"Failed to clean temp folder: {e}", style="red")
                print_substep("Aborting render to avoid inconsistent state.", style="red")
                return

    print_step(f"🚀 Starting render for: {post_id}")

    # Step 1: TTS
    max_length = manual_config.get("max_video_length", 120)
    tts = ManualTTSProcessor(post_object, max_length=max_length)
    post_object = tts.process()

    # Check if we have audio
    clips_with_audio = [s for s in post_object["screenshots"] if s.get("audio_path")]
    if not clips_with_audio:
        print_substep("No audio generated. Check text files.", style="red")
        return

    # Step 2: Video build
    builder = ManualVideoBuilder(post_object, manual_config)
    output_path = builder.build()

    if output_path:
        print_markdown(f"### ✅ Video saved: `{output_path}`")
    else:
        print_substep("Video rendering failed.", style="red")


def cmd_list(args, manual_config):
    """List all posts and their status."""
    from manual.scanner import PostScanner

    scanner = PostScanner(input_dir=manual_config["input_dir"])
    statuses = scanner.list_status()

    if not statuses:
        print_substep(
            f"No posts found in '{manual_config['input_dir']}/'. "
            f"Run 'python manual_main.py init <post_id>' to create one.",
            style="yellow",
        )
        return

    # Status emoji map
    status_icons = {
        "ready": "✅",
        "incomplete": "⚠️",
        "empty": "❌",
    }

    print_step("📋 Manual Posts Status")
    print()

    for s in statuses:
        icon = status_icons.get(s["status"], "❓")
        rendered = "🎬" if _is_already_done(s["post_id"]) else "  "
        print_substep(
            f"  {icon} {rendered} {s['post_id']:30s} "
            f"| {s['num_images']} 🖼️  {s.get('num_audios', 0)} 🎵  {s['num_texts']} 📝 "
            f"| {s['status']}",
            style="bold" if s["status"] == "ready" else "",
        )
        if s["errors"]:
            for err in s["errors"]:
                print_substep(f"      ↳ {err}", style="red")

    print()
    ready_count = sum(1 for s in statuses if s["status"] == "ready")
    rendered_count = sum(1 for s in statuses if _is_already_done(s["post_id"]))
    print_substep(
        f"  Total: {len(statuses)} posts | "
        f"{ready_count} ready | "
        f"{rendered_count} rendered",
        style="bold cyan",
    )


def _is_already_done(post_id: str) -> bool:
    """Check if a post has already been rendered (shared videos.json)."""
    videos_path = "./video_creation/data/videos.json"
    if not exists(videos_path):
        return False
    try:
        with open(videos_path, "r", encoding="utf-8") as f:
            done_videos = json.load(f)
        return any(v.get("id") == post_id for v in done_videos)
    except (json.JSONDecodeError, IOError):
        return False


# ────────────────────────────────────────────────────────────────
# CLI
# ────────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="manual_main.py",
        description="Manual Screenshot → Video Pipeline. "
        "Create videos from screenshots captured from Reddit, Threads, X, or any platform.",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__VERSION__}"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init command
    init_parser = subparsers.add_parser("init", help="Create a new post folder with template files")
    init_parser.add_argument("post_id", type=str, help="Name/ID for the post folder")
    init_parser.add_argument(
        "--platform",
        type=str,
        default="reddit",
        choices=["reddit", "threads", "x", "other"],
        help="Source platform (default: reddit)",
    )

    # render command
    render_parser = subparsers.add_parser("render", help="Render post(s) into video(s)")
    render_parser.add_argument(
        "post_id", type=str, nargs="?", default=None, help="Post ID to render"
    )
    render_parser.add_argument(
        "--all", action="store_true", help="Render all unrendered posts"
    )
    render_parser.add_argument(
        "--force", action="store_true", help="Re-render even if already done"
    )
    render_parser.add_argument(
        "--lang", type=str, default="vi", help="Override TTS language (e.g. vi, en)"
    )

    # list command
    subparsers.add_parser("list", help="List all posts and their status")

    return parser


def main():
    print(
        """
╔══════════════════════════════════════════════════════════╗
║       Manual Screenshot → Video Pipeline v1.0.0         ║
║   Supports: Reddit • Threads • X • Any Platform         ║
╚══════════════════════════════════════════════════════════╝
"""
    )

    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Check Python version
    if sys.version_info.major != 3 or sys.version_info.minor not in [10, 11, 12]:
        print("This program requires Python 3.10, 3.11, or 3.12.")
        sys.exit(1)

    # Check FFmpeg
    ffmpeg_install()

    # Load config
    manual_config = load_config()

    # Create input directory if it doesn't exist
    input_dir = Path(manual_config["input_dir"])
    input_dir.mkdir(parents=True, exist_ok=True)

    # Dispatch command
    commands = {
        "init": cmd_init,
        "render": cmd_render,
        "list": cmd_list,
    }

    cmd_func = commands.get(args.command)
    if cmd_func:
        try:
            cmd_func(args, manual_config)
        except KeyboardInterrupt:
            print("\nInterrupted by user.")
            sys.exit(0)
        except Exception as e:
            print_substep(f"Error: {e}", style="red")
            raise
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
