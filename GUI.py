from genericpath import isfile
from main import main, shutdown, start

from doctest import master
import tkinter
import tkinter.messagebox
import customtkinter
from tkinter import filedialog
import os
import toml
import shutil
from utils.settings import check_toml
from utils import settings
from pathlib import Path

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(customtkinter.CTk):

    WIDTH = 1200
    HEIGHT = 600

    def __init__(self):
        super().__init__()

        self.title("Reddit Video Maker Bot GUI")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed

        # ============ create two frames ============

        # configure grid layout (2x1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self,
                                                 width=180,
                                                 corner_radius=0)
        self.frame_left.grid(row=0, column=0, sticky="nswe")

        # Results Frame
        self.frame_results = customtkinter.CTkFrame(master=self)
        self.frame_results.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        # Settings Frame
        self.frame_settings = customtkinter.CTkFrame(master=self)
        self.frame_settings.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        # Home Frame
        self.frame_home = customtkinter.CTkFrame(master=self)
        self.frame_home.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)
        # ============ frame_left ============

        # configure grid layout (1x11)
        self.frame_left.grid_rowconfigure(0, minsize=10)   # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(5, weight=1)  # empty row as spacing
        self.frame_left.grid_rowconfigure(8, minsize=20)    # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(11, minsize=10)  # empty row with minsize as spacing

        self.label_1 = customtkinter.CTkLabel(master=self.frame_left,
                                              text="Reddit Video Maker Bot",
                                              text_font=("Roboto Medium", -16))  # font name and size in px
        self.label_1.grid(row=1, column=0, pady=10, padx=10)

        # Home Btn
        self.home_btn = customtkinter.CTkButton(master=self.frame_left,
                                                text="Home",
                                                command=self.btn_home)
        self.home_btn.grid(row=2, column=0, pady=10, padx=20)

        # Settings Btn
        self.settings_btn = customtkinter.CTkButton(master=self.frame_left,
                                                text="Settings",
                                                command=self.btn_settings)
        self.settings_btn.grid(row=3, column=0, pady=10, padx=20)
        
        # Results Btn
        self.results_btn = customtkinter.CTkButton(master=self.frame_left,
                                                text="Results",
                                                command=self.btn_results)
        self.results_btn.grid(row=4, column=0, pady=10, padx=20)

        # Start Btn
        self.start_btn = customtkinter.CTkButton(master=self.frame_left,
            text="Start",
            command=self.btn_start)
        self.start_btn.grid(row=5, column=0, pady=10, padx=40)

        # Appeareance Stuff
        self.label_mode = customtkinter.CTkLabel(master=self.frame_left, text="Appearance Mode:")
        self.label_mode.grid(row=9, column=0, pady=10, padx=20, sticky="w")

        self.optionmenu_1 = customtkinter.CTkOptionMenu(master=self.frame_left,
                                                        values=["Light", "Dark", "System"],
                                                        command=self.change_appearance_mode)
        self.optionmenu_1.grid(row=10, column=0, pady=0, padx=20, sticky="w")
        # Set default mode to system
        self.optionmenu_1.set("System")

### Adds all the stuff for frame_settings ###

        # Background within frame
        self.frame_bg_settings = customtkinter.CTkFrame(master=self.frame_settings)
        self.frame_bg_settings.grid(row=0, column=0, pady=15, padx=15, ipadx=18, sticky=("nswe"))

        self.frame_bg_settings.rowconfigure(10, weight=1)
        self.frame_bg_settings.columnconfigure(10, weight=1)

        # Title
        self.settings_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Settings",
            text_font=("Courier_Bold", 24)
        )
        self.settings_title.grid(row=0, column=0, columnspan=8, pady=15, padx=15)

