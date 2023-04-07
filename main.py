import cv2
from flask import Flask, Response

app = Flask(__name__)
camera = cv2.VideoCapture(2) #use 0 for default camera

def generate_frames():
    while True:
        success, frame = camera.read() #read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') #concat frame one by one and show result

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)