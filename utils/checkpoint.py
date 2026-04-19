import json
import time
from pathlib import Path
from typing import Any, Optional

from utils.console import print_step, print_substep

CHECKPOINT_DIR = Path("assets/temp")


def _checkpoint_path(reddit_id: str) -> Path:
    return CHECKPOINT_DIR / reddit_id / "checkpoint.json"


def save_checkpoint(reddit_id: str, step: str, data: dict[str, Any]) -> None:
    path = _checkpoint_path(reddit_id)
    path.parent.mkdir(parents=True, exist_ok=True)

    checkpoint = load_checkpoint(reddit_id) or {}
    checkpoint["reddit_id"] = reddit_id
    checkpoint["last_step"] = step
    checkpoint["updated_at"] = time.time()
    checkpoint.setdefault("completed_steps", [])
    if step not in checkpoint["completed_steps"]:
        checkpoint["completed_steps"].append(step)
    checkpoint[step] = data

    path.write_text(json.dumps(checkpoint, indent=2, default=str))


def load_checkpoint(reddit_id: str) -> Optional[dict]:
    path = _checkpoint_path(reddit_id)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def is_step_done(reddit_id: str, step: str) -> bool:
    cp = load_checkpoint(reddit_id)
    if not cp:
        return False
    return step in cp.get("completed_steps", [])


def get_step_data(reddit_id: str, step: str) -> Optional[dict]:
    cp = load_checkpoint(reddit_id)
    if not cp:
        return None
    return cp.get(step)


def clear_checkpoint(reddit_id: str) -> None:
    path = _checkpoint_path(reddit_id)
    if path.exists():
        path.unlink()


def print_resume_status(reddit_id: str) -> None:
    cp = load_checkpoint(reddit_id)
    if not cp:
        return
    done = cp.get("completed_steps", [])
    print_substep(f"Resuming from checkpoint. Completed steps: {', '.join(done)}", style="bold yellow")


PIPELINE_STEPS = [
    "fetch_reddit",
    "generate_tts",
    "take_screenshots",
    "download_background",
    "chop_background",
    "make_final_video",
]


def run_step(reddit_id: str, step: str, func, *args, max_retries: int = 3, **kwargs) -> Any:
    if is_step_done(reddit_id, step):
        data = get_step_data(reddit_id, step)
        print_substep(f"Step '{step}' already done. Skipping.", style="bold green")
        return data.get("result") if data else None

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            if attempt > 1:
                print_substep(f"Retry {attempt}/{max_retries} for step '{step}'...", style="bold yellow")
            result = func(*args, **kwargs)
            save_checkpoint(reddit_id, step, {"result": result})
            print_substep(f"Step '{step}' completed successfully.", style="bold green")
            return result
        except KeyboardInterrupt:
            raise
        except Exception as e:
            last_error = e
            print_substep(f"Step '{step}' failed (attempt {attempt}/{max_retries}): {e}", style="bold red")
            if attempt < max_retries:
                wait = 2 ** attempt
                print_substep(f"Waiting {wait}s before retry...", style="yellow")
                time.sleep(wait)

    print_step(f"Step '{step}' failed after {max_retries} attempts.")
    save_checkpoint(reddit_id, f"{step}_failed", {"error": str(last_error)})
    raise last_error