## USER SETTINGS ##

    # User settings title
        self.user_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="User Settings",
            text_font=("Courier_Bold", 14)
        )
        self.user_title.grid(row=1, column=0, columnspan=2, pady=10)

    # Client secret title
        self.client_secret_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Client Secrect"
        )
        self.client_secret_title.grid(row=2, column=0, padx=15)

    # Client secret input box
        self.client_secret = customtkinter.CTkEntry(
            master=self.frame_bg_settings,
            placeholder_text = "Client Secret"
        )
        self.client_secret.grid(row=3, column=0, padx=15)

    # Client id title
        self.client_id_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text = "Client Id"
        )
        self.client_id_title.grid(row=4, column=0, padx=15)

    # Client id input box
        self.client_id = customtkinter.CTkEntry(
            master=self.frame_bg_settings,
            placeholder_text="Client Id"
        )
        self.client_id.grid(row=5, column=0, padx=15)

    # Username title
        self.user_name_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Username"
        )
        self.user_name_title.grid(row=2, column=1, padx=15)
    
    # Username input box
        self.user_name = customtkinter.CTkEntry(
            master=self.frame_bg_settings,
            placeholder_text="Username"
        )
        self.user_name.grid(row=3, column=1, padx=15)

    # Password title
        self.user_password_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Password"
        )
        self.user_password_title.grid(row=4, column=1, padx=15)

    # Password input box
        self.user_password = customtkinter.CTkEntry(
            master=self.frame_bg_settings,
            placeholder_text="Password"
        )
        self.user_password.grid(row=5, column=1, padx=15)

    # 2fa label
        self.user_2fa_label = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text = "2FA enabled?"
        )
        self.user_2fa_label.grid(row=6, column=0, padx=15)

    # 2fa option menu
        self.user_2fa = customtkinter.CTkOptionMenu(
            master=self.frame_bg_settings,
            values=["false", "true"]
        )
        self.user_2fa.grid(row=7, column=0, padx=15)

# Thread Settings 

    # Thread settings title
        self.thread_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Thread Settings",
            text_font=("Courier_Bold", 14)
        )
        self.thread_title.grid(row=1, column=2, columnspan=2, pady=10)

    # Random Title
        self.thread_random_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Random"
        )
        self.thread_random_title.grid(row=2, column=2, padx=15)

    # Random option menu
        self.thread_random = customtkinter.CTkOptionMenu(
            master=self.frame_bg_settings,
            values=["false", "true"]
        )
        self.thread_random.grid(row=3, column=2, padx=15)

    # Subreddit title
        self.thread_subreddit_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Subreddit"
        )
        self.thread_subreddit_title.grid(row=2, column=3, padx=15)
    
    # Subreddit input box
        self.thread_subreddit = customtkinter.CTkEntry(
            master=self.frame_bg_settings,
            placeholder_text="Subreddit"
        )
        self.thread_subreddit.grid(row=3, column=3, padx=15)

    # Post id title
        self.thread_post_id_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Post Id"
        )
        self.thread_post_id_title.grid(row=4, column=2, padx=15)

    # Post id input box
        self.thread_post_id = customtkinter.CTkEntry(
            master=self.frame_bg_settings,
            placeholder_text="Post Id"
        )
        self.thread_post_id.grid(row=5, column=2, padx=15)

    # Max comment length title
        self.thread_max_comment_length_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Max comment length (NUM)"
        )
        self.thread_max_comment_length_title.grid(row=4, column=3, padx=15)

    # Max comment length
        self.thread_max_comment_length = customtkinter.CTkEntry(
            master=self.frame_bg_settings,
            placeholder_text="Max comment length"
        )
        self.thread_max_comment_length.grid(row=5, column=3, padx=15)

    # Post lang title
        self.thread_post_lang_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Post language"
        )
        self.thread_post_lang_title.grid(row=6, column=2, padx=15)

    # Post lang
        self.thread_post_lang = customtkinter.CTkEntry(
            master=self.frame_bg_settings,
            placeholder_text="Post language (en/cr)"
        )
        self.thread_post_lang.grid(row=7, column=2, padx=15)

    # Min comment length title
        self.thread_min_comment_length_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Min comment length (NUM)"
        )
        self.thread_min_comment_length_title.grid(row=6, column=3, padx=15)

    # Min comment length
        self.thread_min_comment_length = customtkinter.CTkEntry(
            master=self.frame_bg_settings,
            placeholder_text="Min comment length"
        )
        self.thread_min_comment_length.grid(row=7, column=3, padx=15)

