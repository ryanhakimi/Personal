### project 3 vFxML ###
# get it? cuz FML means fuck my life, and its kinda in the project name? whatever...

#imports
import argparse
from pathlib import Path

#functions
def versionName(file, owner):
    path = Path(file)
    print("Stem:", path.stem)
    print("Suffix:", path.suffix)
    print(f"Base:{path.stem}_VFX_{owner}_v01{path.suffix}")


parser = argparse.ArgumentParser()
parser.add_argument("file", help = "enter file name or path")
parser.add_argument("--owner", help = "define the owner")

args = parser.parse_args()

print("File:", args.file)
print("Owner:", args.owner)

versionName(args.file, args.owner)

