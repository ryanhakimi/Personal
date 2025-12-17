import csv
import argparse
from typing import List, Dict, Tuple
from pymongo import MongoClient

## function definitions ##

# normalize path
def strip_storage_prefix(path: str) -> str:

    parts = path.strip().split("/")

    # remove empty segments
    parts = [p for p in parts if p]

    if not parts:
        return ""

    if "production" in parts:
        idx = parts.index("production") + 1
    else:
        idx = 1 if len(parts) > 1 else 0

    norm = "/".join(parts[idx:])
    return norm


# baselight parsing
def load_baselight_export(line: str) -> Dict:

    line = line.strip()
    if not line:
        return None

    tokens = line.split()
    path = tokens[0]
    frame_strs = tokens[1:]

    frames: List[int] = []
    for tok in frame_strs:
        try:
            frames.append(int(tok))
        except ValueError:
            continue

    return {
        "raw_path": path,
        "norm_path": strip_storage_prefix(path),
        "frames": frames,
    }


def parse_baselight_file(path: str) -> List[Dict]:

    entries: List[Dict] = []
    with open(path, "r") as f:
        for line in f:
            entry = load_baselight_export(line)
            if entry:
                entries.append(entry)
    return entries


# xytech parsing
def load_xytech_locations(path: str) -> List[Dict]:

    entries: List[Dict] = []
    with open(path, "r") as f:
        in_locations = False
        for raw_line in f:
            line = raw_line.rstrip("\n")

            if not in_locations:
                if line.strip().startswith("Location:"):
                    in_locations = True
                continue

            # inside location section
            if not line.strip():
                break

            location_path = line.strip()
            entries.append({
                "raw_path": location_path,
                "norm_path": strip_storage_prefix(location_path),
            })

    return entries


# frame to range helpers
def frames_to_ranges(frames: List[int]) -> List[Tuple[int, int]]:

    if not frames:
        return []

    frames = sorted(set(frames))
    ranges: List[Tuple[int, int]] = []

    start = prev = frames[0]
    for num in frames[1:]:
        if num == prev + 1:
            prev = num
        else:
            ranges.append((start, prev))
            start = prev = num
    ranges.append((start, prev))

    return ranges


def format_range(r: Tuple[int, int]) -> str:

    a, b = r
    return f"{a}" if a == b else f"{a}-{b}"


# matching and csv export
def build_match_table(
    baselight_entries: List[Dict],
    xytech_entries: List[Dict],
) -> List[Dict]:

    # build a lookup from stripped path to matching entries
    bl_map: Dict[str, List[Dict]] = {}
    for e in baselight_entries:
        bl_map.setdefault(e["norm_path"], []).append(e)

    matches: List[Dict] = []
    for x in xytech_entries:
        norm = x["norm_path"]
        if norm in bl_map:
            frames: List[int] = []
            for e in bl_map[norm]:
                frames.extend(e["frames"])

            ranges = frames_to_ranges(frames)
            formatted_ranges = [format_range(r) for r in ranges]

            matches.append({
                "xytech_path": x["raw_path"],
                "norm_path": norm,
                "frame_ranges": formatted_ranges,
            })

    return matches


def write_matches_to_csv(matches: List[Dict], output_csv_path: str) -> None:

    with open(output_csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Location", "FrameRange"])

        for m in matches:
            for fr in m["frame_ranges"]:
                writer.writerow([m["xytech_path"], fr])


# mongo helpers
def get_db():
    client = MongoClient("mongodb://localhost:27017/")
    return client["proj4_db"]


def save_baselight_to_db(db, baselight_entries, source_name):
    coll = db["baselight"]

    docs = []
    for e in baselight_entries:
        docs.append({
            "source": source_name,
            "raw_path": e["raw_path"],
            "norm_path": e["norm_path"],
            "frames": e["frames"],
        })

    if docs:
        coll.insert_many(docs)


def save_xytech_to_db(db, xytech_entries, source_name):
    coll = db["xytech"]

    docs = []
    for x in xytech_entries:
        docs.append({
            "source": source_name,
            "raw_path": x["raw_path"],
            "norm_path": x["norm_path"],
        })

    if docs:
        coll.insert_many(docs)

## func def end ##


parser = argparse.ArgumentParser(
    description="match baselight export to xytech locations and export csv"
)

parser.add_argument(
    "--baselight",
    required=True,
    help="path to baselight export text file"
)

parser.add_argument(
    "--xytech",
    required=True,
    help="path to xytech workorder text file"
)

args = parser.parse_args()

baselight_entries = parse_baselight_file(args.baselight)
xytech_entries = load_xytech_locations(args.xytech)

matches = build_match_table(baselight_entries, xytech_entries)

output_csv = "match_output.csv"
write_matches_to_csv(matches, output_csv)

# stash in mongo
db = get_db()
save_baselight_to_db(db, baselight_entries, args.baselight)
save_xytech_to_db(db, xytech_entries, args.xytech)