# Misc Settings

    # Misc settings title
        self.misc_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Misc Settings",
            text_font=("Courier_Bold", 14)
        )
        self.misc_title.grid(row=8, column=0, columnspan=2, pady=10)

    # Allow nsfw title
        self.misc_allow_nsfw_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Allow NSFW"
        )
        self.misc_allow_nsfw_title.grid(row=9, column=0, padx=15)

    # Allow nsfw option box
        self.misc_allow_nsfw = customtkinter.CTkOptionMenu(
            master=self.frame_bg_settings,
            values=["False", "True"]
        )
        self.misc_allow_nsfw.grid(row=10, column=0, padx=15)

    # Theme title
        self.misc_theme_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Theme"
        )
        self.misc_theme_title.grid(row=9, column=1, padx=15)

    # Theme
        self.misc_theme = customtkinter.CTkOptionMenu(
            master=self.frame_bg_settings,
            values=["dark", "light"]
        )
        self.misc_theme.grid(row=10, column=1, padx=15)

    # Times to run title
        self.misc_times_to_run_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Times to run (NUM)"
        )
        self.misc_times_to_run_title.grid(row=11, column=0, padx=15)

    # Times to run
        self.misc_times_to_run = customtkinter.CTkEntry(
            master=self.frame_bg_settings,
            placeholder_text="Times to run"
        )
        self.misc_times_to_run.grid(row=12, column=0, padx=15)

    # Opacity title
        self.misc_opacity_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Opacity (NUM 0.1-0.9)"
        )
        self.misc_opacity_title.grid(row=11, column=1, padx=15)

    # Opcaity
        self.misc_opacity = customtkinter.CTkEntry(
            master=self.frame_bg_settings,
            placeholder_text="Opacity"
        )
        self.misc_opacity.grid(row=12, column=1, padx=15)

    # Transition title
        self.misc_transition_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Transition"
        )
        self.misc_transition_title.grid(row=13, column=0, padx=15)

    # Transition
        self.misc_transition = customtkinter.CTkEntry(
            master=self.frame_bg_settings,
            placeholder_text="Transtion"
        )
        self.misc_transition.grid(row=14, column=0, padx=15)

# Background Settings

    # Background settings title
        self.background_settings_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Background Settings",
            text_font=("Courier_Bold", 14)
        )
        self.background_settings_title.grid(row=1, column=4, pady=10)

    # Choose background title
        self.background_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Background"
        )
        self.background_title.grid(row=2, column=4, padx=15)

    # Select one of these (custom, youtube or built in video)
        self.background_select = customtkinter.CTkOptionMenu(
            master=self.frame_bg_settings,
            values=["builtin", "custom", "youtube"],
            command=self.switchBackgroundType
        )
        self.background_select.grid(row=3, column=4, padx=15)

    # Custom title
        self.background_custom_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Custom background"
        )
        self.background_custom_title.grid(row=4, column=4, padx=15)

    # Custom file path
        self.background_custom = customtkinter.CTkButton(
            master=self.frame_bg_settings,
            text="Select background",
            command=self.backgroundBrowse
        )
        self.background_custom.grid(row=5, column=4, padx=15)

    # Youtube title
        self.background_youtube_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="YouTube background"
        )
        self.background_youtube_title.grid(row=4, column=4, padx=15)

    # Youtube
        self.background_youtube = customtkinter.CTkEntry(
            master=self.frame_bg_settings,
            placeholder_text="YouTube URL"
        )
        self.background_youtube.grid(row=5, column=4, padx=15)

    # Builtin title
        self.background_builtin_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Builtin background"
        )
        self.background_builtin_title.grid(row=4, column=4, padx=15)

    # Builtin
    # Gets the config template toml options and creates a dropdown menu
        configtemplate = toml.load("utils/.config.template.toml")
        self.background_builtin = customtkinter.CTkOptionMenu(
            master=self.frame_bg_settings,
            values=configtemplate["settings"]["background"]["background_choice"]["options"]
        )
        self.background_builtin.grid(row=5, column=4, padx=15)

