import io
import threading
import time
import cv2
import Image
import redis

class Camera(object):
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera
    r = redis.StrictRedis(host='localhost', port=6379, db=13)

    def initialize(self):
        if Camera.thread is None:
            # start background frame thread
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()

            # wait until frames start to be available
            while self.frame is None:
                time.sleep(0.1)

    def get_frame(self):
        Camera.last_access = time.time()
        self.initialize()
        return self.frame

    @classmethod
    def _thread(cls):
        camera = cv2.VideoCapture(0)
        camera.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 320)
        camera.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 240)
        camera.set(cv2.cv.CV_CAP_PROP_SATURATION,0.2)
        time.sleep(1)
        stream = io.BytesIO()
        while True:
            rc,img = camera.read()
            if not rc:
                continue
            imgRGB=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
            jpg = Image.fromarray(imgRGB)
            time.sleep(0.1)
            jpg.save(stream,'JPEG')

            # store frame
            stream.seek(0)
            cls.frame = stream.read()

            # reset stream for next frame
            stream.seek(0)
            stream.truncate()

            # if there hasn't been any clients asking for frames in
            # the last 10 seconds stop the thread
            if time.time() - cls.last_access > 10:
                break

        camera.release()
        cls.thread = None