import os
import json

DATA_FOLDER = "data"
WARNINGS_FILE = os.path.join(DATA_FOLDER, "warnings.json")

def ensure_data_files():
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

    if not os.path.isfile(WARNINGS_FILE):
        with open(WARNINGS_FILE, "w") as f:
            json.dump({}, f)

def load_warnings():
    ensure_data_files()
    with open(WARNINGS_FILE, "r") as f:
        return json.load(f)

def save_warnings(data):
    ensure_data_files()
    with open(WARNINGS_FILE, "w") as f:
        json.dump(data, f, indent=4)
