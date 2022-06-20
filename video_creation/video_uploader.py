from asyncio import sleep
import asyncio
import json
from os import getenv
import os
from pathlib import Path
import pickle

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common

from playwright.async_api import async_playwright
import undetected_chromedriver.v2 as uc
from fake_useragent import UserAgent, FakeUserAgentError

from utils.console import print_step, print_substep
import json
from rich.console import Console

console = Console()

storymode = False


async def upload_video_to_tiktok(videofile):
    """Uploads the video to tiktok.
    Args:
            videofile: The video file you want to upload inside of /results.
    """
    print_step("Uploading video to tiktok...")

    # ! Make sure the reddit screenshots folder exists
    Path("results").mkdir(parents=True, exist_ok=True)

    
    async with async_playwright() as p:
        print_substep("Launching Headless Browser...")

        options = uc.ChromeOptions()
        options.add_argument("--user-agent=" + UserAgent().random)
        options.add_argument("--headless")
        browser = uc.Chrome(options=options)
        browser.delete_all_cookies()
        
        # Get the thread screenshot
        browser.get("https://www.tiktok.com/login")
        
        await asyncio.sleep(3)
        
        cookie_file = open("./video_creation/data/tiktok.cookie", "rb")
        cookie_data = pickle.load(cookie_file)
        for cookie in cookie_data:
            if 'sameSite' in cookie:
                if cookie['sameSite'] == 'None':
                    cookie['sameSite'] = 'Strict'
            browser.add_cookie(cookie)
        browser.refresh()

        await asyncio.sleep(3)
        print_substep("Logged in...")
        
        browser.get('https://www.tiktok.com/upload')
        await asyncio.sleep(5)
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        abs_path = os.path.join(os.getcwd(), f'results/{videofile}')
        browser.switch_to.frame(0)
        browser.implicitly_wait(1)
        browser.find_elements(By.XPATH, '//*[@id="root"]/div/div/div/div/div[2]/div[1]/div/input')[0].send_keys(abs_path)
        print_substep("Uploading video...")
        await asyncio.sleep(10)
        browser.find_elements(By.XPATH, '//*[@id="root"]/div/div/div/div/div[2]/div[2]/div[7]/div[2]/button')[0].click()
        await asyncio.sleep(5)
        
        print_substep("Video uploaded Successfully.", style="bold green")
