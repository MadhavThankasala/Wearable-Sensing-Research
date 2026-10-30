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
        info = data.get("info", {})

        app = info.get("software", {}).get("app", {})

        if app.get("name") != "Beat Saber":
            continue

        events = data.get("events", [])

        for event in events:
            name = event.get("name")

            if name not in ["Good Cut", "Bad Cut", "Miss"]:
                continue

            print("\n====================")
            print("Recording:", filename)
            print("Event:", name)

            print("\nAttributes:")
            print(event.get("attr"))

            float_data = event.get("floatData", [])
            other_data = event.get("otherData", [])

            print("\nNumber of occurrences:", len(float_data))

            if float_data:
                print("\nFirst floatData item:")
                print(float_data[0])

            if other_data:
                print("\nFirst otherData item:")
                print(other_data[0])

        # Only inspect the first Beat Saber file with these events
        break