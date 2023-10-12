import time
import webbrowser
import pyautogui
import os

path = r"C:\Users\JAdmin\Desktop\RYBot\results\AmItheAsshole"

def hover(image):
    img_location = pyautogui.locateOnScreen(image, confidence=0.95)
    image_location_point = pyautogui.center(img_location)
    x, y = image_location_point
    pyautogui.moveTo(x, y)

def findClick(image):
    img_location = pyautogui.locateOnScreen(image, confidence=0.95)
    image_location_point = pyautogui.center(img_location)
    x, y = image_location_point
    pyautogui.click(x, y)

def findDoubleClick(image):
    img_location = pyautogui.locateOnScreen(image, confidence=0.95)
    image_location_point = pyautogui.center(img_location)
    x, y = image_location_point
    pyautogui.click(x, y)
    time.sleep(0.05)
    pyautogui.click(x, y)

def uploadVideo():
    time.sleep(20)
    findClick("uploadImages\\create.png")
    time.sleep(1)
    findClick("uploadImages\\uploadButton.png")
    time.sleep(1)
    findClick("uploadImages\\selectFiles.png")
    time.sleep(1)
    findClick("uploadImages\\filesAddress.png")
    time.sleep(1)
    pyautogui.write(path)
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(1)
    findDoubleClick("uploadImages\\video.png")
    time.sleep(20)
    hover("uploadImages\\details.png")
    time.sleep(1)
    pyautogui.scroll(-99999)
    time.sleep(1)
    findClick("uploadImages\\coppa.png")
    time.sleep(1)
    findClick("uploadImages\\next.png")
    time.sleep(1)
    findClick("uploadImages\\next.png")
    time.sleep(1)
    findClick("uploadImages\\next.png")
    time.sleep(1)
    findClick("uploadImages\\public.png")
    time.sleep(1)
    findClick("uploadImages\\public.png")
    time.sleep(1)
    findClick("uploadImages\\publish.png")
    time.sleep(20)
    pyautogui.hotkey('alt', 'f4')

def deleteVideo():
    pyautogui.press('win')
    time.sleep(1)
    pyautogui.write(path)
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(1)
    pyautogui.press('down')
    pyautogui.press('up')
    time.sleep(1)
    pyautogui.press('del')
    time.sleep(1)
    pyautogui.press('enter')

    time.sleep(1)
    pyautogui.hotkey('alt', 'f4')


webbrowser.open_new("https://studio.youtube.com/")
uploadVideo()
deleteVideo()
