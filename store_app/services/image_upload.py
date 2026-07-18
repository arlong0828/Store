import base64
import os
from pathlib import Path

import requests


def upload_image(path):
    """Upload a temporary recognition image and return its public URL."""
    client_id = os.environ.get("IMGUR_CLIENT_ID", "")
    if not client_id:
        raise RuntimeError("IMGUR_CLIENT_ID is required")

    encoded = base64.b64encode(Path(path).read_bytes()).decode("utf-8")
    response = requests.post(
        "https://api.imgur.com/3/image",
        headers={"Authorization": f"Client-ID {client_id}"},
        data={"image": encoded, "type": "base64", "name": "recognition.jpg"},
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()["data"]
    return data.get("link") or f"https://i.imgur.com/{data['id']}.jpg"
