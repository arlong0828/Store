from pathlib import Path

import cv2
from django.conf import settings


class BaseCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, frame = self.video.read()
        if not success or frame is None:
            frame = self._fallback_frame()
        camera_file = Path(settings.BASE_DIR) / "static/camera/tem.jpg"
        cv2.imwrite(str(camera_file), frame)
        _, jpeg = cv2.imencode(".jpg", frame)
        return jpeg.tobytes()

    @staticmethod
    def _fallback_frame():
        import numpy as np

        frame = np.full((720, 960, 3), (24, 42, 35), dtype=np.uint8)
        cv2.putText(frame, "CAMERA OFFLINE", (290, 370), cv2.FONT_HERSHEY_SIMPLEX, 1, (69, 255, 215), 2)
        return frame


class VideoCamera(BaseCamera):
    pass


class ProductCamera(BaseCamera):
    pass
