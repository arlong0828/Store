import os


def azure_face_credentials():
    """Return Azure Face credentials configured outside source control."""
    key = os.environ.get("AZURE_FACE_KEY", "")
    endpoint = os.environ.get("AZURE_FACE_ENDPOINT", "")
    if not key or not endpoint:
        raise RuntimeError("AZURE_FACE_KEY and AZURE_FACE_ENDPOINT are required")
    return key, endpoint
