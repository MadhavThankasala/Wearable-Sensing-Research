from xror import XROR
import os

ROOT_FOLDER = os.path.expanduser("~/Downloads/boxrr_samples")

for root, dirs, files in os.walk(ROOT_FOLDER):
    for filename in files:
        if not filename.endswith(".xror"):
            continue

        path = os.path.join(root, filename)

        with open(path, "rb") as f:
            recording = XROR.unpack(f.read())

        data = recording.data

        app = (
            data.get("info", {})
                .get("software", {})
                .get("app", {})
        )

        if app.get("name") != "Beat Saber":
            continue

        frames = data.get("frames", [])
        events = data.get("events", [])

        # Find first Good Cut / Bad Cut / Miss with data
        for event in events:
            name = event.get("name")

            if name not in ["Good Cut", "Bad Cut", "Miss"]:
                continue

            float_data = event.get("floatData", [])

            if not float_data:
                continue

            first_event = float_data[0]

            event_time = first_event[0]
            spawn_time = first_event[1]

            print("\n==========================")
            print("Recording:", filename)
            print("Event:", name)
            print("Event time:", event_time)
            print("Spawn time:", spawn_time)

            # Find frame closest to event time
            closest_index = min(
                range(len(frames)),
                key=lambda i: abs(frames[i][0] - event_time)
            )

            print("\nClosest motion frame:")
            print("Frame index:", closest_index)
            print("Frame time:", frames[closest_index][0])
            print(
                "Difference:",
                abs(frames[closest_index][0] - event_time)
            )

            print("\nNearby frame timestamps:")

            start = max(0, closest_index - 3)
            end = min(len(frames), closest_index + 4)

            for i in range(start, end):
                print(i, frames[i][0])

            # Only show one example from each event type