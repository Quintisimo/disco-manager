from utils import clear_terminal
import cutie

from add_song import add_song
from remove_song import remove_song

songs_folder = "songs"

options = [
  "Add song",
  "Remove song"
]

try:
  selected_option = options[cutie.select(options)]
  clear_terminal()
except KeyboardInterrupt:
  exit(0)

if selected_option == "Add song":
  add_song(songs_folder)
elif selected_option == "Remove song":
  remove_song(songs_folder)
else:
  print("Invalid option selected.")
