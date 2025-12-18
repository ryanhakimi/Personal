import csv
import argparse
from typing import List, Dict, Tuple
from pymongo import MongoClient
import subprocess
import json
from openpyxl import Workbook

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


def process_video(video_path: str):

    print(f"yo, gonna process video: {video_path}")

    db = get_db()

    ps_entries = get_planeshifter_entries(db)
    print(f"found {len(ps_entries)} planeshifter entries")

    all_frames = []
    for e in ps_entries:
        all_frames.extend(e["frames"])
    
    # only print unique frames
    all_frames = sorted(set(all_frames))

    ps_ranges = add_handles_to_frames(all_frames)

    print("ranges w/ handles:")
    for r in ps_ranges:
        print(r)
    
    # pull fps + starting tc from video
    fps, start_tc = get_video_info(video_path)
    print(f"video fps looks like: {fps}")
    if start_tc:
        print(f"video start timecode: {start_tc}")
        base_frame = timecode_to_frames(start_tc, fps)
    else:
        print("no timecode found, assuming base 00:00:00:00")
        base_frame = 0

    # convert frame ranges to tc ranges
    tc_ranges = []
    for start_f, end_f in ps_ranges:
        start_tc_str = frames_to_timecode(start_f, fps, base_frame)
        end_tc_str = frames_to_timecode(end_f, fps, base_frame)
        tc_ranges.append({
            "start_frame": start_f,
            "end_frame": end_f,
            "start_tc": start_tc_str,
            "end_tc": end_tc_str,
        })

    print("ranges as timecode:")
    for r in tc_ranges:
        print(
            f"{r['start_frame']}–{r['end_frame']} "
            f"-> {r['start_tc']} to {r['end_tc']}"
        )
    
    return tc_ranges


def get_planeshifter_entries(db):
    coll = db["baselight"]
    # searching by substring in norm_path
    return list(coll.find({"norm_path": {"$regex": "Planeshifter"}}))


def add_handles_to_frames(frames, fps=24, seconds=2):
    
    if not frames:
        return []

    frames = sorted(frames)

    handle = fps * seconds
    ranges = []

    for f in frames:
        start = f - handle
        end = f + handle
        if start < 0:
            start = 0
        ranges.append((start, end))

    return ranges


def get_video_info(video_path: str):
    
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=avg_frame_rate:format_tags=timecode",
        "-of", "json",
        video_path,
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        print("ffprobe had an issue, falling back to 24fps, no tc")
        return 24.0, None

    data = json.loads(result.stdout or "{}")

    fps = 24.0
    timecode_str = None

    streams = data.get("streams", [])
    if streams:
        s0 = streams[0]
        fr = s0.get("avg_frame_rate")
        if fr and fr != "0/0":
            num, den = fr.split("/")
            try:
                fps = float(num) / float(den)
            except ZeroDivisionError:
                fps = 24.0

    # timecode might sit under format.tags.timecode
    fmt = data.get("format", {})
    tags = fmt.get("tags", {})
    tc = tags.get("timecode")
    if tc:
        timecode_str = tc

    return fps, timecode_str


def timecode_to_frames(tc: str, fps: float) -> int:
    
    parts = tc.split(":")
    if len(parts) != 4:
        return 0

    h = int(parts[0])
    m = int(parts[1])
    s = int(parts[2])
    f = int(parts[3])

    total = (((h * 60) + m) * 60 + s) * fps + f
    return int(round(total))


def frames_to_timecode(frame: int, fps: float, base_frame: int = 0) -> str:
    
    total = frame + base_frame
    fps_i = int(round(fps))
    if fps_i <= 0:
        fps_i = 24

    total = int(round(total))

    secs, ff = divmod(total, fps_i)
    mins, ss = divmod(secs, 60)
    hrs, mm = divmod(mins, 60)

    return f"{hrs:02d}:{mm:02d}:{ss:02d}:{ff:02d}"


def write_xls_with_planeshifter(output_xls_path, matches, tc_ranges):
    wb = Workbook()
    ws = wb.active
    ws.title = "stuff"

    # main match table, same as csv
    ws.append(["Location", "FrameRange"])
    for m in matches:
        loc = m["xytech_path"]
        for fr in m["frame_ranges"]:
            ws.append([loc, fr])

    # add planeshifter tc stuff as extra section
    if tc_ranges:
        ws.append([])  # blank row
        ws.append(["ps_start_frame", "ps_end_frame", "ps_start_tc", "ps_end_tc"])
        for r in tc_ranges:
            ws.append([
                r["start_frame"],
                r["end_frame"],
                r["start_tc"],
                r["end_tc"],
            ])

    wb.save(output_xls_path)
    print(f"wrote xls to {output_xls_path}")

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

parser.add_argument(
    "--process",
    help="video file to process (trailer demo)"
)

parser.add_argument(
    "--output",
    help="excel file (xlsx) to write"
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

tc_ranges = None
if args.process:
    tc_ranges = process_video(args.process)

if args.output:
    write_xls_with_planeshifter(args.output, matches, tc_ranges)