# Tts Settings

    # Tts settings title
        self.tts_settings_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Text To Speech Settings",
            text_font=("Courier_Bold", 14)
        )
        self.tts_settings_title.grid(row=8, column=2, columnspan=2, pady=10)

    # Voice choice title
        self.tts_voice_choice_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Voice choice"
        )
        self.tts_voice_choice_title.grid(row=9, column=2, padx=15)

    # Voice choice
        self.tts_voice_choice = customtkinter.CTkOptionMenu(
            master=self.frame_bg_settings,
            values=["tiktok", "googletranslate", "streamlabspolly", "awspolly", "pyttsx"],
            command=self.ttsVoiceChange
        )
        self.tts_voice_choice.grid(row=10, column=2, padx=15)

    # aws_polly_voice title
        self.tts_aws_polly_voice_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Aws polly voice"
        )
        self.tts_aws_polly_voice_title.grid(row=11, column=2, padx=15)

    # aws_polly_voice
        self.tts_aws_polly_voice = customtkinter.CTkOptionMenu(
            master=self.frame_bg_settings,
            values=["Brian","Emma","Russell","Joey","Matthew","Joanna","Kimberly","Amy","Geraint","Nicole","Justin","Ivy","Kendra","Salli","Raveena"]
        )
        self.tts_aws_polly_voice.grid(row=12, column=2, padx=15)

    # streamlabs_polly_voice title
        self.tts_streamlabs_polly_voice_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Streamlabs polly voice"
        )
        self.tts_streamlabs_polly_voice_title.grid(row=11, column=2, padx=15)

    # streamlabs_polly_voice
        self.tts_streamlabs_polly_voice = customtkinter.CTkOptionMenu(
            master=self.frame_bg_settings,
            values=["Brian","Emma","Russell","Joey","Matthew","Joanna","Kimberly","Amy","Geraint","Nicole","Justin","Ivy","Kendra","Salli","Raveena"]
        )
        self.tts_streamlabs_polly_voice.grid(row=12, column=2, padx=15)

    # GoogleTranslate title
        self.tts_google_translate_voice_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Google Translate voice"
        )
        self.tts_aws_polly_voice_title.grid(row=11, column=2, padx=15)

    # GoogleTranslate
        self.tts_google_translate_voice = customtkinter.CTkOptionMenu(
            master=self.frame_bg_settings,
            values=["No options"],
            state="disabled"
        )
        self.tts_google_translate_voice.grid(row=12, column=2, padx=15)
    
    # python_voice title
        self.tts_python_voice_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Python voice"
        )
        self.tts_python_voice_title.grid(row=11, column=2, padx=15)

    # python_voice
        self.tts_python_voice = customtkinter.CTkOptionMenu(
            master=self.frame_bg_settings,
            values=["1", "2"]
        )
        self.tts_python_voice.grid(row=12, column=2, padx=15)

    # py_voice_num title
        self.py_voice_num_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Python voice number"
        )
        self.py_voice_num_title.grid(row=11, column=2, padx=15)

    # py_voice_num
        self.tts_py_voice_num = customtkinter.CTkOptionMenu(
            master=self.frame_bg_settings,
            values=["1", "2"]
        )
        self.tts_py_voice_num.grid(row=12, column=2, padx=15)

    # tiktok_voice title
        self.tts_tiktok_voice_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="TikTok voice"
        )
        self.tts_tiktok_voice_title.grid(row=11, column=2, padx=15)

    # tiktok_voice
        self.tts_tiktok_voice = customtkinter.CTkOptionMenu(
            master=self.frame_bg_settings,
            values=["en_au_001","en_au_002","en_uk_001","en_uk_003","en_us_001","en_us_002","en_us_006","en_us_007","en_us_009","en_us_010",]
        )
        self.tts_tiktok_voice.grid(row=12, column=2, padx=15)

    # silence_duration title
        self.tts_silence_duration_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Silence duration"
        )
        self.tts_silence_duration_title.grid(row=9, column=3, padx=15)

    # silence_duration
        self.tts_silence_duration = customtkinter.CTkEntry(
            master=self.frame_bg_settings,
            placeholder_text="0.1 / 0.9"
        )
        self.tts_silence_duration.grid(row=10, column=3, padx=15)

    

        # configure grid layout (3x7)
        
        self.frame_info = customtkinter.CTkFrame(master=self.frame_home)
        self.frame_info.grid(row=0, column=0, columnspan=2, rowspan=4, pady=20, padx=20, sticky="nsew")

        # ============ frame_info ============

        # configure grid layout (1x1)
        self.frame_info.rowconfigure(0, weight=1)
        self.frame_info.columnconfigure(0, weight=1)

        self.label_info_1 = customtkinter.CTkLabel(master=self.frame_info,
                                                   text="Thanks for using this tool! \n" +
                                                   "Feel free to contribute to this project on GitHub!\n"+
                                                   "If you have any questions, feel free to reach out to\nme on Twitter or submit a GitHub issue. \n"+
                                                   "You can find solutions to many common problems in the Documentation\nhttps://reddit-video-maker-bot.netlify.app/" ,
                                                   height=100,
                                                   corner_radius=6,  # <- custom corner radius
                                                   fg_color=("white", "gray38"),  # <- custom tuple-color
                                                   justify=tkinter.LEFT)
        self.label_info_1.grid(column=0, row=0, sticky="nwe", padx=15, pady=15)



