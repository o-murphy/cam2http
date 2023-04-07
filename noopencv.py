from io import BytesIO
from picamera import PiCamera
from flask import Flask, Response

app = Flask(__name__)

def generate_frames():
    with PiCamera() as camera:
        # Set camera resolution
        camera.resolution = (640, 480)
        # Wait for camera to warm up
        camera.start_preview()
        camera.stream.seek(0)

        while True:
            # Capture frame as JPEG image
            frame = BytesIO()
            camera.capture(frame, format='jpeg')
            # Reset stream position
            frame.seek(0)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame.read() + b'\r\n')

@app.route('/')
def index():
    return 'Hello, world!'

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)