import json
import os

DATA_FILE = "data/shop_data.json"

def load_data():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_FILE):
        default = {
            "prices": {"1day": "100", "7day": "500", "30day": "1500", "forever": "5000"},
            "keys": {"1day": "", "7day": "", "30day": "", "forever": ""}
        }
        save_data(default)
        return default
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
