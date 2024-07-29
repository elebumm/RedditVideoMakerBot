import json
import time
import os

from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
import asyncio

from bs4 import BeautifulSoup

from utils import settings

# Utils
def check_similarity(video_title, text):
        video_title_words = set(video_title.lower().split())
        text_words = set(text.lower().split())

        common_words = text_words.intersection(video_title_words)

        return len(common_words) / len(text_words) >= 0.6

# Runthrough
def generate_captions(file_path, title):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        page.goto("https://www.capcut.com/")

        email = settings.config["capcut"]["email"]
        password = settings.config["capcut"]["password"]
        video_title = title.lower()
        video_file_name = title.replace(" ", "_")

        page.click("//span[contains(text(),'Decline all')]")

        page.click("//span[contains(text(),'OK')]")

        page.goto("https://www.capcut.com/login")

        page.fill("//input[@class='lv-input lv-input-size-default lv_sign_in_panel_wide-input']", email)

        page.click("//span[normalize-space()='Continue']")

        # time.sleep(5)

        page.fill("//input[@type='password']", password)

        page.click("//span[contains(text(),'Sign in')]")

        try:
            page.click("//div[@class='skip--kncMC']")

        except:
            pass

        page.goto(f"https://www.capcut.com/my-cloud/{str(settings.config['capcut']['cloud_id'])}?start_tab=video&enter_from=page_header&from_page=work_space&tab=all")

        try:
            page.click("//span[contains(text(),'Decline all')]")

        except:
            pass

        if page.is_visible("//div[@class='guide-modal-close-icon']"):
            page.click("//div[@class='guide-modal-close-icon']")

        if page.is_visible("//div[@data-selectable-item-id]"):

            page.hover("//div[@data-selectable-item-id]")

            page.click("//*[@width='16']")

            page.click("//div[contains(text(),'Move to Trash')]")

            page.click("//span[contains(text(),'Confirm')]")

            # time.sleep(2)

            # page.click("//span[contains(text(),'Trash')]")

            # page.hover("//div[@data-selectable-item-id]")

            # page.screenshot(path="video_creation/Error3.png")

        page.goto("https://www.capcut.com/editor?enter_from=create_new&current_page=landing_page&from_page=work_space&start_tab=video&__action_from=my_draft&position=my_draft&scenario=youtube_ads&scale=9%3A16")

        if page.is_visible("//div[@class='guide-close-icon-f8J9FZ']//*[name()='svg']"):
            page.click("//div[@class='guide-close-icon-f8J9FZ']//*[name()='svg']")

        if page.is_visible("//div[@class='guide-placeholder-before-OsTdXF']"):
            page.click("//div[@class='guide-placeholder-before-OsTdXF']")

        if page.is_visible("//div[@class='guide-close-icon-f8J9FZ']//*[name()='svg']"):
            page.click("//div[@class='guide-close-icon-f8J9FZ']//*[name()='svg']")

        if page.is_visible("//div[@class='guide-close-icon-Gtxdju']//*[name()='svg']"):
            page.click("//div[@class='guide-close-icon-Gtxdju']//*[name()='svg']")

        if page.is_visible("//div[@class='guide-close-icon-Gtxdju']"):
            page.click("//div[@class='guide-close-icon-Gtxdju']")

        if page.is_visible("//div[@class='guide-close-icon-Gtxdju'][1]"):
            page.click("//div[@class='guide-close-icon-Gtxdju'][1]")

        if page.is_visible("//div[@class='guide-close-icon-OwPlMC']"):
            page.click("//div[@class='guide-close-icon-OwPlMC']")

        page.set_input_files("(//input[@type='file'])[1]", file_path)

        time.sleep(2)

        page.click("//div[@class='tools-dCzTyg']")
        page.click("(//li[@role='option'])[5]")

        time.sleep(18)

        page.click("//div[@id='siderMenuCaption']//div[@class='menu-inner-box']//*[name()='svg']")

        page.click("//div[normalize-space()='Auto captions']")

        video_ready = False
        while not video_ready:
            page.click("//footer[@class='active-panel']//span[contains(text(),'Generate')]")
            try:
                # check if class="lv-message lv-message-error" is visible
                if page.locator("//div[@class='lv-message lv-message-error']").is_visible():
                    video_ready = False
                else:
                    video_ready = True
            except:
                pass

            time.sleep(10)

        print("Changing settings")

        page.click("//div[@id='workbench-tool-bar-toolbarTextPreset']")

        time.sleep(20)

        page.click("//div[@id='lv-tabs-1-tab-1']")

        time.sleep(1)

        page.click(f"(//img[@class='image-QII91y'])[{str(settings.config['capcut']['preset_number'])}]")

        time.sleep(2)

        page.click("//div[@id='workbench-tool-bar-toolbarTextBasic']//div[@class='tool-bar-icon']//*[name()='svg']")

        time.sleep(2)

        page.fill("//input[@value='-672']", "0")

        time.sleep(1)

        page.fill("//input[@value='100' and @aria-valuemax='500']", "150")

        time.sleep(2)

        print("Cleaning up captions")

        for _ in range(10):
            element = page.query_selector("//div[@class='subtitle-list-content']/section[1]")
            html_code = page.evaluate("element => element.innerHTML", element)
            soup = BeautifulSoup(html_code, 'html.parser')
            textarea = soup.find('textarea', {'class': 'lv-textarea'})
            text = textarea.text.lower()

            if check_similarity(video_title.lower(), text.lower()):
                page.click("//section[@class='subtitle-list-item']")
                page.click("//button[@class='lv-btn lv-btn-text lv-btn-size-default lv-btn-shape-square']//*[name()='svg']")
            else:
                break

        print("Exporting video")

        page.click("//div[contains(@data-id,'titlebarExport')]//div[contains(@style,'position: relative;')]")

        page.click("//div[contains(@class,'content_7ddfe')]")

        page.fill("//input[@id='form-video_name_input']", video_file_name )

        page.click("//span[contains(text(),'720p')]")

        page.click("//span[contains(text(),'1080p')]")

        page.click("//span[contains(text(),'Recommended quality')]")

        page.click("//li[contains(text(),'High quality')]")

        page.click("//span[contains(text(),'30fps')]")

        page.click("//li[contains(text(),'60fps')]")

        time.sleep(2)

        page.click("//button[@id='export-confirm-button']")

        time.sleep(35)

        while not page.locator("//a[@class='shadowAnchor_5bc06']").is_visible():
            time.sleep(5)

        with page.expect_download() as download_info:
            page.locator("//a[@class='shadowAnchor_5bc06']").click()

        dl = download_info.value
        print(dl.path())
        working_dir_path = os.getcwd()

        os.makedirs(os.path.join(working_dir_path, "capcut_results", "videos"), exist_ok=True)

        final_path = os.path.join(working_dir_path, "capcut_results", "videos", video_file_name + ".mp4")
        print(final_path)
        dl.save_as(final_path)
        browser.close()
