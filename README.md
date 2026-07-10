# Disco Manager

A simple wrapper around [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [ffmpeg](https://ffmpeg.org/) to manage your custom songs for [Dead As Disco](https://deadasdisco.com/).

## Features

- Search and download songs from YouTube, detect the bpm and automatically add them to the game.
- Delete custom songs from the game.

## IMPORT_SONGS_PATH

This changes based on the os you are using:

- Windows: `%localappdata%/Pagoda/Saved/ImportedSongs`
- Linux: run `find ~/.local/share/Steam/steamapps/compatdata -type d -name ImportedSongs` to find the path

Run the cli:

The game should not be running when you run the CLI.

```bash
  # Can also use podman if you prefer
  docker run --privileged --rm -it -v "IMPORT_SONGS_PATH:/app/songs" ghcr.io/quintisimo/disco-manager:latest
```
