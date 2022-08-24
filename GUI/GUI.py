#from main import main, shutdown

from doctest import master
import tkinter
import tkinter.messagebox
import customtkinter

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
        self.resizable(False, False)

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

### Adds all the stuff for frame_settings ###

        # Background within frame
        self.frame_bg_settings = customtkinter.CTkFrame(master=self.frame_settings)
        self.frame_bg_settings.grid(row=0, column=0, pady=15, padx=15, sticky=("nswe"))

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
            values=["False", "True"]
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
            values=["False", "True"]
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
            text="Max comment length"
        )
        self.thread_max_comment_length_title.grid(row=4, column=3, padx=15)

    # Max comment length
        self.thread_max_comment_length = customtkinter.CTkEntry(
            master=self.frame_bg_settings,
            placeholder_text="Max comment length (NUM)"
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

        self.progressbar = customtkinter.CTkProgressBar(master=self.frame_info)
        self.progressbar.grid(row=1, column=0, sticky="ew", padx=15, pady=15)

        
        # set default values
        self.optionmenu_1.set("Dark")
        ###self.button_3.configure(state="disabled", text="Disabled CTkButton")
        ###self.combobox_1.set("CTkCombobox")
        ###self.radio_button_1.select()
        ###self.slider_1.set(0.2)
        ###self.slider_2.set(0.7)
        ###self.progressbar.set(0.5)
        ###self.switch_2.select()
        ###self.radio_button_3.configure(state=tkinter.DISABLED)
        ###self.check_box_1.configure(state=tkinter.DISABLED, text="CheckBox disabled")
        ###self.check_box_2.select()

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
        print("Start Pressed!")

    # Appearance event
    def change_appearance_mode(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    # Close event
    def on_closing(self, event=0):
        self.destroy()
        shutdown()

def start():
    if __name__ == "__main__":
        app = App()
        app.mainloop()

start()