import json
import random
from tkinter import StringVar, filedialog, messagebox, ttk
from typing import TypedDict, cast

import yt_dlp
from youtube_search import YoutubeSearch

from bpm import SAMPLE_RATE, analyze_audio, compute_bpm
from utils import create_entry_with_button, format_views


class YoutubeSearchResults(TypedDict):
    title: str
    channel: str
    duration: str
    views: str
    id: str


def get_search_results(
    search: str, search_table: ttk.Treeview, download_table: ttk.Treeview
) -> None:
    results = cast(
        list[YoutubeSearchResults], YoutubeSearch(search, max_results=10).to_dict()
    )
    search_table.delete(*search_table.get_children())  # Clear previous results

    search_table.bind(
        "<Double-1>",
        lambda _: download_table.insert(
            "",
            "end",
            values=search_table.item(search_table.selection())["values"],  # ty:ignore[no-matching-overload]
        ),
    )
    download_table.bind(
        "<Double-1>",
        lambda _: download_table.delete(download_table.selection()),  # ty:ignore[invalid-argument-type]
    )

    for result in results:
        values = (
            result["title"],
            result["channel"],
            result["duration"],
            format_views(result["views"]),
            result["id"],
        )
        search_table.insert("", "end", values=values)


def create_results_table(frame: ttk.Frame, label_text: str) -> ttk.Treeview:
    table_label = ttk.Label(frame, text=label_text)
    table_label.pack(anchor="w", padx=10, pady=(10, 0))
    table = ttk.Treeview(
        frame, columns=("Title", "Channel", "Duration", "Views"), show="headings"
    )
    table.column("Title", width=400)
    table.column("Channel", width=200)
    table.column("Duration", width=60)
    table.column("Views", width=60)
    table.heading("Title", text="Title")
    table.heading("Channel", text="Channel")
    table.heading("Duration", text="Duration")
    table.heading("Views", text="Views")
    table.pack(anchor="w", fill="both", expand=True, padx=10, pady=(5, 10))
    return table


def download_selected_songs(
    download_table: ttk.Treeview,
    progress: ttk.Progressbar,
    label: ttk.Label,
    frame: ttk.Frame,
    tab: ttk.Frame,
    songs_folder: StringVar,
) -> None:
    rows = [
        cast(tuple[str, str, str, str, str], download_table.item(row)["values"])
        for row in download_table.get_children()
    ]
    if not rows:
        print("No songs selected for download.")
        return

    FORMAT = "ogg"

    for row in rows:
        name = row[0]
        channel = row[1]
        url = f"https://www.youtube.com/watch?v={row[4]}"
        folder = f"{songs_folder.get()}/{name}"
        song_path = f"{folder}/Audio"

        label.config(text=f"Downloading {name}...")
        frame.update_idletasks()

        ydl_opts = {
            "quiet": True,
            "format": f"{FORMAT}/bestaudio/best",
            "outtmpl": song_path,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "vorbis",
                    "preferredquality": "192",  # bitrate in kbps (optional)
                }
            ],
            "extractor-args": "youtube:player_js_version=actual",
            "postprocessor_args": {
                # sample rate + EBU R128 loudness normalization to -14 LUFS → ffmpeg
                "extractaudio": [
                    "-ar",
                    str(SAMPLE_RATE),
                    "-af",
                    "loudnorm=I=-14:TP=-1:LRA=11",
                ],
            },
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            error_code = ydl.download([url])
            if error_code:
                messagebox.showerror(
                    "Download Error",
                    f"Failed to download {name}. Please check the URL or your internet connection.",
                )
                continue

            leading, trailing, _ = analyze_audio(f"{song_path}.{FORMAT}")

            bpm = compute_bpm(f"{song_path}.{FORMAT}")

            meta = {
                "version": 1,
                "uniqueId": random.randint(100000000, 999999999),
                "songName": name,
                "performedBy": [channel],
                "writtenBy": [channel],
                "seed": random.randint(100000000, 999999999),
                "tempo": round(bpm, 2),
                "customTempoSections": [],
                "beatOffset": round(leading * 1000),
                "startSongOffset": round(leading, 3),
                "endSongOffset": round(trailing, 3),
                "uEAssetName": name,
                "originalAudioFileHash": "",
                "originalAudioFilePath": "",
            }

            with open(f"{folder}/Meta.json", "w") as f:
                json.dump(meta, f, indent=2)

            progress["value"] += 100 / len(rows)
            frame.update_idletasks()

    frame.destroy()  # Close the add song frame
    create_add_frame(tab=tab, songs_folder=songs_folder)  # Recreate the add song frame
    messagebox.showinfo("Download Complete", "All songs downloaded successfully!")


def create_add_frame(tab: ttk.Frame, songs_folder: StringVar) -> None:
    add_frame = ttk.Frame(tab)
    add_frame.pack(fill="both", expand=True)

    create_entry_with_button(
        frame=add_frame,
        entry_var=songs_folder,
        entry_state="readonly",
        button_text="Change Folder",
        button_command=lambda: songs_folder.set(
            filedialog.askdirectory(
                initialdir=songs_folder.get(),
                title="Select Folder",
                mustexist=True,
                parent=add_frame,
            )
        ),
        label_text="Import folder",
    )

    search_value = StringVar()
    create_entry_with_button(
        frame=add_frame,
        entry_var=search_value,
        button_text="Search",
        button_command=lambda: get_search_results(
            search_value.get(), search_table, download_table
        ),
        label_text="Search for a song to add:",
    )

    search_table = create_results_table(
        add_frame, "Double-click a song to add it to the download list:"
    )
    download_table = create_results_table(
        add_frame, "Double-click a song to remove it from the download list:"
    )

    download_label = ttk.Label(add_frame, text="")
    download_label.pack(anchor="w", padx=10, pady=(10, 0))
    download_progress = ttk.Progressbar(
        add_frame, orient="horizontal", mode="determinate"
    )
    download_progress.pack(fill="x", padx=10, pady=(0, 10))

    download_button = ttk.Button(
        add_frame,
        text="Download Songs",
        command=lambda: download_selected_songs(
            download_table=download_table,
            progress=download_progress,
            label=download_label,
            frame=add_frame,
            tab=tab,
            songs_folder=songs_folder,
        ),
    )
    download_button.pack(pady=10)
