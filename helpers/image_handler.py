from PIL import Image, ImageDraw, ImageFont
import requests


def draw_text(y, font, text, draw, width):
    shadowcolor = (0, 0, 0)
    fillcolor = (255, 255, 255)
    textWidth = font.getsize(text)[0]
    x = (width - textWidth) / 2
    draw.text((x - 2, y - 2), text, font=font, fill=shadowcolor)
    draw.text((x + 2, y - 2), text, font=font, fill=shadowcolor)
    draw.text((x - 2, y + 2), text, font=font, fill=shadowcolor)
    draw.text((x + 2, y + 2), text, font=font, fill=shadowcolor)
    draw.text((x, y), text, font=font, fill=fillcolor)
    return draw


def make_welcome(background, user):
    font_path = "images/Franklin Gothic Medium Regular.ttf"
    bg = Image.open("images/sky3.png")
    width = bg.size[0]
    if background == "leave":
        bg = Image.new('RGBA', bg.size, (255, 255, 255, 0))
    pfp = Image.open(requests.get(user.avatar_url_as(format="png", size=256), stream=True).raw)

    p_size = (256, 256)
    p_x = 380
    p_y = 50

    pfp = pfp.resize(p_size)
    bg.paste(pfp, (p_x, p_y, p_x + p_size[0], p_y + p_size[1]))

    draw = ImageDraw.Draw(bg)

    # welcome
    font = ImageFont.truetype(font_path, 75)

    if background == "leave":
        text = "Goodbye"
    else:
        text = "Welcome"

    y = 325
    draw = draw_text(y, font, text, draw, width)

    # username
    font = ImageFont.truetype(font_path, 56)
    text = str(user)
    y = 430
    draw = draw_text(y, font, text, draw, width)

    bg.save("image.png")


def mask_circle_transparent(pil_img, offset=0):
    mask = Image.new("L", pil_img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset), fill=255)

    result = pil_img.copy()
    result.putalpha(mask)

    return result
