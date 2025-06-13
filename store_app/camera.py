import cv2
class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success , frame = self.video.read()
        cv2.imwrite("static/camera/tem.jpg" , frame)
        ret , jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

class VideoCamera2(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success , frame = self.video.read()
        cv2.imwrite("static/camera/tem.jpg" , frame)
        ret , jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()