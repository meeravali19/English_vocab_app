import json
import os

DATASET_PATH = "datasets/vocab.json"

def load_dataset():
    if not os.path.exists(DATASET_PATH):
        return []
    with open(DATASET_PATH, "r") as f:
        return json.load(f)

def save_dataset(data):
    with open(DATASET_PATH, "w") as f:
        json.dump(data, f, indent=4)

def add_new_word(new_entry):
    data = load_dataset()
    data.append(new_entry)
    save_dataset(data)
