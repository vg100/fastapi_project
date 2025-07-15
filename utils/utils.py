# utils.py

import os
import json
from datetime import datetime, timedelta
import jwt


# Logging helper
def log(message: str, level: str = "INFO") -> None:
    print(f"[{datetime.now().isoformat()}] [{level.upper()}] {message}")


# Date formatting
def current_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# JSON file read/write
def save_json(filepath: str, data: dict) -> None:
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)


def load_json(filepath: str) -> dict:
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r") as f:
        return json.load(f)


# Check if string is a valid int
def is_int(value: str) -> bool:
    try:
        int(value)
        return True
    except ValueError:
        return False


# Convert bytes to human-readable format
def sizeof_fmt(num: int, suffix="B") -> str:
    for unit in ["", "K", "M", "G", "T", "P"]:
        if abs(num) < 1024:
            return f"{num:.1f}{unit}{suffix}"
        num /= 1024
    return f"{num:.1f}Y{suffix}"


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=60))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, "python", algorithm="HS256")


if __name__ == "__main__":
    log("HELLO")
else:
    print("Usage: python my_script.py")
