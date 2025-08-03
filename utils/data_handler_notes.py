import os
import json

DATA_FOLDER = "data"
NOTES_FILE = os.path.join(DATA_FOLDER, "notes.json")

def ensure_note_file():
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    if not os.path.isfile(NOTES_FILE):
        with open(NOTES_FILE, "w") as f:
            json.dump({}, f)

def load_notes():
    ensure_note_file()
    with open(NOTES_FILE, "r") as f:
        return json.load(f)

def save_notes(data):
    ensure_note_file()
    with open(NOTES_FILE, "w") as f:
        json.dump(data, f, indent=4)
