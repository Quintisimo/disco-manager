from utils import print_with_banner
import cutie

from add_song import add_song
from remove_song import remove_song

try:
    songs_folder = "songs"

    options = ["Add song", "Remove song"]

    selected_option = print_with_banner(lambda: options[cutie.select(options)])

    if selected_option == "Add song":
        add_song(songs_folder)
    elif selected_option == "Remove song":
        remove_song(songs_folder)
    else:
        print("Invalid option selected.")
except KeyboardInterrupt:
    exit(0)
