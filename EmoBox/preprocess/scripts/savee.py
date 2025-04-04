import os
import re
from collections import defaultdict
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.preprocess_utils import *
from tqdm import tqdm

DATASET_NAME = "savee"
SAMPLE_RATE = 44100

def parse_filename(filename):
    # Remove file extension
    name = filename.split(".")[0]

    # Split the filename by underscores
    parts = name.split("_")

    speaker_id = parts[0]

    emotion = parts[1][:-2]

    # Construct the dictionary
    parsed_info = {
        "id": name,
        "lang": "en",
        "spk": speaker_id,
        "gd": "Male",
        "emotion": emotion,
    }
    return parsed_info


def process_savee(
    dataset_path, output_base_dir="data/savee", output_format: str | list = "jsonl"
):

    # Create output directories
    os.makedirs(output_base_dir, exist_ok=True)

    data = {}
    emotion_freq = defaultdict(int)

    # Processing files with a progress bar
    for file_path in tqdm(os.listdir(dataset_path), desc="Processing files"):
        if not file_path.lower().endswith(".wav"):
            continue
        file_path = os.path.join(dataset_path, file_path)
        waveform, sample_rate = load_audio(file_path)
        if waveform is None:
            continue
        if sample_rate != SAMPLE_RATE:
            print(f"Sample rate of {file_path} is not {SAMPLE_RATE}")
        
        num_frame = waveform.size(1)
        parsed_info = parse_filename(os.path.basename(file_path))
        sid = f"{DATASET_NAME}-{parsed_info['id'].replace('_', '-')}"

        data[sid] = {
            # relative path from dataset_path
            "audio": file_path,
            "emotion": parsed_info["emotion"],
            "channel": 1,
            "sid": sid,
            "sample_rate": sample_rate,
            "num_frame": num_frame,
            "spk": parsed_info["spk"],
            "start_time": 0,
            "end_time": num_frame / sample_rate,
            "duration": num_frame / sample_rate,
            "lang": parsed_info["lang"],
        }

        emotion_freq[parsed_info["emotion"]] += 1

    if output_format == "mini_format" or "mini_format" in output_format:
        write_mini_format(data, output_base_dir)

    if output_format == "jsonl" or "jsonl" in output_format:
        # Handle single-file JSON or JSONL output for the entire dataset
        jsonl_file_path = os.path.join(output_base_dir, f"{DATASET_NAME}.jsonl")
        write_jsonl(data, jsonl_file_path, DATASET_NAME)

    if output_format == "json" or "json" in output_format:
        # Handle single-file JSON output for the entire dataset
        json_file_path = os.path.join(output_base_dir, f"{DATASET_NAME}.json")
        write_json(data, json_file_path, DATASET_NAME)

    if output_format == "split" or "split" in output_format:
        write_folds(data, output_base_dir, DATASET_NAME)

    print(f"Emotion frequency: {emotion_freq}")
    
if __name__ == "__main__":
    process_savee(
        "downloads/savee", output_format=["mini_format", "jsonl", "json", "split"]
    )
