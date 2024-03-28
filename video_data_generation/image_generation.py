import requests
from bs4 import BeautifulSoup


s = requests.session()

def renew_connection():
    csrf_url = "https://image.plus/"
    payload = {}

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

    s.cookies.clear()
    response = s.request("GET", csrf_url, headers=csrf_headers)
    print(response.status_code)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.find("meta", {"name":"csrf-token"})['content']


def generate_image(csrf_token, prompt=None):
    url = "https://image.plus/images/generate"

    prompt = "A ghost flying with a person sitting scared on a couch."
    payload = f"prompt={prompt.replace(' ', '+')}&negative_prompt=&model=1&style=cinematic&samples=1&size=1152x896"
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
    return response.json()

image = generate_image(renew_connection())
print(image)