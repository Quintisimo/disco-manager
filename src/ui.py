import platform
import subprocess
from os import path
from tkinter import StringVar, Tk, ttk

from add_song import create_add_frame

root = Tk()
root.title("Disco Manager")

songs_default_folder = "songs"

if platform.system() == "Windows":
  songs_default_folder = path.expandvars("%localappdata%/Pagoda/Saved/ImportedSongs")
elif platform.system() == "Linux":
  songs_default_folder = subprocess.run("find ~/.local/share/Steam/steamapps/compatdata -type d -name ImportedSongs", shell=True, capture_output=True, text=True, check=True).stdout.strip()

songs_folder = StringVar(value=songs_default_folder)

tab_control = ttk.Notebook(root)

add_tab = ttk.Frame(tab_control)
create_add_frame(tab=add_tab, songs_folder=songs_folder)

tab_control.add(add_tab, text='Add Song')




remove_tab = ttk.Frame(tab_control)
tab_control.add(remove_tab, text='Remove Song')

tab_control.pack(expand=1, fill='both')

root.mainloop()
