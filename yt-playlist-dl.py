from bs4 import BeautifulSoup
import ffmpeg

import argparse
import tempfile
import json
import os
import re
import shutil

def strip_video(input_file):
    base, ext = os.path.splitext(input_file)
    output_file = f"{base}_audio_only{ext}"
    try:
        (
            ffmpeg
            .input(input_file)
            .output(output_file, vn=None, acodec='copy') # Remove video, copy audio
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
            .output(output_file, an=None, vcodec='copy') # Remove audio, copy video
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
        print(f"Downloading {link}. Sorry for the lack of progress indicator.")
        os.system(f"yt-dlp -j --no-simulate -P {temp_dir} {link} > {temp_json}")
        with open(temp_json, 'r') as json_file:
            filename = json.load(json_file)['filename']
        print(f"Converting {filename}")
        outfile = ffmpeg_func(filename)
        shutil.move(outfile, out_dir)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if os.path.exists(temp_json):
            os.remove(temp_json)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def download_only(out_dir, link):
    try:
        print(f"Downloading {link} ")
        os.system(f"yt-dlp -P {out_dir} {link}")
    except Exception as e:
        print(f"Failed to download {link}: {e}")

def main():
    parser = argparse.ArgumentParser(description="an extremely simple script for downloading youtube playlists")
    # required argument
    parser.add_argument('input_file', type=str, help="Input file to process")
    # optional arguments
    parser.add_argument('-o', '--output', type=str, help="Output directory", default=".")
    parser.add_argument('-na', '--no-sound', action='store_true', help="whether to strip audio", default=False)
    parser.add_argument('-nv', '--no-video', action='store_true', help="whether to strip video", default=False)
    args = parser.parse_args()

    try:
        with open(args.input_file, 'r') as file:
            soup = BeautifulSoup(file.read(), "html.parser")

        videos = [
            re.sub(r"&.*", "", item['href'])
            for item in soup.select("a#video-title")
            if "style-scope" in item.find_parent().get("class", [])
            and "ytd-playlist-video-renderer" in item.find_parent().get("class", [])
        ]

        out_dir = args.output
        if not os.path.exists(out_dir):
            try:
                print(f"Creating output directory: {out_dir}")
                os.mkdir(out_dir)
            except Exception as e:
                print(f"Could not create {out_dir} due to: {e}")
                raise

        i = 1
        length = len(videos)
        for link in videos:
            print(f"{i}/{length}")
            i += 1
            if args.no_sound:
                download_and_ffmpeg(out_dir, link, strip_audio)
            elif args.no_video:
                download_and_ffmpeg(out_dir, link, strip_video)
            else:
                download_only(out_dir, link)

    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except IOError as e:
        raise IOError(f"An error occurred while reading the file: {e}")

    print("done")

if __name__ == "__main__":
    main()
