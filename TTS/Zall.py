import base64
import json
import os
import random
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

from utils import settings
from utils.console import print_substep

# Load environment variables from .env file
load_dotenv()

ZALL_API_URL = os.getenv("ZALL_API_URL", "")
ZALL_BASE_URL = os.getenv("ZALL_BASE_URL", "")
ZALL_JWT_TOKEN = os.getenv("ZALL_JWT_TOKEN", "")
VOICES_FILE = Path(__file__).resolve().parent.parent / "config" / "zall_voices.json"
MAX_RETRIES = 3
RATE_LIMIT_WAIT = 20


def _load_voices() -> list[dict]:
    try:
        with open(VOICES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print_substep(f"Warning: Could not load voices from {VOICES_FILE}: {e}", style="yellow")
        return []


class Zall:
    # Load list of User‑Agent strings for random header
    _user_agents = None

    def _load_user_agents(self) -> list[str]:
        """Read user_agents.json and cache result.
        Returns empty list on failure and logs warning.
        """
        if self._user_agents is not None:
            return self._user_agents
        try:
            agents_path = Path(__file__).resolve().parent.parent / "config" / "user_agents.json"
            with open(agents_path, "r", encoding="utf-8") as f:
                self._user_agents = json.load(f)
        except Exception as e:
            print_substep(f"Warning: Could not load user agents: {e}", style="yellow")
            self._user_agents = []
        return self._user_agents

    def _pick_user_agent(self) -> str:
        """Return a random User‑Agent string from loaded list.
        Falls back to generic UA on empty list.
        """
        agents = self._load_user_agents()
        if agents:
            return random.choice(agents)
        return "Mozilla/5.0"

    def __init__(self):
        self.max_chars = 2500
        self.voices = _load_voices()

    def run(self, text, filepath, random_voice: bool = False):
        voice = self._pick_voice(random_voice)
        audio_bytes = self._call_api(text, voice["id"])
        with open(filepath, "wb") as f:
            f.write(audio_bytes)

    def randomvoice(self) -> dict:
        lang = settings.config["settings"]["tts"].get("zall_lang", "vi")
        filtered = [v for v in self.voices if v["lang"] == lang]
        if not filtered:
            filtered = self.voices
        return random.choice(filtered)

    def _pick_voice(self, random_voice: bool) -> dict:
        if random_voice:
            return self.randomvoice()
        lang = settings.config["settings"]["tts"].get("zall_lang", "vi")
        gender = settings.config["settings"]["tts"].get("zall_gender", "random")
        candidates = [v for v in self.voices if v["lang"] == lang]
        if gender != "random":
            candidates = [v for v in candidates if v["gender"] == gender]
        if not candidates:
            candidates = self.voices
        return random.choice(candidates)

    def _call_api(self, text: str, voice_id: int) -> bytes:
        payload = {
            "segments": [
                {
                    "voiceId": voice_id,
                    "text": text
                }
            ],
            "useNaturalVoice": settings.config["settings"]["tts"].get("zall_natural_voice", False),
            "enableBrandKeywords": settings.config["settings"]["tts"].get("zall_enable_brand_keywords", False),
        }
        headers = {
            "cache-control": "no-cache",
            "content-type": "application/json",
            "accept": "*/*",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,vi;q=0.7", # important
            "sec-fetch-mode": "cors", # important
            "sec-fetch-site": "same-origin", # important
            "Cookie": f"auth_token={ZALL_JWT_TOKEN}", # important
            "user-agent": self._pick_user_agent(), # important
        }

        for attempt in range(MAX_RETRIES):
            resp = requests.post(ZALL_API_URL, json=payload, headers=headers, stream=True)
            audio_bytes = b""

            for line in resp.iter_lines():
                if not line:
                    continue

                try:
                    event = json.loads(line.decode("utf-8"))
                except json.JSONDecodeError:
                    continue

                status = event.get("status")
                if status == "audio_chunk":
                    audio_bytes += base64.b64decode(event["chunk"])
                elif status == "error":
                    print_substep(
                        f"  Rate limited, waiting {RATE_LIMIT_WAIT}s... (attempt {attempt + 1}/{MAX_RETRIES})",
                        style="yellow",
                    )
                    time.sleep(RATE_LIMIT_WAIT)
                    break
                elif status == "done":
                    if not audio_bytes:
                        raise RuntimeError("Zall TTS completed without audio chunks")
                    return audio_bytes
            else:
                raise RuntimeError("Zall TTS response ended before completion")

        raise RuntimeError(f"Zall TTS failed after {MAX_RETRIES} retries (rate limited)")
