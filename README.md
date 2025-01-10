A script to fill overlapping needs me and a friend had regarding downloading from youtube playlists

I wanted to watch videos/listen to podcasts on a laptop with no wifi.

he needed a playlist without its audio.

uses yt-dlp and ffmpeg to do the downloading and converting

uses beautifulsoup4 to parse the html to get the videos in the playlist from the page

Packaged for nix package manager via a flake.

If you do not have nix package manager, you will need to install these dependencies to run the script successfully

This is a VERY simple script, with subpar error handling and user feedback.

It is also likely that youtube will change their page layouts in the future and break this script

### Dependencies

- python3
- beautifulsoup4
- ffmpeg-python
- yt-dlp

### Usage

go to your youtube playlists and click view full playlist.

right click on the page and click "save page as"

run the script on that file

```bash
python3 ./main.py thatfile.html [-h] [-o OUTPUT] [-na] [-nv] input_file

download the html page with the playlist as input file, download the video and strip audio of all videos

positional arguments:
  input_file            Input file to process

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output directory
  -na, --no-sound       whether to strip audio
  -nv, --no-video       whether to strip video
```
