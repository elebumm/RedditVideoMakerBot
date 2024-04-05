import json
import re
import textwrap
import os

from PIL import Image, ImageDraw, ImageFont
from rich.progress import track
from TTS.engine_wrapper import process_text
from utils.process_post import process_post


def draw_multiple_line_text(
    image, text, font, text_color, padding, wrap=50, transparent=False
) -> None:
    """
    Draw multiline text over given image
    """
    draw = ImageDraw.Draw(image)
    Fontperm = font.getsize(text)
    image_width, image_height = image.size
    lines = textwrap.wrap(text, width=wrap)
    y = (image_height / 2) - (((Fontperm[1] + (len(lines) * padding) / len(lines)) * len(lines)) / 2)
    
    c = 0
    for line in lines:
        line_width, line_height = font.getsize(line)
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
        if isinstance(text_color, tuple) and len(text_color) == 3:
            draw.text(((image_width - line_width) / 2, y), line, font=font, fill=text_color)
        elif isinstance(text_color, list):
            draw.text(((image_width - line_width) / 2, y), line, font=font, fill=text_color[c % len(text_color)])
            c += 1
        y += line_height + padding


def imagemaker(theme, reddit_obj: dict, txtclr, padding=5, transparent=False) -> None:
    """
    Render Images for video
    """
    # return
    title = process_text(reddit_obj["thread_title"], False)
    texts = process_post(reddit_obj["thread_post"])
    id = re.sub(r"[^\w\s-]", "", reddit_obj["thread_id"])

    if transparent:
        font = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), 100)
        tfont = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), 100)
    else:
        tfont = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), 100)  # for title
        font = ImageFont.truetype(os.path.join("fonts", "Roboto-Regular.ttf"), 100)
    size = (1920, 1080)

    image = Image.new("RGBA", size, theme)

    # for title
    draw_multiple_line_text(image, title, tfont, txtclr, padding, wrap=30, transparent=transparent)

    image.save(f"assets/temp/{id}/png/title.png")

    weights = dict()
    for idx, text in track(enumerate(texts), "Rendering Image"):
        if isinstance(text, tuple):
            total_text_length = sum(len(t) for t in text)
            for i in range(len(text)):
                sub_text = text[i]
                image = Image.new("RGBA", size, theme)
                sub_text = process_text(sub_text, False)
                draw_multiple_line_text(image, sub_text, font, txtclr, padding, wrap=30, transparent=transparent)
                image.save(f"assets/temp/{id}/png/img{idx}-{i+1}.png")
                weights[f"{idx}-{i+1}"] = round(len(sub_text) / total_text_length, 3)
        else:
            image = Image.new("RGBA", size, theme)
            text = process_text(text, False)
            draw_multiple_line_text(image, text, font, txtclr, padding, wrap=30, transparent=transparent)
            image.save(f"assets/temp/{id}/png/img{idx}.png")
    
    with open(f"assets/temp/{id}/weights.json", 'w') as file:
        file.write(json.dumps(weights, indent=4))
