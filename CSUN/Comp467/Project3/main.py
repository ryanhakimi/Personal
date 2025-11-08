### project 3 vFxML ###
# get it? cuz FML means fuck my life, and its kinda in the project name? whatever...

#imports
import argparse
from pathlib import Path
import re
import subprocess

## functions ##

#renames the new file based on input and version num
def versionName(file, owner):
    path = Path(file)
    v_max = 0

    #print("Stem:", path.stem)
    #print("Suffix:", path.suffix)
    #print(f"Base:{path.stem}_VFX_{owner}_v01{path.suffix}")

    for f in path.parent.glob(f"{path.stem}_VFX_{owner}_v*{path.suffix}"):
        #print("Found:", f.name)
        v_curr = re.search(r"_v(\d{2})", f.name)
        if v_curr:
            v_curr = int(v_curr.group(1))
            if v_curr > v_max:
                v_max = v_curr
    
    v_next = v_max + 1
    return path.parent / f"{path.stem}_VFX_{owner}_v{v_next:02d}{path.suffix}"


import subprocess
from pathlib import Path

def watermark(file, owner):
    path = Path(file)
    output_path = versionName(file, owner)
    watermark_text = path.stem

    print("Input Path:", path)
    print("Output Path:", output_path)
    print("Watermark Text:", watermark_text)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(path),
        "-vf", f"drawtext=font='Arial':text='{watermark_text}':x=50:y=50:fontsize=200:fontcolor=black:bordercolor=white:borderw=15",
    ]

    if path.suffix.lower() in (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"):
        cmd.extend(["-frames:v", "1", "-update", "1"])

    cmd.append(str(output_path))
    subprocess.run(cmd, check=True)
    print("Watermarked file created:", output_path)

    return output_path


def thumbnail(file, owner):
    path = Path(file)
    output_path = versionName(file, owner)
    print("Input Path:", path)
    print("Output Path:", output_path)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(path),
        "-vf", "scale=320:180",
    ]

    if path.suffix.lower() in (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"):
        cmd.extend(["-frames:v", "1", "-update", "1"])

    cmd.append(str(output_path))
    subprocess.run(cmd, check=True)
    return output_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help = "enter file name or path")
    parser.add_argument("--owner", help = "define the owner")
    parser.add_argument("--watermark", action = "store_true", help = "add watermark")
    parser.add_argument("--gif", action = "store_true", help = "convert to gif")
    parser.add_argument("--thumbnail", action = "store_true", help = "extract thumbnail")
    parser.add_argument("--metadata", action = "store_true", help = "extract metadata")

    args = parser.parse_args()

    print("File:", args.file)
    print("Owner:", args.owner)
    print("Watermark:", args.watermark)
    print("Gif:", args.gif)
    print("Thumbnail:", args.thumbnail)
    print("Metadata:", args.metadata)

    new_name = versionName(args.file, args.owner)
    print("New file name:", new_name)

    if args.watermark:
        watermark(args.file, args.owner)
    
    if args.thumbnail:
        thumbnail(args.file, args.owner)

main()
