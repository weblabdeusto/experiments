from app.camera.config import CAMERA
from flask import Response
import time
from app.sessionManager.tools import check_permission
from app import video

if CAMERA == 'pi_camera':
    from app.camera.pi_camera import Camera
else:
    from app.camera.web_camera import Camera

camera = Camera()


def gen(camera):
    """Video streaming generator function."""
    while True:
        time.sleep(0.2)
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')




@video.route('/video_feed')
@check_permission
def video_feed():
    global camera
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')