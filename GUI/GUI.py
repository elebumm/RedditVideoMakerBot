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

        # frame_home
        self.frame_config(self.frame_home)
        # frame_settings
        self.frame_settings.rowconfigure(0)
        self.frame_settings.columnconfigure(0)
        # frame_results
        self.frame_config(self.frame_results)

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
        self.user_title.grid(row=1, column=0, columnspan=2)

        # Client secret input box
        self.client_secret = customtkinter.CTkEntry(
            master=self.frame_bg_settings,
            placeholder_text = "Client Secret"
        )
        self.client_secret.grid(row=2, column=0, pady=5, padx=15)

        # Client id input box
        self.client_id = customtkinter.CTkEntry(
            master=self.frame_bg_settings,
            placeholder_text = "Client Id"
        )
        self.client_id.grid(row=3, column=0, pady=5, padx=15)

        # Username
        self.user_name = customtkinter.CTkEntry(
            master=self.frame_bg_settings,
            placeholder_text = "Username"
        )
        self.user_name.grid(row=2, column=1, pady=5, padx=15)

        # Password
        self.user_password = customtkinter.CTkEntry(
            master=self.frame_bg_settings,
            placeholder_text = "Password"
        )
        self.user_password.grid(row=3, column=1, pady=5, padx=15)

        # 2fa label
        self.user_2fa_label = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text = "2FA enabled?"
        )
        self.user_2fa_label.grid(row=4, column=0, pady=0, padx=15)

        # 2fa option menu
        self.user_2fa = customtkinter.CTkOptionMenu(
            master=self.frame_bg_settings,
            values=["True", "False"]
        )
        self.user_2fa.grid(row=5, column=0, pady=0, padx=15)

## THREAD SETTINGS

        # Thread Settings Title
        self.thread_title = customtkinter.CTkLabel(
            master=self.frame_bg_settings,
            text="Thread Settings",
            text_font=("Courier_Bold", 14)
        )
        self.thread_title.grid(row=1, column=3, columnspan=2)

        # Subreddit
        self.thread_subreddit = customtkinter.CTkEntry(
            master=self.frame_bg_settings,
            placeholder_text="Subreddit"
        )
        self.thread_subreddit.grid(row=2, column=3, pady=15, padx=15)

        # Max Comment Lenght
        self.thread_max_comment_lenght = customtkinter.CTkEntry(
            master=self.frame_bg_settings,
            placeholder_text="Max Comment Lenght"
        )
        self.thread_max_comment_lenght.grid(row=2, column=4, pady=15, padx=15)

        # Post Id
        self.thread_post_id = customtkinter.CTkEntry(
            master=self.frame_bg_settings,
            placeholder_text="Post Id"
        )
        self.thread_post_id.grid(row=3, column=3, pady=15, padx=15)

        # Min Comment Lenght
        self.thread_min_comment_lenght = customtkinter.CTkEntry(
            master=self.frame_bg_settings,
            placeholder_text="Min Comment Lenght"
        )
        self.thread_min_comment_lenght.grid(row=3, column=4, pady=15, padx=15)



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

    # Configures the frames of the right side
    def frame_config(self, frame):
            frame.rowconfigure(8, weight=1)
            frame.columnconfigure(8, weight=10)

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