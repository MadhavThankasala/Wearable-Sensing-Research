from xror import XROR
import os
import csv

ROOT_FOLDER = os.path.expanduser("~/Downloads/boxrr_samples")

rows = []

for root, dirs, files in os.walk(ROOT_FOLDER):
    for filename in files:
        if not filename.endswith(".xror"):
            continue

        path = os.path.join(root, filename)

        try:
            with open(path, "rb") as f:
                recording = XROR.unpack(f.read())

            data = recording.data
            info = data.get("info", {})
            frames = data.get("frames", [])
            events = data.get("events", [])

            software = info.get("software", {})
            app = software.get("app", {})
            activity = software.get("activity", {})

            app_name = app.get("name", "Unknown")

            # Ignore non-Beat Saber recordings
            if app_name != "Beat Saber":
                print("Skipped:", filename, "-", app_name)
                continue

            event_summary = {}

            for event in events:
                name = event.get("name", "Unknown")

                event_summary[name] = {
                    "has_floatData": "floatData" in event,
                    "floatData_length": len(event.get("floatData", [])),
                    "has_otherData": "otherData" in event,
                    "otherData_length": len(event.get("otherData", [])),
                    "attr_length": len(event.get("attr", []))
                }

            row = {
                "recording_id": filename.replace(".xror", ""),
                "num_frames": len(frames),
                "difficulty": activity.get("difficulty", ""),
                "mode": activity.get("mode", ""),
                "note_count": activity.get("noteCount", ""),
                "bomb_count": activity.get("bombCount", ""),
                "wall_count": activity.get("wallCount", ""),
                "good_cut_float_len": event_summary.get(
                    "Good Cut", {}
                ).get("floatData_length", 0),
                "good_cut_other_len": event_summary.get(
                    "Good Cut", {}
                ).get("otherData_length", 0),
                "bad_cut_float_len": event_summary.get(
                    "Bad Cut", {}
                ).get("floatData_length", 0),
                "miss_float_len": event_summary.get(
                    "Miss", {}
                ).get("floatData_length", 0),
                "bomb_cut_float_len": event_summary.get(
                    "Bomb Cut", {}
                ).get("floatData_length", 0),
            }

            rows.append(row)

            print("\nBeat Saber recording:", filename)
            print("Frames:", len(frames))
            print("Activity:", activity)

            for name, summary in event_summary.items():
                print(name, "->", summary)

        except Exception as e:
            print("ERROR:", filename, e)

output_file = "beat_saber_summary.csv"

fieldnames = [
    "recording_id",
    "num_frames",
    "difficulty",
    "mode",
    "note_count",
    "bomb_count",
    "wall_count",
    "good_cut_float_len",
    "good_cut_other_len",
    "bad_cut_float_len",
    "miss_float_len",
    "bomb_cut_float_len",
]

with open(output_file, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("\n---------------------------")
print("Beat Saber recordings processed:", len(rows))
print("Saved to:", output_file)

