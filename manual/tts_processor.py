"""
TTS Processor for the manual pipeline.

Takes a post_object (built by scanner.py), generates MP3 audio files
for each screenshot's text using the existing TTS engines, and updates
the post_object with audio paths and durations.

Reuses TTS engines from TTS/ module — no code duplication.
"""

import re
import time
from pathlib import Path
from typing import Tuple

from moviepy import AudioFileClip

from utils import settings
from utils.console import print_step, print_substep
from utils.voice import sanitize_text


class ManualTTSProcessor:
    """Processes text-to-speech for manual pipeline posts."""

    def __init__(self, post_object: dict, max_length: int = 120):
        """
        Args:
            post_object: Post data from scanner.py
            max_length: Maximum total audio length in seconds (default: 120s = 2 min)
        """
        self.post = post_object
        self.post_id = post_object["post_id"]
        self.max_length = max_length
        self.mp3_dir = Path(f"assets/temp/{self.post_id}/mp3")
        self.tts_module = None

    def process(self) -> dict:
        """Process audio for all screenshots.

        For each screenshot:
        - If .mp3 already provided (audio_path set by scanner) → skip TTS, just measure duration
        - If only .txt provided → run TTS to generate .mp3
        - If neither → skip

        Returns:
            Updated post_object with audio_path and audio_duration filled in
        """
        self.mp3_dir.mkdir(parents=True, exist_ok=True)
        print_step("🔊 Processing audio files...")

        existing_audio = self._scan_existing_audio()
        if existing_audio:
            print_substep(
                f"  ♻ Found {len(existing_audio)} cached TTS audio file(s).",
                style="dim",
            )

        total_duration = 0
        processed_count = 0
        tts_needed = False

        for screenshot in self.post["screenshots"]:
            idx = screenshot["index"]

            # Case 1: .mp3 already provided — just measure duration
            if screenshot.get("audio_path"):
                duration = self._get_audio_duration(screenshot["audio_path"])

                screenshot["audio_duration"] = duration
                total_duration += duration
                processed_count += 1
                print_substep(
                    f"  ✓ #{idx} → {duration:.1f}s (pre-recorded .mp3)",
                    style="green",
                )
                continue

            # Case 2: Cached temp .mp3 from a previous failed render — validate and reuse
            cached_audio_path = existing_audio.get(idx)
            if cached_audio_path:
                if self._validate_audio_file(cached_audio_path):
                    duration = self._get_audio_duration(cached_audio_path)
                    screenshot["audio_path"] = cached_audio_path
                    screenshot["audio_duration"] = duration
                    total_duration += duration
                    processed_count += 1
                    print_substep(
                        f"  ✓ #{idx} → {duration:.1f}s (reused cached .mp3)",
                        style="green",
                    )
                    continue
                print_substep(
                    f"  ⚠ Cached audio #{idx} is invalid, regenerating...",
                    style="yellow",
                )

            # Case 3: Only .txt provided — need TTS
            text = screenshot.get("text", "").strip()
            if not text:
                print_substep(
                    f"  ⚠ Screenshot #{idx} has no audio or text, skipping.",
                    style="yellow",
                )
                continue

            # Initialize TTS engine only when needed (lazy)
            if not tts_needed:
                print_substep("  📝 Some entries need TTS generation...")
                self.tts_module = self._get_tts_engine()
                tts_needed = True

            mp3_path = str(self.mp3_dir / f"{idx}.mp3")

            # Sanitize and process text
            clean_text = self._process_text(text)
            if not clean_text or clean_text.isspace():
                print_substep(
                    f"  ⚠ Screenshot #{idx} text is empty after sanitization, skipping.",
                    style="yellow",
                )
                continue

            # Handle long text by splitting
            if len(clean_text) > self.tts_module.max_chars:
                self._generate_split_audio(clean_text, idx, mp3_path)
            else:
                self._generate_audio(clean_text, mp3_path)

            # Measure duration
            duration = self._get_audio_duration(mp3_path)

            # Update screenshot entry
            screenshot["audio_path"] = mp3_path
            screenshot["audio_duration"] = duration
            total_duration += duration
            processed_count += 1

            # Sleep 10s between TTS generation
            print_substep("  💤 Sleeping 10s...", style="dim")
            time.sleep(10)

            print_substep(
                f"  ✓ #{idx} → {duration:.1f}s (TTS generated, {len(clean_text)} chars)",
                style="green",
            )

            # Check max length
            if total_duration > self.max_length and processed_count > 1:
                print_substep(
                    f"  ⚠ Total duration ({total_duration:.1f}s) exceeds max ({self.max_length}s). "
                    f"Stopping at {processed_count} clips.",
                    style="yellow",
                )
                break

        self.post["total_duration"] = total_duration
        print_substep(
            f"✅ {processed_count} audio clips ready, total: {total_duration:.1f}s",
            style="bold green",
        )

        return self.post

    def _scan_existing_audio(self) -> dict[int, str]:
        """Return temp mp3 candidates mapped by screenshot index."""
        if not self.mp3_dir.exists():
            return {}

        existing_audio = {}
        for mp3_file in sorted(self.mp3_dir.glob("*.mp3")):
            if mp3_file.name.endswith(".part.mp3"):
                continue
            if not mp3_file.stem.isdigit():
                continue
            existing_audio[int(mp3_file.stem)] = str(mp3_file)
        return existing_audio

    def _get_audio_duration(self, filepath: str) -> float:
        """Return audio duration in seconds, or 0.0 if unreadable."""
        try:
            clip = AudioFileClip(filepath)
            duration = float(clip.duration or 0)
            clip.close()
            return duration
        except Exception as e:
            print_substep(f"  ✗ Failed to read audio: {e}", style="red")
            return 0.0

    def _validate_audio_file(self, filepath: str) -> bool:
        """Return True when an existing audio file can be reused."""
        audio_path = Path(filepath)
        if not audio_path.exists() or audio_path.stat().st_size == 0:
            return False
        return self._get_audio_duration(filepath) > 0

    def _get_tts_engine(self):
        """Initialize the TTS engine based on config.

        Reuses the TTS engines from video_creation/voices.py
        """
        from TTS.GTTS import GTTS
        from TTS.OhFreeMe import OhFreeMe
        from TTS.Crikk import Crikk
        from TTS.TikTok import TikTok
        from TTS.aws_polly import AWSPolly
        from TTS.elevenlabs import elevenlabs
        from TTS.openai_tts import OpenAITTS
        from TTS.pyttsx import pyttsx
        from TTS.streamlabs_polly import StreamlabsPolly

        providers = {
            "googletranslate": GTTS,
            "ohfreeme": OhFreeMe,
            "crikk": Crikk,
            "awspolly": AWSPolly,
            "streamlabspolly": StreamlabsPolly,
            "tiktok": TikTok,
            "pyttsx": pyttsx,
            "elevenlabs": elevenlabs,
            "openai": OpenAITTS,
        }

        voice_choice = settings.config["settings"]["tts"]["voice_choice"]
        engine_class = providers.get(str(voice_choice).lower())

        if engine_class is None:
            print_substep(
                f"Unknown TTS provider: {voice_choice}. Falling back to GoogleTranslate.",
                style="yellow",
            )
            engine_class = Crikk

        print_substep(f"Using TTS engine: {engine_class.__name__}")
        return engine_class()

    def _generate_audio(self, text: str, filepath: str):
        """Generate a single audio file from text."""
        try:
            random_voice = settings.config["settings"]["tts"].get("random_voice", False)

            if str(settings.config["settings"]["tts"]["voice_choice"]).lower() == "googletranslate":
                # GTTS doesn't support random_voice parameter
                self.tts_module.run(text, filepath=filepath)
            else:
                self.tts_module.run(text, filepath=filepath, random_voice=random_voice)
        except Exception as e:
            print_substep(f"  ✗ TTS generation failed: {e}", style="red")
            raise

    def _generate_split_audio(self, text: str, idx: int, final_path: str):
        """Split long text and concat into one audio file.

        For texts longer than the TTS engine's max_chars limit.
        """
        import os

        # Split text into chunks at sentence boundaries
        max_chars = self.tts_module.max_chars
        chunks = [
            x.group().strip()
            for x in re.finditer(
                r" *(((.|\\n){0," + str(max_chars) + r"})(\.|.$))", text
            )
        ]

        if not chunks:
            chunks = [text[:max_chars]]

        part_files = []
        for part_idx, chunk in enumerate(chunks):
            if not chunk or chunk.isspace():
                continue
            part_path = str(self.mp3_dir / f"{idx}-{part_idx}.part.mp3")
            self._generate_audio(chunk, part_path)
            part_files.append(part_path)

        if not part_files:
            return

        # Concat using ffmpeg
        list_path = str(self.mp3_dir / f"{idx}_list.txt")
        with open(list_path, "w") as f:
            for part in part_files:
                f.write(f"file '{Path(part).name}'\n")

        os.system(
            f"ffmpeg -f concat -y -hide_banner -loglevel panic -safe 0 "
            f"-i {list_path} -c copy {final_path}"
        )

        # Cleanup part files
        for part in part_files:
            try:
                os.unlink(part)
            except OSError:
                pass
        try:
            os.unlink(list_path)
        except OSError:
            pass

    def _process_text(self, text: str) -> str:
        """Clean and sanitize text for TTS.

        - Removes lines starting with # (comments in txt files)
        - Sanitizes using existing sanitize_text()
        """
        # Remove comment lines (lines starting with #)
        lines = text.split("\n")
        lines = [line for line in lines if not line.strip().startswith("#")]
        text = " ".join(lines).strip()

        # Remove URLs
        regex_urls = r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"
        text = re.sub(regex_urls, " ", text)

        # Replace newlines with periods for natural speech
        text = text.replace("\n", ". ")

        # Add period at end if missing
        if text and text[-1] not in ".!?":
            text += "."

        # Clean repeated dots
        text = re.sub(r"\.{2,}", ".", text)
        text = re.sub(r"\.\s*\.", ".", text)

        # Use existing sanitize_text for final cleanup
        text = sanitize_text(text)

        return text
