from utils import clear_terminal
import os
import cutie
import shutil


def remove_song(songs_folder):
    if not os.path.exists(songs_folder):
        print("No songs folder found.")
        return

    song_dirs = [
        d
        for d in os.listdir(songs_folder)
        if os.path.isdir(os.path.join(songs_folder, d))
    ]
    if not song_dirs:
        print("No songs available to remove.")
        return

    try:
        remove_song_indices = cutie.select_multiple(song_dirs)
        clear_terminal()
    except KeyboardInterrupt:
        exit(0)

    for index in remove_song_indices:
        selected_song = song_dirs[index]
        song_path = os.path.join(songs_folder, selected_song)
        if os.path.exists(song_path):
            shutil.rmtree(song_path)
            print(f"Removed {selected_song}.")
