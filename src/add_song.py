import random
import json

import cutie
import yt_dlp
from youtube_search import YoutubeSearch

from bpm import analyze_audio, compute_bpm, SAMPLE_RATE
from utils import clear_terminal

def add_song(songs_folder):
  try:
      video_list = []
      add_song_to_video_list = True

      while add_song_to_video_list:
        search = input("Search for a song: ")
        results = YoutubeSearch(search, max_results=10).to_dict()
        titles = [
            f"{result['title']} [{result['channel']}] [{result['duration']}] [{result['views']}]"
            for result in results
        ]
        video = results[cutie.select(titles)]
        video_list.append(video)
        add_song_to_video_list = cutie.prompt_yes_or_no("Add another song?")
        clear_terminal()
        print(f"Songs to be downloaded: {[video['title'] for video in video_list]}\n")
  except KeyboardInterrupt:
      exit(0)

  FORMAT = "ogg"

  for video in video_list:
    name = video["title"]
    url = f"https://www.youtube.com/watch?v={video['id']}"
    folder = f"{songs_folder}/{name}"
    song_path = f"{folder}/Audio"

    clear_terminal()
    print(f"Downloading {name}...")

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
            "extractaudio": ["-ar", str(SAMPLE_RATE)],  # sample rate → ffmpeg
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
          "originalAudioFilePath": ""
        }

        with open(f"{folder}/Meta.json", "w") as f:
            json.dump(meta, f, indent=2)

  print("All songs downloaded successfully!")
