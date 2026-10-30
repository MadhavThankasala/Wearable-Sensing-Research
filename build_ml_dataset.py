from xror import XROR
import os
import csv
import math
import statistics

ROOT_FOLDER = os.path.expanduser("~/Downloads/boxrr_samples")
WINDOW_SECONDS = 1.0

OUTPUT_FILE = "beat_saber_ml_dataset.csv"

def mean(values):
    return statistics.mean(values) if values else 0.0

def stdev(values):
    return statistics.pstdev(values) if len(values) > 1 else 0.0

def distance(p1, p2):
    return math.sqrt(
        (p2[0] - p1[0]) ** 2 +
        (p2[1] - p1[1]) ** 2 +
        (p2[2] - p1[2]) ** 2
    )

def extract_features(window):
    """
    Each frame:
    0       = time
    1:8     = head
    8:15    = left controller
    15:22   = right controller

    Within each device:
    first 3 values = x, y, z position
    remaining 4    = orientation
    """

    if len(window) < 2:
        return None

    times = [frame[0] for frame in window]

    head_positions = [frame[1:4] for frame in window]
    left_positions = [frame[8:11] for frame in window]
    right_positions = [frame[15:18] for frame in window]

    features = {}

    devices = {
        "head": head_positions,
        "left": left_positions,
        "right": right_positions,
    }

    for device_name, positions in devices.items():

        xs = [p[0] for p in positions]
        ys = [p[1] for p in positions]
        zs = [p[2] for p in positions]

        features[f"{device_name}_x_mean"] = mean(xs)
        features[f"{device_name}_y_mean"] = mean(ys)
        features[f"{device_name}_z_mean"] = mean(zs)

        features[f"{device_name}_x_std"] = stdev(xs)
        features[f"{device_name}_y_std"] = stdev(ys)
        features[f"{device_name}_z_std"] = stdev(zs)

        speeds = []

        for i in range(1, len(positions)):
            dt = times[i] - times[i - 1]

            if dt <= 0:
                continue

            d = distance(positions[i - 1], positions[i])
            speeds.append(d / dt)

        features[f"{device_name}_avg_speed"] = mean(speeds)
        features[f"{device_name}_max_speed"] = max(speeds) if speeds else 0.0

        total_distance = 0.0

        for i in range(1, len(positions)):
            total_distance += distance(
                positions[i - 1],
                positions[i]
            )

        features[f"{device_name}_distance"] = total_distance

    features["window_frame_count"] = len(window)

    return features


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

            # Only use Beat Saber
            if app.get("name") != "Beat Saber":
                continue

            recording_id = filename.replace(".xror", "")

            for event in events:

                label = event.get("name")

                if label not in ["Good Cut", "Bad Cut", "Miss"]:
                    continue

                float_data = event.get("floatData", [])

                for occurrence in float_data:

                    if not occurrence:
                        continue

                    event_time = occurrence[0]
                    window_start = event_time - WINDOW_SECONDS

                    window = [
                        frame for frame in frames
                        if window_start <= frame[0] <= event_time
                    ]

                    features = extract_features(window)

                    if features is None:
                        continue

                    row = {
                        "recording_id": recording_id,
                        "event_time": event_time,
                        "label": label,
                    }

                    row.update(features)
                    rows.append(row)

            print("Processed:", filename)

        except Exception as e:
            print("ERROR:", filename, e)


if rows:
    fieldnames = list(rows[0].keys())

    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("\n---------------------------")
    print("ML dataset created")
    print("Rows:", len(rows))
    print("Saved to:", OUTPUT_FILE)

    label_counts = {}

    for row in rows:
        label = row["label"]
        label_counts[label] = label_counts.get(label, 0) + 1

    print("\nLabel counts:")
    for label, count in label_counts.items():
        print(label, count)

else:
    print("No ML rows were created.")