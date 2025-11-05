import argparse
import ffmpeg
import json


parser = argparse.ArgumentParser()
parser.add_argument("image", help = "image filepath")
args = parser.parse_args()

print ("image path: ", args.image)
info = ffmpeg.probe(args.image)
print(type(info), info.keys())
print(json.dumps(info, indent=2))

out_path = "metadata.txt"
with open(out_path, "w", encoding="utf-8") as file:
    json.dump(info, file, indent=2)
print("Saved metadata to:", out_path)