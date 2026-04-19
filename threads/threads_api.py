"""Threads API integration for fetching posts and replies.

Uses Meta's Threads Graph API (https://developers.facebook.com/docs/threads).
Requires an access token with 'threads_basic' and 'threads_read_replies' permissions.
"""

import json
import re
from pathlib import Path
from typing import Optional

import requests

from utils import settings
from utils.console import print_step, print_substep
from utils.voice import sanitize_text

THREADS_API_BASE = "https://graph.threads.net/v1.0"
VIDEOS_DONE_FILE = "./video_creation/data/videos.json"


def _api_get(path: str, access_token: str, params: Optional[dict] = None) -> dict:
    """Call Threads Graph API GET endpoint."""
    params = dict(params or {})
    params["access_token"] = access_token
    url = f"{THREADS_API_BASE}/{path.lstrip('/')}"
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def _extract_thread_id(url_or_id: str) -> str:
    """Extract thread ID from a threads.net URL or return as-is if already an ID."""
    match = re.search(r"/post/([A-Za-z0-9_-]+)", url_or_id)
    return match.group(1) if match else url_or_id


def _fetch_thread_details(thread_id: str, access_token: str) -> dict:
    fields = "id,text,username,timestamp,permalink,media_type,is_quote_post"
    return _api_get(thread_id, access_token, {"fields": fields})


def _fetch_replies(thread_id: str, access_token: str, limit: int = 50) -> list[dict]:
    fields = "id,text,username,timestamp,permalink"
    try:
        data = _api_get(
            f"{thread_id}/replies",
            access_token,
            {"fields": fields, "limit": limit, "reverse": "false"},
        )
        return data.get("data", [])
    except requests.HTTPError:
        return []


def _fetch_user_threads(access_token: str, limit: int = 25) -> list[dict]:
    fields = "id,text,username,timestamp,permalink,media_type"
    data = _api_get(
        "me/threads",
        access_token,
        {"fields": fields, "limit": limit},
    )
    return data.get("data", [])


def _is_valid_reply(text: str, min_len: int, max_len: int, blocked_words: list[str]) -> bool:
    if not text or not text.strip():
        return False
    if len(text) < min_len or len(text) > max_len:
        return False
    lower = text.lower()
    if any(w.strip().lower() in lower for w in blocked_words if w.strip()):
        return False
    if not sanitize_text(text):
        return False
    return True


def get_threads_posts(POST_URL: Optional[str] = None) -> dict:
    """Fetches a Threads post + replies. Returns a dict compatible with the video pipeline.

    Args:
        POST_URL: Optional specific thread URL or ID. If not provided, picks from
                  the authenticated user's recent threads.

    Returns:
        A dict with keys: thread_url, thread_title, thread_id, is_nsfw, comments,
        optionally thread_post (for storymode).
    """
    print_step("Fetching Threads post...")

    try:
        access_token = settings.config["threads"]["creds"]["access_token"]
    except KeyError:
        raise RuntimeError(
            "Missing Threads access_token in config.toml under [threads.creds]"
        )

    if not access_token:
        raise RuntimeError("Threads access_token is empty. Set it in config.toml.")

    thread_cfg = settings.config["threads"]["thread"]
    min_len = int(thread_cfg.get("min_comment_length", 10))
    max_len = int(thread_cfg.get("max_comment_length", 500))
    blocked_words = [
        w for w in str(thread_cfg.get("blocked_words", "")).split(",") if w.strip()
    ]

    target = POST_URL or thread_cfg.get("post_id") or ""

    if target:
        thread_id = _extract_thread_id(target)
        submission = _fetch_thread_details(thread_id, access_token)
    else:
        print_substep("No post_id specified. Fetching authenticated user's recent threads.")
        user_threads = _fetch_user_threads(access_token, limit=25)
        if not user_threads:
            raise RuntimeError("No threads found for authenticated user.")
        submission = user_threads[0]
        thread_id = submission["id"]

    text = submission.get("text", "")
    title = (text[:100] + "...") if len(text) > 100 else text
    permalink = submission.get("permalink", f"https://www.threads.net/@unknown/post/{thread_id}")

    print_substep(f"Thread: {title}", style="bold green")
    print_substep(f"URL: {permalink}", style="bold blue")

    content = {
        "thread_url": permalink,
        "thread_title": title or f"Thread {thread_id}",
        "thread_id": thread_id,
        "is_nsfw": False,
        "comments": [],
    }

    if settings.config["settings"]["storymode"]:
        content["thread_post"] = text
    else:
        replies = _fetch_replies(thread_id, access_token, limit=50)
        for reply in replies:
            body = reply.get("text", "")
            if not _is_valid_reply(body, min_len, max_len, blocked_words):
                continue
            content["comments"].append({
                "comment_body": body,
                "comment_url": reply.get("permalink", ""),
                "comment_id": reply["id"],
            })

    print_substep(
        f"Got {len(content['comments'])} valid replies.",
        style="bold green",
    )

    if _is_already_done(thread_id) and not target:
        print_substep("Thread already processed. Fetch skipped.", style="yellow")
        raise RuntimeError("Thread already processed. Set post_id to force reprocess.")

    return content


def _is_already_done(thread_id: str) -> bool:
    path = Path(VIDEOS_DONE_FILE)
    if not path.exists():
        return False
    try:
        done = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    return any(v.get("id") == thread_id for v in done)
