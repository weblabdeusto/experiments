import eventlet

eventlet.monkey_patch()

import time
import io
import threading
import picamera


class Camera(object):
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera
    camera = None
    stop = True

    def initialize(self):
        if Camera.thread is None:
            # start background frame thread
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.daemon = True
            Camera.thread.start()

            # wait until frames start to be available
            while self.frame is None:
                time.sleep(0)

    def get_frame(self):
        Camera.last_access = time.time()
        self.initialize()
        return self.frame

    def close(self):
        Camera.stop = True
        print 'stopping thread'
        Camera.thread.join()
        print 'Thread stopped'
        Camera.camera.close()

    @classmethod
    def _thread(cls):
        try:
            print 'Stopping camera thread'
            cls.stop = False
            with picamera.PiCamera() as cls.camera:
                # camera setup
                cls.camera.resolution = (320, 180)
                cls.camera.hflip = True
                cls.camera.vflip = True

                # let camera warm up
                cls.camera.start_preview()
                time.sleep(2)

                stream = io.BytesIO()
                for foo in cls.camera.capture_continuous(stream, 'jpeg',
                                                     use_video_port=True):
                    # store frame
                    stream.seek(0)
                    cls.frame = stream.read()

                    # reset stream for next frame
                    stream.seek(0)
                    stream.truncate()

                    # if there hasn't been any clients asking for frames in
                    # the last 10 seconds stop the thread
                    if time.time() - cls.last_access > 3:
                        print 'No client asking for camera'
                        break
                    if cls.stop:
                        break


            cls.camera.close()
            cls.thread = None
        except:
            print 'Camera exception'
            cls.camera.close()
            cls.thread = None
