"""
Threads Screenshot Generator - Tạo hình ảnh giả lập giao diện Threads.

Sử dụng Pillow để render hình ảnh thay vì chụp screenshot từ trình duyệt,
vì Threads không có giao diện web tĩnh dễ chụp như Reddit.
"""

import os
import re
import textwrap
from pathlib import Path
from typing import Dict, Final, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont
from rich.progress import track

from utils import settings
from utils.console import print_step, print_substep


# Threads color themes
THEMES = {
    "dark": {
        "bg_color": (0, 0, 0),
        "card_bg": (30, 30, 30),
        "text_color": (255, 255, 255),
        "secondary_text": (140, 140, 140),
        "border_color": (50, 50, 50),
        "accent_color": (0, 149, 246),  # Threads blue
        "reply_line": (60, 60, 60),
    },
    "light": {
        "bg_color": (255, 255, 255),
        "card_bg": (255, 255, 255),
        "text_color": (0, 0, 0),
        "secondary_text": (130, 130, 130),
        "border_color": (219, 219, 219),
        "accent_color": (0, 149, 246),
        "reply_line": (200, 200, 200),
    },
}


def _get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Load font hỗ trợ tiếng Việt."""
    font_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fonts")
    if bold:
        font_path = os.path.join(font_dir, "Roboto-Bold.ttf")
    else:
        font_path = os.path.join(font_dir, "Roboto-Medium.ttf")

    try:
        return ImageFont.truetype(font_path, size)
    except (OSError, IOError):
        return ImageFont.load_default()


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
    """Wrap text to fit within max_width pixels."""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = font.getbbox(test_line)
        if bbox[2] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines if lines else [""]


def _draw_avatar(draw: ImageDraw.Draw, x: int, y: int, size: int, color: Tuple[int, ...]):
    """Vẽ avatar tròn placeholder."""
    draw.ellipse([x, y, x + size, y + size], fill=color)
    # Vẽ chữ cái đầu trong avatar
    font = _get_font(size // 2, bold=True)
    draw.text(
        (x + size // 4, y + size // 6),
        "T",
        fill=(255, 255, 255),
        font=font,
    )


def create_thread_post_image(
    thread_obj: dict,
    theme_name: str = "dark",
    width: int = 1080,
) -> Image.Image:
    """Tạo hình ảnh cho bài viết Threads chính (title/post).

    Args:
        thread_obj: Thread object chứa thông tin bài viết.
        theme_name: Theme name ("dark" hoặc "light").
        width: Chiều rộng hình ảnh.

    Returns:
        PIL Image object.
    """
    theme = THEMES.get(theme_name, THEMES["dark"])

    padding = 40
    content_width = width - (padding * 2)
    avatar_size = 60

    # Fonts
    username_font = _get_font(28, bold=True)
    body_font = _get_font(32)
    meta_font = _get_font(22)

    author = thread_obj.get("thread_author", "@user")
    text = thread_obj.get("thread_title", thread_obj.get("thread_post", ""))

    # Tính chiều cao
    text_lines = _wrap_text(text, body_font, content_width - avatar_size - 30)
    line_height = 42
    text_height = len(text_lines) * line_height

    total_height = padding + avatar_size + 20 + text_height + 60 + padding

    # Tạo image
    img = Image.new("RGBA", (width, total_height), theme["bg_color"])
    draw = ImageDraw.Draw(img)

    y_cursor = padding

    # Avatar
    _draw_avatar(draw, padding, y_cursor, avatar_size, theme["accent_color"])

    # Username
    draw.text(
        (padding + avatar_size + 15, y_cursor + 5),
        author,
        fill=theme["text_color"],
        font=username_font,
    )

    # Timestamp
    draw.text(
        (padding + avatar_size + 15, y_cursor + 35),
        "🧵 Threads",
        fill=theme["secondary_text"],
        font=meta_font,
    )

    y_cursor += avatar_size + 20

    # Thread line (vertical line from avatar to content)
    line_x = padding + avatar_size // 2
    draw.line(
        [(line_x, padding + avatar_size + 5), (line_x, y_cursor - 5)],
        fill=theme["reply_line"],
        width=3,
    )

    # Body text
    for line in text_lines:
        draw.text(
            (padding + 10, y_cursor),
            line,
            fill=theme["text_color"],
            font=body_font,
        )
        y_cursor += line_height

    # Interaction bar
    y_cursor += 20
    icons = "❤️  💬  🔄  ✈️"
    draw.text(
        (padding + 10, y_cursor),
        icons,
        fill=theme["secondary_text"],
        font=meta_font,
    )

    return img


def create_comment_image(
    comment: dict,
    index: int,
    theme_name: str = "dark",
    width: int = 1080,
) -> Image.Image:
    """Tạo hình ảnh cho một reply/comment trên Threads.

    Args:
        comment: Comment dict.
        index: Số thứ tự comment.
        theme_name: Theme name.
        width: Chiều rộng hình ảnh.

    Returns:
        PIL Image object.
    """
    theme = THEMES.get(theme_name, THEMES["dark"])

    padding = 40
    content_width = width - (padding * 2)
    avatar_size = 50

    # Fonts
    username_font = _get_font(24, bold=True)
    body_font = _get_font(30)
    meta_font = _get_font(20)

    author = comment.get("comment_author", f"@user{index}")
    text = comment.get("comment_body", "")

    # Tính chiều cao
    text_lines = _wrap_text(text, body_font, content_width - avatar_size - 30)
    line_height = 40
    text_height = len(text_lines) * line_height

    total_height = padding + avatar_size + 15 + text_height + 40 + padding

    # Tạo image
    img = Image.new("RGBA", (width, total_height), theme["bg_color"])
    draw = ImageDraw.Draw(img)

    y_cursor = padding

    # Reply line at top
    draw.line(
        [(padding, 0), (padding, y_cursor)],
        fill=theme["reply_line"],
        width=2,
    )

    # Avatar (smaller for comments)
    colors = [
        (88, 101, 242),   # Blue
        (237, 66, 69),    # Red
        (87, 242, 135),   # Green
        (254, 231, 92),   # Yellow
        (235, 69, 158),   # Pink
    ]
    avatar_color = colors[index % len(colors)]
    _draw_avatar(draw, padding, y_cursor, avatar_size, avatar_color)

    # Username
    draw.text(
        (padding + avatar_size + 12, y_cursor + 5),
        author,
        fill=theme["text_color"],
        font=username_font,
    )

    # Time indicator
    draw.text(
        (padding + avatar_size + 12, y_cursor + 30),
        "Trả lời",
        fill=theme["secondary_text"],
        font=meta_font,
    )

    y_cursor += avatar_size + 15

    # Body text
    for line in text_lines:
        draw.text(
            (padding + 10, y_cursor),
            line,
            fill=theme["text_color"],
            font=body_font,
        )
        y_cursor += line_height

    # Bottom separator
    y_cursor += 10
    draw.line(
        [(padding, y_cursor), (width - padding, y_cursor)],
        fill=theme["border_color"],
        width=1,
    )

    return img


def get_screenshots_of_threads_posts(thread_object: dict, screenshot_num: int):
    """Tạo screenshots cho bài viết Threads.

    Thay thế get_screenshots_of_reddit_posts() cho Threads.

    Args:
        thread_object: Thread object từ threads_client.py.
        screenshot_num: Số lượng screenshots cần tạo.
    """
    W: Final[int] = int(settings.config["settings"]["resolution_w"])
    H: Final[int] = int(settings.config["settings"]["resolution_h"])
    theme: str = settings.config["settings"].get("theme", "dark")
    storymode: bool = settings.config["settings"].get("storymode", False)

    print_step("Đang tạo hình ảnh cho bài viết Threads...")

    thread_id = re.sub(r"[^\w\s-]", "", thread_object["thread_id"])
    Path(f"assets/temp/{thread_id}/png").mkdir(parents=True, exist_ok=True)

    # Tạo hình ảnh cho bài viết chính (title)
    title_img = create_thread_post_image(
        thread_object,
        theme_name=theme if theme in THEMES else "dark",
        width=W,
    )
    title_img.save(f"assets/temp/{thread_id}/png/title.png")
    print_substep("Đã tạo hình ảnh tiêu đề", style="bold green")

    if storymode:
        # Story mode - chỉ cần 1 hình cho toàn bộ nội dung
        story_img = create_thread_post_image(
            {
                "thread_author": thread_object.get("thread_author", "@user"),
                "thread_title": thread_object.get("thread_post", ""),
            },
            theme_name=theme if theme in THEMES else "dark",
            width=W,
        )
        story_img.save(f"assets/temp/{thread_id}/png/story_content.png")
    else:
        # Comment mode - tạo hình cho từng reply
        comments = thread_object.get("comments", [])[:screenshot_num]
        for idx, comment in enumerate(
            track(comments, "Đang tạo hình ảnh replies...")
        ):
            if idx >= screenshot_num:
                break

            comment_img = create_comment_image(
                comment,
                index=idx,
                theme_name=theme if theme in THEMES else "dark",
                width=W,
            )
            comment_img.save(f"assets/temp/{thread_id}/png/comment_{idx}.png")

    print_substep("Đã tạo tất cả hình ảnh thành công! ✅", style="bold green")
