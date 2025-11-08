### project 3 vFxML ###
# get it? cuz FML means fuck my life, and its kinda in the project name?
# whatever...

## imports ##
import argparse
from pathlib import Path
import re
import subprocess

## functions ##

# renames the new file based on input and version num
def versionName(file, owner, out_suffix=None):
    path = Path(file)
    ext = out_suffix if out_suffix is not None else path.suffix

    # these two lines are AI generated not gonna lie
    # i just needed a quick fix for double named files
    # this removes any trailing so the name is consistent
    m = re.match(r"^(?P<base>.+)_VFX_[^_]+_v\d{2}$", path.stem)
    base_stem = m.group("base") if m else path.stem

    # find latest version
    v_max = 0
    for f in path.parent.glob(f"{base_stem}_VFX_{owner}_v*{ext}"):
        m2 = re.search(r"_v(\d{2})", f.name)
        if m2:
            v_max = max(v_max, int(m2.group(1)))

    # inc v
    v_next = v_max + 1
    return path.parent / f"{base_stem}_VFX_{owner}_v{v_next:02d}{ext}"


# adds watermark to file
def addWatermark(file, owner):
    path = Path(file)

    # for gif files
    if path.suffix.lower() == ".gif":
        output_path = versionName(file, owner, ".gif")
    
    # for other files
    else:
        output_path = versionName(file, owner, out_suffix = path.suffix)
        
    watermark_text = path.stem

    print("Input Path:", path)
    print("Output Path:", output_path)
    print("Watermark Text:", watermark_text)

    # color handling for gif
    if path.suffix.lower() == ".gif":
        cmd = [
            "ffmpeg", "-y",
            "-i", str(path),
            "-filter_complex",
            f"[0:v]drawtext=font='Arial':text='{watermark_text}':x=50:y=50:fontsize=200:fontcolor=black:bordercolor=white:borderw=15,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
            str(output_path)
        ]
    # color handling for image
    else:
        cmd = [
            "ffmpeg", "-y",
            "-i", str(path),
            "-vf", f"drawtext=font='Arial':text='{watermark_text}':x=50:y=50:fontsize=200:fontcolor=black:bordercolor=white:borderw=15",
        ]

        # set a 1 frame limit
        if path.suffix.lower() in (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"):
            cmd.extend(["-frames:v", "1", "-update", "1"])

        cmd.append(str(output_path))

    subprocess.run(cmd, check=True)
    print("Watermarked file created:", output_path)
    return output_path

# makes 320x180 thumbnail
def createThumbnail(file, owner):
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


# loop image for gif creation
def makeGif(file, owner, fps = 24):
    path = Path(file)
    output_path = versionName(file, owner, ".gif")

    print("Input Path:", path)
    print("Output Gif:", output_path)

    if path.suffix.lower() in (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"):
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-t", "1",
            "-r", str(fps),
            "-i", str(path),
            str(output_path)
        ]

        subprocess.run(cmd, check=True)
        print("GIF created:", output_path)
        return output_path


# extract metadata and output to txt file
def extractMetadata(file, owner):
    path = Path(file)
    print(f"Metadata for {path}:")

    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        str(path)
    ]

    result = subprocess.run(cmd, capture_output = True, text = True)

    # write to txt file
    output_txt = path.parent / f"{path.stem}_VFX_{owner}_metadata.txt"
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(result.stdout)

    print("Metadata exported to:", output_txt)
    return output_txt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help = "enter file name or path")
    parser.add_argument("--owner", required = True, help = "define the owner")
    parser.add_argument("--watermark", action = "store_true", help = "add watermark")
    parser.add_argument("--gif", action = "store_true", help = "convert to gif")
    parser.add_argument("--thumbnail", action = "store_true", help = "create")
    parser.add_argument("--metadata", action = "store_true", help = "extract metadata")

    args = parser.parse_args()

    # most prints in this entire program were for testing
    # too lazy to remove so they stay
    print("File:", args.file)
    print("Owner:", args.owner)
    print("Watermark:", args.watermark)
    print("Gif:", args.gif)
    print("Thumbnail:", args.thumbnail)
    print("Metadata:", args.metadata)

    # if directory input for file
    path = Path(args.file)
    if path.is_dir():
        print("Folder detected...")
        media_exts = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp", ".gif")
        files = [
            f for f in path.iterdir() if f.suffix.lower() in media_exts
        ]
    else:
        files = [path]

    #new_name = versionName(args.file, args.owner)
    #print("New file name:", new_name)

    # function calls based on args
    for file_path in files:
        if args.watermark:
            addWatermark(file_path, args.owner)
        
        if args.thumbnail:
            createThumbnail(file_path, args.owner)
        
        if args.gif:
            makeGif(file_path, args.owner, fps = 24)

        if args.metadata:
            extractMetadata(file_path, args.owner)

main()