# Settings sync

    # Check if config.toml exists if not generates a new config with default values
        if not os.path.isfile("config.toml"):
            print("Can't find config generating new config")
            open("config.toml", "w")
            shutil.copyfile("utils/config.temp.toml", "config.toml")

        config = toml.load("config.toml") # Loads config to be able to read and write

# Sync config settings to gui
        
    # User Settings

        # User name
        if not config["reddit"]["creds"]["username"] == "":
            self.user_name.insert("0", config["reddit"]["creds"]["username"])

        # User password
        if not config["reddit"]["creds"]["password"] == "":
            self.user_password.insert("0", config["reddit"]["creds"]["password"])
        
        # Client Secret
        if not config["reddit"]["creds"]["client_secret"] == "":
            self.client_secret.insert("0", config["reddit"]["creds"]["client_secret"])
        
        # Client Id
        if not config["reddit"]["creds"]["client_id"] == "":
            self.client_id.insert("0", config["reddit"]["creds"]["client_id"])

        # 2fa
        self.user_2fa.set(str(config["reddit"]["creds"]["2fa"]))

    # Thread Settings

        # Random
        self.thread_random.set(str(config["reddit"]["thread"]["random"]))

        # Subreddit
        if not config["reddit"]["thread"]["subreddit"] == "":
            self.thread_subreddit.insert("0", config["reddit"]["thread"]["subreddit"])

        # Post id
        if not config["reddit"]["thread"]["post_id"] == "":
            self.thread_post_id.insert("0", config["reddit"]["thread"]["post_id"])

        # Max comment length
        self.thread_max_comment_length.insert("0", config["reddit"]["thread"]["max_comment_length"])

        # Post langauge
        if not config["reddit"]["thread"]["post_lang"] == "":
            self.thread_post_lang.insert("0", config["reddit"]["thread"]["post_lang"])

        # Min comments
        self.thread_min_comment_length.insert("0", config["reddit"]["thread"]["min_comments"])

    # Misc Settings

        # Allow nsfw
        self.misc_allow_nsfw.set(str(config["settings"]["allow_nsfw"]))

        # Theme
        self.misc_theme.set(str(config["settings"]["theme"]))

        # Times to run
        self.misc_times_to_run.insert("0", config["settings"]["times_to_run"])

        # Opacity
        self.misc_opacity.insert("0", config["settings"]["opacity"])
        
        # Transition
        self.misc_transition.insert("0", config["settings"]["transition"])

    # TTS settings

        # Voice
        self.tts_voice_choice.insert("0", config["settings"]["tts"]["voice_choice"])

        # AWS polly voice
        self.tts_aws_polly_voice.insert("0", config["settings"]["tts"]["aws_polly_voice"])

        # Streamlabs polly voice
        self.tts_streamlabs_polly_voice.insert("0", config["settings"]["tts"]["streamlabs_polly_voice"])

        # Tiktok voice
        self.tts_tiktok_voice.insert("0", config["settings"]["tts"]["tiktok_voice"])

        # python_voice
        self.tts_python_voice.insert("0", config["settings"]["tts"]["python_voice"])

        # py_voice_num
        self.tts_py_voice_num.insert("0", config["settings"]["tts"]["py_voice_num"])

