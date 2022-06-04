from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as readme:
    description = readme.read()

setup(
    name="RedditVideoMakerBot",
    version="1.0", # change this if it is wrong,
    description="Create a Reddit video with Python!",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/iaacornus/scpterm",
    py_modules=[
        "main",
        "cli",
        "reddit/subreddit",
        "utils/console",
        "video_creation/background",
        "video_creation/final_video",
        "video_creation/screenshot_downloader",
        "video_creation/voices"
    ],
    include_package_data=True,
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "gTTS==2.2.4",
        "rich<=12.4.4",
        "moviepy==1.0.3",
        "mutagen==1.45.1",
        "playwright==1.22.0",
        "praw==7.6.0",
        "python-dotenv==0.20.0",
        "yt_dlp==2022.5.18"
    ],
    entry_points={
        "console_scripts" : [
            "RedditVideoMakerBot=cli:program_options",
        ]
    },
)
