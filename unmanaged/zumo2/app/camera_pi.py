import time
import io
import threading
import picamera


class Camera(object):

    def __init__(self):
        self.thread = None  # background thread that reads frames from camera
        self.frame = None  # current frame is stored here by background thread
        self.last_access = 0  # time of last client access to the camera
        self.camera = picamera.PiCamera()
        self.camera.resolution = (320, 180)
        self.camera.hflip = True
        self.camera.vflip = True
        self.camera.start_preview()


    def start(self):
        if self.thread is None:
            # start background frame thread
            self.thread = threading.Thread(target=self.thread)
            self.thread.start()

            # wait until frames start to be available
            while self.frame is None:
                time.sleep(0)

    def get_frame(self):
        self.last_access = time.time()
        self.start()
        return self.frame


    def thread(self):
            # let camera warm up
            self.camera.start_preview()
            time.sleep(2)
            stream = io.BytesIO()
            for foo in self.camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
                # store frame
                stream.seek(0)
                self.frame = stream.read()

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()

                # if there hasn't been any clients asking for frames in
                # the last 10 seconds stop the thread
                if time.time() - self.last_access > 10:
                    break
            self.thread = None
