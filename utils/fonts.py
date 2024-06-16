from PIL.ImageFont import FreeTypeFont, ImageFont


def getsize(font: ImageFont | FreeTypeFont, text: str):
    left, top, right, bottom = font.getbbox(text)
    width = right - left
    height = bottom - top
    return width, height


def getheight(font: ImageFont | FreeTypeFont, text: str):
    _, height = getsize(font, text)
    return height
