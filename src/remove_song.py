import os
import shutil
from tkinter import Listbox, StringVar, ttk


def get_songs(songs_folder: StringVar) -> list[str]:
    if not os.path.exists(songs_folder.get()):
        print("No songs folder found.")
        return []

    song_dirs = [
        d
        for d in os.listdir(songs_folder.get())
        if os.path.isdir(os.path.join(songs_folder.get(), d))
    ]
    return song_dirs


def create_remove_frame(tab: ttk.Frame, songs_folder: StringVar) -> None:
    songs_label = ttk.Label(tab, text="Select songs to remove:")
    songs_label.pack(pady=10)

    songs_list = Listbox(tab, selectmode="multiple")
    songs = get_songs(songs_folder)
    for song in songs:
        songs_list.insert("end", song)
    songs_list.pack(fill="both", expand=True, padx=10)

    remove_song_button = ttk.Button(
        tab,
        text="Remove Selected Songs",
        command=lambda: remove_selected_songs(songs_list, songs_folder),
    )
    remove_song_button.pack(pady=10)


def remove_selected_songs(songs_list: Listbox, songs_folder: StringVar) -> None:
    selected_indices = songs_list.curselection()
    for index in selected_indices:
        selected_song = songs_list.get(index)
        song_path = os.path.join(songs_folder.get(), selected_song)
        if os.path.exists(song_path):
            shutil.rmtree(song_path)
            songs_list.delete(index)
