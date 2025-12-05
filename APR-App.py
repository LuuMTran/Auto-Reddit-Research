from customtkinter import *
import undetected_chromedriver as uc
import time
import pandas as pd
from utils.full_automa import *


class ToplevelWindowAutomata(CTkToplevel):
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.title = "Automatic Mode"
        self.geometry("400x300")
        full_pipeline_start()


class ToplevelWindowMannual(CTkToplevel):
    def __init__(self, master=None, url=r"https://www.reddit.com", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.geometry("400x300")
        self.df = pd.DataFrame(columns=["Topic", "Comment"])
        self.html_visit = set()
        self.title = "Mannual Mode"
        self.driver = uc.Chrome(headless=False, use_subprocess=False, version_main=142)
        self.btn = CTkButton(
            master=self,
            text="Capture Comment",
            corner_radius=32,
            fg_color="#4158D0",
            hover_color="#0019FC",
            border_color="#FFCC70",
            border_width=2,
            command=self.capture_comment,
        )
        self.btn_save = CTkButton(
            master=self,
            text="Save Comment",
            corner_radius=32,
            fg_color="#4158D0",
            hover_color="#0019FC",
            border_color="#FFCC70",
            border_width=2,
            command=self.save_comment,
        )
        self.btn.place(relx=0.5, rely=0.5, anchor="center")
        self.btn_save.place(relx=0.5, rely=0.6, anchor="center")
        self.geturl(url)
    def save_comment(self):
        self.df.to_csv(r"./checkpoints/comment_data.csv", header=False)

    def geturl(self, url):
        if not isinstance(url, str):
            url = r"https://www.reddit.com"
        self.driver.get(url)
        time.sleep(1)
        self.driver.get(url)

    def capture_comment(self):
        current_url = self.driver.current_url
        source = self.driver.page_source
        if current_url not in self.html_visit:
            try:
                topic, comments = get_comment1(source)
                store_comment(df=self.df, topic=topic, comments=comments)
                self.html_visit.add(current_url)
            except:
                print("Error, topic and comments not found")
        else:
            print("Page visited")


class App(CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.toplevel_window = None
        self.geometry("500x400")
        self.frame = CTkFrame(
            master=self, fg_color="#8D6F3A", border_color="#FFCC70", border_width=2
        )
        self.frame.pack(expand=True)
        self.btn = CTkButton(
            master=self.frame,
            text="Autonomous mode",
            corner_radius=32,
            fg_color="#4158D0",
            hover_color="#0019FC",
            border_color="#FFCC70",
            border_width=2,
            command=self.open_toplevel_automatic,
        )
        self.btn2 = CTkButton(
            master=self.frame,
            text="Manual Mode",
            corner_radius=32,
            fg_color="#4158D0",
            hover_color="#0019FC",
            border_color="#FFCC70",
            border_width=2,
            command=self.open_toplevel_mannual,
        )

        self.btn.pack(anchor="s", expand=True, pady=10, padx=30)
        self.btn2.pack(anchor="s", expand=True, pady=10, padx=30)

    def open_toplevel_mannual(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ToplevelWindowMannual(self)
        else:
            self.toplevel_window.focus()

    def open_toplevel_automatic(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():

            self.toplevel_window = ToplevelWindowAutomata(self)
        else:
            self.toplevel_window.focus()


if __name__ == "__main__":
    app = App()
    app.title("Auto Reddit Research")
    app.mainloop()
