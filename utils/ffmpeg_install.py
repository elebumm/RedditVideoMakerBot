import requests
import os
import subprocess


def ffmpeg_install_windows():
    try:
        zip = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        r = requests.get(zip)
        with open("ffmpeg.zip", "wb") as f:
            f.write(r.content)
        import zipfile

        with zipfile.ZipFile("ffmpeg.zip", "r") as zip_ref:
            zip_ref.extractall()
        os.remove("ffmpeg.zip")
        os.rename("ffmpeg-master-latest-win64-gpl", "ffmpeg")
        # Move the files inside bin to the root
        for file in os.listdir("ffmpeg/bin"):
            os.rename(f"ffmpeg/bin/{file}", f"ffmpeg/{file}")
        os.rmdir("ffmpeg/bin")
        for file in os.listdir("ffmpeg/doc"):
            os.remove(f"ffmpeg/doc/{file}")
        os.rmdir("ffmpeg/doc")
        # Add to the path
        subprocess.run("setx /M PATH \"%PATH%;%CD%\\ffmpeg\"", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("FFmpeg installed successfully! Please restart your computer and then re-run the program.")
        exit()
    except Exception as e:
        print(
            "An error occurred while trying to install FFmpeg. Please try again. Otherwise, please install FFmpeg manually and try again.")
        print(e)
        exit()


def ffmpeg_install_linux():
    try:
        subprocess.run("sudo apt install ffmpeg", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        print(
            "An error occurred while trying to install FFmpeg. Please try again. Otherwise, please install FFmpeg manually and try again.")
        print(e)
        exit()
    print("FFmpeg installed successfully! Please re-run the program.")
    exit()


def ffmpeg_install_mac():
    try:
        subprocess.run("brew install ffmpeg", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print(
            "Homebrew is not installed. Please install it and try again. Otherwise, please install FFmpeg manually and try again.")
        exit()
    print("FFmpeg installed successfully! Please re-run the program.")
    exit()


def ffmpeg_install():
    try:
        # Try to run the FFmpeg command
        subprocess.run(['ffmpeg', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print('FFmpeg is installed on this system! If you are seeing this error for the second time, restart your computer.')
    except FileNotFoundError as e:
        print('FFmpeg is not installed on this system.')
        resp = input("We can try to automatically install it for you. Would you like to do that? (y/n): ")
        if resp.lower() == "y":
            print("Installing FFmpeg...")
            if os.name == "nt":
                ffmpeg_install_windows()
            elif os.name == "posix":
                ffmpeg_install_linux()
            elif os.name == "mac":
                ffmpeg_install_mac()
            else:
                print("Your OS is not supported. Please install FFmpeg manually and try again.")
                exit()
        else:
            print("Please install FFmpeg manually and try again.")
            exit()
    except Exception as e:
        print("Welcome fellow traveler! You're one of the few who have made it this far. We have no idea how you got at this error, but we're glad you're here. Please report this error to the developer, and we'll try to fix it as soon as possible. Thank you for your patience!")
        print(e)
    return None