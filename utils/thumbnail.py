from PIL import ImageDraw, ImageFont


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
