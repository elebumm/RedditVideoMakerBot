"""
Preflight Access-Token Checker — chạy trước khi pipeline bắt đầu.

Kiểm tra:
1. access_token có được cấu hình trong config.toml không.
2. Token có hợp lệ trên Threads API (/me endpoint) không.
3. Nếu token hết hạn → tự động thử refresh.
4. user_id trong config khớp với user sở hữu token không.

Usage:
    # Gọi trực tiếp:
    python -m utils.check_token

    # Hoặc import trong code:
    from utils.check_token import preflight_check
    preflight_check()          # raises SystemExit on failure
"""

import sys
from typing import Optional

import requests

from utils import settings
from utils.console import print_step, print_substep

THREADS_API_BASE = "https://graph.threads.net/v1.0"
_REQUEST_TIMEOUT = 15  # seconds – preflight should be fast


class TokenCheckError(Exception):
    """Raised when the access-token preflight fails."""


def _call_me_endpoint(access_token: str) -> dict:
    """GET /me?fields=id,username&access_token=… with minimal retry."""
    url = f"{THREADS_API_BASE}/me"
    params = {
        "fields": "id,username",
        "access_token": access_token,
    }
    response = requests.get(url, params=params, timeout=_REQUEST_TIMEOUT)

    # HTTP-level errors
    if response.status_code == 401:
        raise TokenCheckError(
            "Access token không hợp lệ hoặc đã hết hạn (HTTP 401).\n"
            "→ Cập nhật [threads.creds] access_token trong config.toml."
        )
    if response.status_code == 403:
        raise TokenCheckError(
            "Token thiếu quyền (HTTP 403).\n"
            "→ Đảm bảo token có quyền threads_basic_read trong Meta Developer Portal."
        )
    response.raise_for_status()

    data = response.json()

    # Graph API may return 200 with an error body
    if "error" in data:
        err = data["error"]
        msg = err.get("message", "Unknown error")
        code = err.get("code", 0)
        raise TokenCheckError(f"Threads API trả về lỗi: {msg} (code={code})")

    return data


def _try_refresh(access_token: str) -> Optional[str]:
    """Attempt to refresh a long-lived Threads token.

    Returns new token string, or None if refresh is not possible.
    """
    url = f"{THREADS_API_BASE}/refresh_access_token"
    try:
        resp = requests.get(
            url,
            params={
                "grant_type": "th_refresh_token",
                "access_token": access_token,
            },
            timeout=_REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            return None
        return data.get("access_token") or None
    except requests.RequestException:
        return None


def preflight_check() -> None:
    """Validate the Threads access token configured in *config.toml*.

    On success, prints a confirmation and returns normally.
    On failure, prints actionable diagnostics and raises ``SystemExit(1)``.
    """
    print_step("🔑 Kiểm tra access token trước khi chạy...")

    # --- 1. Check config values exist -----------------------------------
    try:
        threads_creds = settings.config["threads"]["creds"]
        access_token: str = threads_creds.get("access_token", "").strip()
        user_id: str = threads_creds.get("user_id", "").strip()
    except (KeyError, TypeError):
        print_substep(
            "❌ Thiếu cấu hình [threads.creds] trong config.toml.\n"
            "   Cần có access_token và user_id.",
            style="bold red",
        )
        sys.exit(1)

    if not access_token:
        print_substep(
            "❌ access_token trống trong config.toml!\n"
            "   Lấy token tại: https://developers.facebook.com/docs/threads/get-started",
            style="bold red",
        )
        sys.exit(1)

    if not user_id:
        print_substep(
            "❌ user_id trống trong config.toml!\n"
            "   Lấy user_id bằng cách gọi /me với access token.",
            style="bold red",
        )
        sys.exit(1)

    # --- 2. Validate token via /me endpoint -----------------------------
    try:
        me_data = _call_me_endpoint(access_token)
    except TokenCheckError as exc:
        # Token invalid → try refresh
        print_substep(
            f"⚠️ Token hiện tại không hợp lệ: {exc}\n" "   Đang thử refresh token...",
            style="bold yellow",
        )
        new_token = _try_refresh(access_token)
        if new_token:
            try:
                me_data = _call_me_endpoint(new_token)
                access_token = new_token
                # Update in-memory config so downstream code uses the new token
                settings.config["threads"]["creds"]["access_token"] = new_token
                print_substep("✅ Token đã được refresh thành công!", style="bold green")
            except TokenCheckError as inner:
                print_substep(
                    f"❌ Token mới sau refresh vẫn lỗi: {inner}\n"
                    "   Vui lòng lấy token mới từ Meta Developer Portal:\n"
                    "   https://developers.facebook.com/docs/threads/get-started",
                    style="bold red",
                )
                sys.exit(1)
        else:
            print_substep(
                "❌ Không thể refresh token.\n"
                "   Vui lòng lấy token mới từ Meta Developer Portal:\n"
                "   https://developers.facebook.com/docs/threads/get-started",
                style="bold red",
            )
            sys.exit(1)
    except requests.RequestException as exc:
        print_substep(
            f"❌ Lỗi kết nối khi kiểm tra token: {exc}\n" "   Kiểm tra kết nối mạng và thử lại.",
            style="bold red",
        )
        sys.exit(1)

    # --- 3. Cross-check user_id ----------------------------------------
    api_user_id = me_data.get("id", "")
    api_username = me_data.get("username", "N/A")

    if api_user_id and api_user_id != user_id:
        print_substep(
            f"⚠️ user_id trong config ({user_id}) khác với user sở hữu token ({api_user_id}).\n"
            "   Nếu bạn muốn lấy threads của chính mình, hãy cập nhật user_id trong config.toml.\n"
            "   Đang tiếp tục với token hiện tại...",
            style="bold yellow",
        )

    print_substep(
        f"✅ Access token hợp lệ — @{api_username} (ID: {api_user_id})",
        style="bold green",
    )


# Allow running standalone: python -m utils.check_token
if __name__ == "__main__":
    from pathlib import Path

    directory = Path().absolute()
    settings.check_toml(
        f"{directory}/utils/.config.template.toml",
        f"{directory}/config.toml",
    )
    preflight_check()
    print_step("🎉 Tất cả kiểm tra đều OK — sẵn sàng chạy!")