# Sync gui to config
    def saveSettings(self):
        print("Saving Settings to config.toml")
        config = toml.load("config.toml")

    # User Settings

        # User name
        config["reddit"]["creds"]["username"] = self.user_name.get()

        # User password
        config["reddit"]["creds"]["password"] = self.user_password.get()

        # Client secret
        config["reddit"]["creds"]["client_secret"] = self.client_secret.get()

        # Client id
        config["reddit"]["creds"]["client_id"] = self.client_id.get()

        # 2fa
        config["reddit"]["creds"]["2fa"] = self.user_2fa.get()

    # Thread Settings

        # Random
        config["reddit"]["thread"]["random"] = self.thread_random.get()

        # Subreddit
        config["reddit"]["thread"]["subreddit"] = self.thread_subreddit.get()

        # Post id
        config["reddit"]["thread"]["post_id"] = self.thread_post_id.get()

        # Max comment length
        config["reddit"]["thread"]["max_comment_length"] = self.thread_max_comment_length.get()

        # Post langauge
        config["reddit"]["thread"]["post_lang"] = self.thread_post_lang.get()

        # Min comments
        config["reddit"]["thread"]["min_comments"] = self.thread_min_comment_length.get()

    # Misc Settings

        # Allow nsfw
        config["settings"]["allow_nsfw"] = self.misc_allow_nsfw.get()

        # Theme
        config["settings"]["theme"] = self.misc_theme.get()

        # Times to run
        config["settings"]["times_to_run"] = self.misc_times_to_run.get()

        # Opacity
        config["settings"]["opacity"] = self.misc_opacity.get()

        # Transition
        config["settings"]["transition"] = self.misc_transition.get()

        #TODO save TTS settings

    # Dump new data into config.toml
        configWrite = open("config.toml", "w")
        toml.dump(config, configWrite)

        print("Settings saved to config.toml")

    # Background file browse
    def backgroundBrowse(self):
        filepath = filedialog.askopenfilename(
            initialdir="/",
            title="Select a mp4 file",
            multiple=False,
            filetypes=(("mp4 files", "*.mp4"), ("all files", "*.*"))
        )
        filename = Path(filepath).stem

        self.background_custom.configure(text=filename)

        if filepath == "":
            self.background_custom.configure(text="Select background")
        else:
            #get current path
            current_path = os.getcwd()
            Path("./assets/backgrounds/").mkdir(parents=True, exist_ok=True)
            shutil.copy(filepath, f"{current_path}\\assets\\backgrounds\\{filename}.mp4")

    # Background type switch
    def switchBackgroundType(self, type):
        if type == "custom":
            self.background_custom_title.tkraise()
            self.background_custom.tkraise()

        if type == "builtin":
            self.background_builtin_title.tkraise()
            self.background_builtin.tkraise()

        if type == "youtube":
            self.background_youtube_title.tkraise()
            self.background_youtube.tkraise()

    # tts voice change
    def ttsVoiceChange(self, type):
        if type == "streamlabspolly":
            self.tts_streamlabs_polly_voice_title.tkraise()
            self.tts_streamlabs_polly_voice.tkraise()

        if type == "tiktok":
            self.tts_tiktok_voice_title.tkraise()
            self.tts_tiktok_voice.tkraise()

        if type == "googletranslate":
            self.tts_google_translate_voice_title.tkraise()
            self.tts_google_translate_voice.tkraise()

        if type == "awspolly":
            self.tts_aws_polly_voice_title.tkraise()
            self.tts_aws_polly_voice.tkraise()

        if type == "pyttsx":
            self.tts_python_voice_title.tkraise()
            self.tts_python_voice.tkraise()

    # Show frame
    def showFrame(self, frame):
        frame.tkraise()

    # Home button event
    def btn_home(self):
        self.showFrame(self.frame_home)

    # Settings button event
    def btn_settings(self):
        self.showFrame(self.frame_settings)

    # Results button event
    def btn_results(self):
        print("Results Pressed!")

    # Start button event
    def btn_start(self):
        self.saveSettings()
        start()
        print("Start Pressed!")

    # Appearance event
    def change_appearance_mode(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    # Close event
    def on_closing(self, event=0):
        self.saveSettings()
        self.destroy()
        shutdown()

def launchGui():
    if __name__ == "__main__":
        app = App()
        app.mainloop()

launchGui()