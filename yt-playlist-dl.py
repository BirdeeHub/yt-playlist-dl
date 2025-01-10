from bs4 import BeautifulSoup
import ffmpeg

import argparse
import tempfile
import json
import os
import re
import shutil

def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except IOError as e:
        raise IOError(f"An error occurred while reading the file: {e}")

def strip_video(input_file):
    base, ext = os.path.splitext(input_file)
    output_file = f"{base}_audio_only{ext}"
    try:
        (
            ffmpeg
            .input(input_file)
            .output(output_file, vn=None, acodec='copy')  # Remove video, copy audio
            .run(overwrite_output=True)
        )
        print(f"Conversion successful: {output_file}")
        return output_file
    except ffmpeg.Error as e:
        print(f"Error during conversion: {e.stderr.decode()}")
        raise

def strip_audio(input_file):
    base, ext = os.path.splitext(input_file)
    output_file = f"{base}_video_only{ext}"
    try:
        (
            ffmpeg
            .input(input_file)
            .output(output_file, an=None, vcodec='copy')
            .run(overwrite_output=True)
        )
        print(f"Conversion successful: {output_file}")
        return output_file
    except ffmpeg.Error as e:
        print(f"Error during conversion: {e.stderr.decode()}")
        raise

# ffmpeg_func recieves an input_file and returns a DIFFERENT output_file
def download_and_ffmpeg(out_dir, link, ffmpeg_func):
    temp_dir = tempfile.mkdtemp()
    temp_json = tempfile.mktemp()
    try:
        print(f"Downloading {link} sorry for the lack of progress indicator")
        os.system(f"yt-dlp -j --no-simulate -P {temp_dir} {link} > {temp_json}")
    except Exception as e:
        print(f"Failed to download {link}: {e}")

    filename = json.loads(read_file(temp_json))['filename']
    os.remove(temp_json)
    print(f"Converting {filename}")
    outfile = ffmpeg_func(filename)
    shutil.move(outfile, out_dir)
    os.remove(filename)
    shutil.rmtree(temp_dir)

def download_only(out_dir, link):
    try:
        print(f"Downloading {link} ")
        os.system(f"yt-dlp -P {out_dir} {link}")
    except Exception as e:
        print(f"Failed to download {link}: {e}")

def main():
    parser = argparse.ArgumentParser(description="an extremely simple script for downloading youtube playlists")
    # Adding required argument
    parser.add_argument('input_file', type=str, help="Input file to process")
    # Adding optional argument
    parser.add_argument('-o', '--output', type=str, help="Output directory", default=".")
    parser.add_argument('-na', '--no-sound', action='store_true', help="whether to strip audio", default=False)
    parser.add_argument('-nv', '--no-video', action='store_true', help="whether to strip video", default=False)
    # Parse the arguments
    args = parser.parse_args()

    soup = BeautifulSoup(read_file(args.input_file), "html.parser")
    videos = [
        re.sub(r"&.*", "", item['href'])
        for item in soup.select("a#video-title")
        if "style-scope" in item.find_parent().get("class", [])
        and "ytd-playlist-video-renderer" in item.find_parent().get("class", [])
    ]

    out_dir = args.output
    try:
        os.mkdir(out_dir)
        print(f"{out_dir}")
    except Exception as e:
        print(f"Could not create {out_dir} due to: {e}")

    i = 1
    length = len(videos)
    for link in videos:
        print(f"{i}/{length}")
        i += 1
        if args.no_sound:
            download_and_ffmpeg(out_dir, link, strip_audio)
        if args.no_video:
            download_and_ffmpeg(out_dir, link, strip_video)
        else:
            download_only(out_dir, link)

    print("done")

if __name__ == "__main__":
    main()
