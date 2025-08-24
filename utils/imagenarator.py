import os
import re
import textwrap

from PIL import Image, ImageDraw, ImageFont
from rich.progress import track

from TTS.engine_wrapper import process_text
from utils.fonts import getheight, getsize
from utils import settings


def calculate_text_dimensions(text, font, padding, wrap=50):
    """
    Calculate the dimensions needed for text with given font and padding
    """
    lines = textwrap.wrap(text, width=wrap)
    max_line_width = 0
    total_height = 0
    
    for line in lines:
        line_width, line_height = getsize(font, line)
        max_line_width = max(max_line_width, line_width)
        total_height += line_height
    
    # Add padding between lines
    if len(lines) > 1:
        total_height += (len(lines) - 1) * padding
    
    # Add minimal padding around the text
    padding_around = 10
    return max_line_width + (padding_around * 2), total_height + (padding_around * 2)


def draw_multiple_line_text(
    image, text, font, text_color, padding, wrap=50, transparent=False
) -> None:
    """
    Draw multiline text over given image
    """
    draw = ImageDraw.Draw(image)
    font_height = getheight(font, text)
    image_width, image_height = image.size
    lines = textwrap.wrap(text, width=wrap)
    y = (image_height / 2) - (((font_height + (len(lines) * padding) / len(lines)) * len(lines)) / 2)
    for line in lines:
        line_width, line_height = getsize(font, line)
        if transparent:
            shadowcolor = "black"
            for i in range(1, 5):
                draw.text(
                    ((image_width - line_width) / 2 - i, y - i),
                    line,
                    font=font,
                    fill=shadowcolor,
                )
                draw.text(
                    ((image_width - line_width) / 2 + i, y - i),
                    line,
                    font=font,
                    fill=shadowcolor,
                )
                draw.text(
                    ((image_width - line_width) / 2 - i, y + i),
                    line,
                    font=font,
                    fill=shadowcolor,
                )
                draw.text(
                    ((image_width - line_width) / 2 + i, y + i),
                    line,
                    font=font,
                    fill=shadowcolor,
                )
        draw.text(((image_width - line_width) / 2, y), line, font=font, fill=text_color)
        y += line_height + padding


def imagemaker(theme, reddit_obj: dict, txtclr, padding=5, transparent=False) -> None:
    """
    Render Images for video
    """
    texts = reddit_obj["thread_post"]
    id = re.sub(r"[^\w\s-]", "", reddit_obj["thread_id"])

    # Use the actual video resolution from config instead of fixed landscape size
    W = int(settings.config["settings"]["resolution_w"])
    H = int(settings.config["settings"]["resolution_h"])
    size = (W, H)
    
    # Adjust font size based on video resolution for better readability
    # For 9:16 portrait videos, use smaller font size to fit better in the compact background
    if transparent:
        font_size = min(50, max(25, H // 50))  # Smaller font size for compact background
        font = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), font_size)
    else:
        font_size = min(50, max(25, H // 50))  # Smaller font size for compact background
        font = ImageFont.truetype(os.path.join("fonts", "Roboto-Regular.ttf"), font_size)

    image = Image.new("RGBA", size, theme)

    for idx, text in track(enumerate(texts), "Rendering Image"):
        text = process_text(text, False)
        # Adjust text wrapping based on video width for better fit
        wrap_width = max(20, min(35, W // 60))  # More balanced wrap width to fill the overlay better
        
        # Calculate the dimensions needed for this text
        text_width, text_height = calculate_text_dimensions(text, font, padding=2, wrap=wrap_width)
        
        # Create an image that's only as big as the text content
        image = Image.new("RGBA", (text_width, text_height), theme)
        
        # Use smaller padding to make text lines closer together and fill more vertical space
        draw_multiple_line_text(image, text, font, txtclr, padding=2, wrap=wrap_width, transparent=transparent)
        image.save(f"assets/temp/{id}/png/img{idx}.png")
