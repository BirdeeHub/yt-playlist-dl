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

def convert_video(input_file):
    base, ext = os.path.splitext(input_file)
    output_file = f"{base}_modified{ext}"
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

def main():
    parser = argparse.ArgumentParser(description="A simple CLI program.")
    
    # Adding required argument
    parser.add_argument('input_file', type=str, help="Input file to process")
    
    # Adding optional argument
    parser.add_argument('-o', '--output', type=str, help="Output directory", default="test_out")
    
    # Parse the arguments
    args = parser.parse_args()

    soup = BeautifulSoup(read_file(args.input_file), "html.parser")

    videos = [re.sub(r"&.*", "", item['href']) for item in soup.find_all("a", id="video-title")]

    temp_dir = tempfile.mkdtemp()
    temp_json = tempfile.mktemp()
    out_dir = args.output
    os.mkdir(out_dir)
    print(f"{out_dir}")
    i = 1
    length = len(videos)
    for link in videos:
        try:
            print(f"Downloading {link} {i}/{length}")
            os.system(f"yt-dlp -j --no-simulate -P {temp_dir} {link} > {temp_json}")
        except Exception as e:
            print(f"Failed to download {link}: {e}")

        filename = json.loads(read_file(temp_json))['filename']
        print(f"Converting {filename}")
        outfile = convert_video(filename)
        os.remove(filename)
        shutil.move(outfile, out_dir)
        i += 1

    os.system(f"ls {out_dir}")
    os.remove(temp_json)
    os.system(f"rm -rf {temp_dir}")
    print("done")

if __name__ == "__main__":
    main()
