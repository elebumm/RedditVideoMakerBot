import textwrap
import os

from PIL import ImageDraw, ImageFont, Image
from utils import settings
from utils.console import print_step, print_substep


def create_thumbnail(thumbnail, font_family, font_size, font_color, width, height, title):
    font = ImageFont.truetype(font_family + ".ttf", font_size)
    Xaxis = width - (width * 0.2)  # 20% of the width
    sizeLetterXaxis = font_size * 0.5  # 50% of the font size
    XaxisLetterQty = round(Xaxis / sizeLetterXaxis)  # Quantity of letters that can fit in the X axis
    MarginYaxis = height * 0.12  # 12% of the height
    MarginXaxis = width * 0.05  # 5% of the width
    # 1.1 rem
    LineHeight = font_size * 1.1
    # rgb = "255,255,255" transform to list
    rgb = font_color.split(",")
    rgb = (int(rgb[0]), int(rgb[1]), int(rgb[2]))

    arrayTitle = []
    for word in title.split():
        if len(arrayTitle) == 0:
            # colocar a primeira palavra no arrayTitl# put the first word in the arrayTitle
            arrayTitle.append(word)
        else:
            # if the size of arrayTitle is less than qtLetters
            if len(arrayTitle[-1]) + len(word) < XaxisLetterQty:
                arrayTitle[-1] = arrayTitle[-1] + " " + word
            else:
                arrayTitle.append(word)

    draw = ImageDraw.Draw(thumbnail)
    # loop for put the title in the thumbnail
    for i in range(0, len(arrayTitle)):
        # 1.1 rem
        draw.text((MarginXaxis, MarginYaxis + (LineHeight * i)), arrayTitle[i], rgb, font=font)

    return thumbnail

def create_fancy_thumbnail(image, text, text_color, padding, wrap=35):
    print_step(f"Creating fancy thumbnail for: {text}")
    font_title_size = 47
    font = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), font_title_size)
    image_width, image_height = image.size
    lines = textwrap.wrap(text, width=wrap)
    y = (image_height / 2) - (((font.getsize(text)[1] + (len(lines) * padding) / len(lines)) * len(lines)) / 2) + 30
    draw = ImageDraw.Draw(image)

    username_font = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), 30)
    draw.text((205, 825), settings.config["settings"]["channel_name"], font=username_font, fill=text_color, align="left")

    if len(lines) == 3:
        lines = textwrap.wrap(text, width=wrap+10)
        font_title_size = 40
        font = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), font_title_size)
        y = (image_height / 2) - (((font.getsize(text)[1] + (len(lines) * padding) / len(lines)) * len(lines)) / 2) + 35
    elif len(lines) == 4:
        lines = textwrap.wrap(text, width=wrap+10)
        font_title_size = 35
        font = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), font_title_size)
        y = (image_height / 2) - (((font.getsize(text)[1] + (len(lines) * padding) / len(lines)) * len(lines)) / 2) + 40
    elif len(lines) > 4:
        lines = textwrap.wrap(text, width=wrap+10)
        font_title_size = 30
        font = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), font_title_size)
        y = (image_height / 2) - (((font.getsize(text)[1] + (len(lines) * padding) / len(lines)) * len(lines)) / 2) + 30

    for line in lines:
        _, line_height = font.getsize(line)
        draw.text((120, y), line, font=font, fill=text_color, align="left")
        y += line_height + padding

    return image
