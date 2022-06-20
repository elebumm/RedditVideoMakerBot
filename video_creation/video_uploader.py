from asyncio import sleep
import asyncio
import imp
from os import getenv
import os
from pathlib import Path
import pickle

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from playwright.async_api import async_playwright
import undetected_chromedriver.v2 as uc
from fake_useragent import UserAgent

from utils.console import print_step, print_substep
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
        options = uc.ChromeOptions()
        options.add_argument("--user-agent=" + UserAgent().random)
        
        cookie_path = "./video_creation/data/tiktok.cookie"
        has_cookie = False
        try:
            cookie_file = open(cookie_path, "rb")
            has_cookie = True
            options.add_argument("--headless")
            print_substep("Launching Headless Browser...")
        except FileNotFoundError:
            print_substep("Launching Browser to manually log you in (only first time).")
      
        browser = uc.Chrome(options=options)
        browser.delete_all_cookies()
        
        # Get the thread screenshot
        browser.get("https://www.tiktok.com/login")
        
        await asyncio.sleep(3)
        
        if not has_cookie:
            print("Your browser currently shows the tiktok login page, please login in.")
            input("After you have logged in fully, please press any button to continue...")
            print("#####")
            pickle.dump(browser.get_cookies(), open(cookie_path, "wb+"))
            print("Cookie has been created successfully, resuming upload!")
            cookie_file = open(cookie_path, "rb")
            
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
        
        title = os.getenv("VIDEO_TITLE") or videofile.split(".")[0]
        is_nsfw = os.getenv("nsfw") or "false"
        if is_nsfw:
            title = "#nsfw " + title
        
        tags = os.getenv("TIKTOK_TAGS") or "#AskReddit"
        
        if len(title) + len(tags) > 150:
            if len(tags) > 150:
                print_substep("Tags are too long, please shorten them.")
                return
            
            remove = 149 - len(tags)
            title = title[:remove] + " " + tags
        else:
            title = title + " " + tags
        
        title_input = browser.find_elements(By.XPATH, '//*[@id="root"]/div/div/div/div/div[2]/div[2]/div[1]/div/div[1]/div[2]/div/div[1]/div/div/div/div/div/div')[0]
        title_input.send_keys(Keys.CONTROL, "a")
        title_input.send_keys(Keys.BACKSPACE)
        title_input.send_keys(title)
        
        await asyncio.sleep(1)
        
        browser.find_elements(By.XPATH, '//*[@id="root"]/div/div/div/div/div[2]/div[2]/div[7]/div[2]/button')[0].click()
        await asyncio.sleep(5)
        
        print_substep("Video uploaded Successfully.", style="bold green")
