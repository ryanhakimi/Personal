import argparse

fps = 24

def frame_to_timecode(frame: int, fps: int = fps) -> str:
    if frame <0:
        raise ValueError("invalid input...")
    seconds, frame_count = divmod(frame, fps)
    hours, rem = divmod(seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frame_count:02d}"

parser = argparse.ArgumentParser(
    description = "convert frame number to timecode"
)
parser.add_argument("frames", nargs="+", type=int, help="frame numbers to convert")
args = parser.parse_args()

for frame in args.frames:
    print(f"{frame} -> {frame_to_timecode(frame)}")