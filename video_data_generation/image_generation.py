import os
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont

from utils.imagenarator import draw_multiple_line_text


s = requests.session()

def get_csrf_token():
    csrf_url = "https://image.plus/"

    csrf_headers = {
    'Host': 'image.plus',
    'Sec-Ch-Ua': '"Chromium";v="121", "Not A(Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.160 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Priority': 'u=0, i',
    'Connection': 'close'
    }

    response = s.request("GET", csrf_url, headers=csrf_headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.find("meta", {"name":"csrf-token"})['content']

def generate_image(prompt, save_path):
    url = "https://image.plus/images/generate"
    csrf_token = get_csrf_token()

    payload = f"prompt={prompt.replace(' ', '+')}&negative_prompt=&model=1&style=comic-book&samples=1&size=1152x896"
    headers = {
        'Host': 'image.plus',
        'Content-Length': '106',
        'Sec-Ch-Ua': '"Chromium";v="121", "Not A(Brand";v="99"',
        'Sec-Ch-Ua-Mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.160 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Origin': 'https://image.plus',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://image.plus/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Priority': 'u=1, i',
        'X-Csrf-Token': csrf_token,
    }

    response = s.request("POST", url, headers=headers, data=payload)
    image_url = response.json()['images'][0]['src']
    image = s.get(image_url).content
    with open(save_path, 'wb') as file:
        file.write(image)
    return save_path

def add_text(thumbnail_path, text, save_path):
    bg = "./assets/backgrounds/background.jpg"
    if thumbnail_path is None:
        thumbnail_path = "./assets/thumbnail_bg.png"
    
    img1 = Image.open(bg).convert("RGBA")
    img2 = Image.open(thumbnail_path).resize((720, 720)).convert("RGBA")
    img1.paste(img2, (0,0), mask=img2)
    
    # font = ImageFont.truetype(os.path.join("fonts", "Another-Danger.otf"), 50)
    # font = ImageFont.truetype(os.path.join("fonts", "Foul-Fiend.ttf"), 30)
    font = ImageFont.truetype(os.path.join("fonts", "Mystery-Lake.ttf"), 75)
    size = (560, 720)
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw_multiple_line_text(
        image,
        text,
        font,
        [(255, 255, 255), (165, 42, 42)],
        20,
        wrap=20,
        transparent=True
    )

    img1.paste(image, (720,0), mask=image)
    img1.show()
    img1.save(save_path)
    return save_path


if __name__ == '__main__':
    prompt = "A hyper-realistic, scary image of a ghost flying in a room and a person sitting on a couch very scared looking at the ghost."
    image_path = generate_image(prompt)
    print(image_path)