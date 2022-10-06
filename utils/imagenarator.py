from PIL import Image, ImageDraw,ImageFont 
import textwrap
import re

def draw_multiple_line_text(image, text, font, text_color,padding):
    '''
    Draw multiline text over given image
    '''
    draw = ImageDraw.Draw(image)
    Fontperm= font.getsize(text)
    image_width, image_height = image.size
    lines = textwrap.wrap(text, width=50)
    y=(image_height/2)-(((Fontperm[1]+(len(lines)*padding)/len(lines))*len(lines))/2) #dont touch it
    for line in lines:
        line_width, line_height = font.getsize(line)
        draw.text(((image_width - line_width) / 2, y), 
                    line, font=font, fill=text_color)
        y += line_height + padding


def imagemaker(text,
                reddit_obj,
                idx='NoName',
                padding=5
                ):
    id = re.sub(r"[^\w\s-]", "", reddit_obj["thread_id"])
    font=ImageFont.truetype("arial.ttf", 20)
    Fontperm= font.getsize(text)
    # print(Fontperm[1])
    size=(500,176) 
    
    textcolor=(240,240,240)

    image =Image.new('RGBA',size,(33,33,36,255))
    
    draw = ImageDraw.Draw(image)
    if len(text)>50:
        draw_multiple_line_text(image, text,font, textcolor,padding)
    else:
        draw.text(((image.size[0]-Fontperm[0])/2,(image.size[1]-Fontperm[1])/2),font=font,text=text,align='center') #(image.size[1]/2)-(Fontperm[1]/2)
    image.save(f'assets/temp/{id}/png/img{idx}.png')