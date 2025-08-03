import json
import os

DATA_FILE = "data/warnings.json"

def load_warnings():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_warnings(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
