import cv2
from flask import Flask, Response, render_template, request

app = Flask(__name__, template_folder='templates')

# Get list of available camera names
camera_names = [f'Camera {i}' for i in range(10)]

# Set default camera index to 0
current_camera = 0

# Start the camera
camera = cv2.VideoCapture(current_camera)

# Flag to control the video stream
video_stream = False


# Load pre-trained Haar Cascade classifier for detecting faces
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')



def compare_frames(prev, cur):
    # Convert the frames to grayscale
    if prev is None:
        return 0
    elif not prev.any():
        return 0
    else:

        gray1 = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(cur, cv2.COLOR_BGR2GRAY)

        if gray1.size == gray2.size:

            # Compute the absolute difference between the two frames
            diff = cv2.absdiff(gray1, gray2)

            sad = diff.sum()

            # Print SAD value
            return sad


def detect_human(frame):
    # Convert the frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame using the face cascade classifier
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Loop through each face detected in the frame
    for (x, y, w, h) in faces:
        # Draw a rectangle around the face
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Crop the face region from the frame
        face_roi = gray[y:y + h, x:x + w]

        # Resize the face region to a fixed size for classification
        face_roi = cv2.resize(face_roi, (100, 100))

        # Apply your identification algorithm here
        # ...
    return frame

def generate_frames():
    global video_stream, camera, current_camera
    prev_frame = None
    while video_stream:
        ret, frame = camera.read() #read the camera frame

        frame = detect_human(frame)
        # if compare_frames(prev_frame, frame) == 0:
        #     current_camera += 1
        #     camera = cv2.VideoCapture(current_camera)

        if ret:
            # Resize frame to 320x240 for reduced latency
            # frame = cv2.resize(frame, (320, 240))
            # Convert frame to JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            # Use bytearray instead of tobytes() to reduce memory allocation
            jpeg_bytes = bytearray(buffer)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg_bytes + b'\r\n') #concat frame one by one and show result
        prev_frame = frame

@app.route('/')
def index():
    global current_camera
    return render_template('index.html', camera_names=camera_names, current_camera=current_camera)

@app.route('/video_feed')
def video_feed():
    global video_stream
    video_stream = True
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start')
def start():
    global video_stream
    video_stream = True
    return render_template('index.html', camera_names=camera_names, current_camera=current_camera)

@app.route('/stop')
def stop():
    global video_stream
    video_stream = False
    return render_template('index.html', camera_names=camera_names, current_camera=current_camera)

@app.route('/change_camera')
def change_camera():
    global camera, current_camera
    camera_id = int(request.args.get('camera_id'))
    if camera.isOpened():
        camera.release()
    camera = cv2.VideoCapture(camera_id)
    current_camera = camera_id
    return render_template('index.html', camera_names=camera_names, current_camera=current_camera)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
