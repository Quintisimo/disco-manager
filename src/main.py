import os
import subprocess
from tkinter import PhotoImage, StringVar, Tk, ttk

from add_song import create_add_frame
from remove_song import create_remove_frame
from utils import is_bundle, resource_path

root = Tk()
root.title("Disco Manager")
# https://www.flaticon.com/free-icon/vinyl_812629?term=record&related_id=812629
photo = PhotoImage(file=resource_path("vinyl.png"))
root.wm_iconphoto(False, photo)

songs_default_folder = "./songs"

if is_bundle():
    if os.name == "nt":
        songs_default_folder = os.path.expandvars(
            "%localappdata%/Pagoda/Saved/ImportedSongs"
        )
    else:
        songs_default_folder = subprocess.run(
            "find ~/.local/share/Steam/steamapps/compatdata -type d -name ImportedSongs",
            shell=True,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

songs_folder = StringVar(value=songs_default_folder)

tab_control = ttk.Notebook(root)

add_tab = ttk.Frame(tab_control)
create_add_frame(tab=add_tab, songs_folder=songs_folder)
tab_control.add(add_tab, text="Add Song")

remove_tab = ttk.Frame(tab_control)
create_remove_frame(tab=remove_tab, songs_folder=songs_folder)
tab_control.add(remove_tab, text="Remove Song")

tab_control.pack(expand=1, fill="both")

root.mainloop()
