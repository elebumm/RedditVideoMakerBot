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


def draw_highlighted_text(
    image, text, font, padding, wrap=50, highlighted_word_index=-1
) -> None:
    """
    Draw text with white fill, black outline, and yellow inner outline (layered effect)
    """
    draw = ImageDraw.Draw(image)
    image_width, image_height = image.size
    
    # Split text into words and wrap
    words = text.split()
    lines = []
    current_line = []
    current_line_width = 0
    
    for word in words:
        word_width, _ = getsize(font, word + " ")
        if current_line_width + word_width <= image_width - 40:  # 20px padding on each side
            current_line.append(word)
            current_line_width += word_width
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_line_width = word_width
    
    if current_line:
        lines.append(" ".join(current_line))
    
    # Calculate total height
    line_height = getheight(font, "A")
    total_height = len(lines) * line_height + (len(lines) - 1) * padding
    y_start = (image_height - total_height) // 2
    
    # Draw each line
    word_index = 0
    for line_idx, line in enumerate(lines):
        line_words = line.split()
        x = (image_width - getsize(font, line)[0]) // 2
        y = y_start + line_idx * (line_height + padding)
        
        # Draw each word in the line
        for word in line_words:
            word_width, _ = getsize(font, word + " ")
            
            # Determine color based on highlighting
            if highlighted_word_index >= 0 and word_index == highlighted_word_index:
                text_color = (255, 255, 0)  # Bright yellow for highlighted word
                inner_outline_color = (255, 255, 255)  # White inner outline for highlighted word
            else:
                text_color = (255, 255, 255)  # White for other words
                inner_outline_color = (255, 255, 0)  # Yellow inner outline for non-highlighted words
            
            # Draw black outer outline (thickest)
            outer_stroke_width = 4
            for dx in range(-outer_stroke_width, outer_stroke_width + 1):
                for dy in range(-outer_stroke_width, outer_stroke_width + 1):
                    if dx != 0 or dy != 0:  # Skip the center pixel
                        draw.text(
                            (x + dx, y + dy),
                            word,
                            font=font,
                            fill=(0, 0, 0)  # Black outer outline
                        )
            
            # Draw yellow inner outline (medium thickness)
            inner_stroke_width = 2
            for dx in range(-inner_stroke_width, inner_stroke_width + 1):
                for dy in range(-inner_stroke_width, inner_stroke_width + 1):
                    if dx != 0 or dy != 0:  # Skip the center pixel
                        draw.text(
                            (x + dx, y + dy),
                            word,
                            font=font,
                            fill=inner_outline_color  # Yellow inner outline
                        )
            
            # Draw the main text (white or yellow)
            draw.text((x, y), word, font=font, fill=text_color)
            
            x += word_width
            word_index += 1


def create_highlighted_captions(theme, reddit_obj: dict, padding=5) -> None:
    """
    Create captions with white text and black stroke (highlighted style)
    """
    texts = reddit_obj["thread_post"]
    id = re.sub(r"[^\w\s-]", "", reddit_obj["thread_id"])

    # Use the actual video resolution from config
    W = int(settings.config["settings"]["resolution_w"])
    H = int(settings.config["settings"]["resolution_h"])
    size = (W, H)
    
    # Use larger, bolder font for better visibility like the screenshot
    font_size = min(80, max(40, H // 25))  # Larger font size for better impact
    font = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), font_size)

    for idx, text in track(enumerate(texts), "Creating Highlighted Captions"):
        text = process_text(text, False)
        
        # Create transparent background
        image = Image.new("RGBA", size, (0, 0, 0, 0))
        
        # Draw highlighted text with white text and black stroke
        draw_highlighted_text(
            image, 
            text, 
            font, 
            padding=padding, 
            wrap=25,  # Tighter wrap for better text flow
            highlighted_word_index=-1  # No specific word highlighted, just the style
        )
        
        # Save the image
        image.save(f"assets/temp/{id}/png/img{idx}.png")


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
