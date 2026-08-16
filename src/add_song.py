from typing import TypedDict, cast
from tkinter import ttk, messagebox, StringVar
import random
import json

import cutie
import yt_dlp
from youtube_search import YoutubeSearch

from bpm import analyze_audio, compute_bpm, SAMPLE_RATE
from utils import print_with_banner, format_views

class YoutubeSearchResults(TypedDict):
    title: str
    channel: str
    duration: str
    views: str
    id: str

def get_search_results(search: str, search_table: ttk.Treeview, download_table: ttk.Treeview):
    results = cast(list[YoutubeSearchResults], YoutubeSearch(search, max_results=10).to_dict())
    search_table.delete(*search_table.get_children())  # Clear previous results

    search_table.bind("<Double-1>", lambda _: download_table.insert("", "end", values=search_table.item(search_table.selection())["values"]))  # ty:ignore[no-matching-overload]
    download_table.bind("<Double-1>", lambda _: download_table.delete(download_table.selection()))  # ty:ignore[invalid-argument-type]

    for result in results:
        values = (result['title'], result['channel'], result['duration'], format_views(result['views']), result['id'])
        search_table.insert("", "end", values=values)

def create_results_table(frame: ttk.Frame, label_text: str) -> ttk.Treeview:
  table_label = ttk.Label(frame, text=label_text)
  table_label.pack(anchor='w', padx=10, pady=(10, 0))
  table = ttk.Treeview(frame, columns=("Title", "Channel", "Duration", "Views"), show='headings')
  table.column("Title", width=400)
  table.column("Channel", width=200)
  table.column("Duration", width=60)
  table.column("Views", width=60)
  table.heading("Title", text="Title")
  table.heading("Channel", text="Channel")
  table.heading("Duration", text="Duration")
  table.heading("Views", text="Views")
  table.pack(anchor='w', fill='both', expand=True, padx=10, pady=(5, 10))
  return table

def download_selected_songs(download_table: ttk.Treeview, progress: ttk.Progressbar, label: ttk.Label, frame: ttk.Frame, tab: ttk.Frame, songs_folder: str):
    rows = [cast(tuple[str, str, str, str, str], download_table.item(row)["values"]) for row in download_table.get_children()]
    if not rows:
        print("No songs selected for download.")
        return

    FORMAT = "ogg"

    for row in rows:
        name = row[0]
        channel = row[1]
        url = f"https://www.youtube.com/watch?v={row[4]}"
        folder = f"{songs_folder}/{name}"
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
                print(f"Download failed with error code: {error_code}")
                exit(1)

            leading, trailing, duration = analyze_audio(f"{song_path}.{FORMAT}")

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

            progress['value'] += 100 / len(rows)
            frame.update_idletasks()

    frame.destroy()  # Close the add song frame
    create_add_frame(tab)  # Recreate the add song frame
    messagebox.showinfo("Download Complete", "All songs downloaded successfully!")

def create_add_frame(tab: ttk.Frame):
  add_frame = ttk.Frame(tab)
  add_frame.pack(fill='both', expand=True)

  label = ttk.Label(add_frame, text="Search for a song to add:")
  label.pack(anchor='w', padx=10)

  search_row = ttk.Frame(add_frame)
  search_row.pack(fill='x', padx=10, pady=5)

  search_value = StringVar()
  search_input = ttk.Entry(search_row, textvariable=search_value)
  search_input.pack(side='left', fill='x', expand=True)
  search_button = ttk.Button(search_row, text="Search", command=lambda: get_search_results(search_value.get(), search_table, download_table))
  search_button.pack(side='left', padx=(5, 0))

  search_table = create_results_table(add_frame, "Double-click a song to add it to the download list:")
  download_table = create_results_table(add_frame, "Double-click a song to remove it from the download list:")

  download_label = ttk.Label(add_frame, text="")
  download_label.pack(anchor='w', padx=10, pady=(10, 0))
  download_progress = ttk.Progressbar(add_frame, orient='horizontal', mode='determinate')
  download_progress.pack(fill='x', padx=10, pady=(0, 10))

  download_button = ttk.Button(add_frame, text="Download Songs", command=lambda: download_selected_songs(
    download_table=download_table, progress=download_progress, label=download_label, frame=add_frame, tab=tab, songs_folder="songs"))
  download_button.pack(pady=10)

def add_song(songs_folder):
    video_list = []
    add_song_to_video_list = True

    def print_with_video_list(func):
        print_with_banner(
            lambda: print(
                f"Songs to be downloaded: {[video['title'] for video in video_list]}\n"
                if video_list
                else "\r",
                end="\n" if video_list else "",
            )
        )
        return func()

    while add_song_to_video_list:
        search = print_with_video_list(lambda: input("Search for a song: "))
        results = YoutubeSearch(search, max_results=10).to_dict()
        titles = [
            f"{result['title']} [{result['channel']}] [{result['duration']}] [{format_views(result['views'])}]"
            for result in results
        ]

        try:
            print_with_video_list(
                lambda: print(
                    "Select a song from the list below or <Ctrl+C> to search again:\n\nFormat: Title [Channel] [Duration] [views]"
                )
            )
            video = results[cutie.select(titles)]
            video_list.append(video)
        finally:
            add_song_to_video_list = print_with_video_list(
                lambda: cutie.prompt_yes_or_no("Add another song?")
            )
            continue

    if not video_list:
        print("No songs selected. Exiting.")
        return

    FORMAT = "ogg"

    for video in video_list:
        name = video["title"]
        url = f"https://www.youtube.com/watch?v={video['id']}"
        folder = f"{songs_folder}/{name}"
        song_path = f"{folder}/Audio"

        print_with_banner(lambda: print(f"Downloading {name}..."))

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
                print(f"Download failed with error code: {error_code}")
                exit(1)

            leading, trailing, duration = analyze_audio(f"{song_path}.{FORMAT}")

            bpm = compute_bpm(f"{song_path}.{FORMAT}")

            meta = {
                "version": 1,
                "uniqueId": random.randint(100000000, 999999999),
                "songName": name,
                "performedBy": [video["channel"]],
                "writtenBy": [video["channel"]],
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

    print("All songs downloaded successfully!")
