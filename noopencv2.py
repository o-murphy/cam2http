import io
import time
import select
import socket
import v4l2capture
from PIL import Image

# Open the first video device (/dev/video0)
video = v4l2capture.Video_device("/dev/video0")

# Suggest an image size to the device
size_x, size_y = video.set_format(640, 480)

# Create a socket and bind to the address
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(0)

# Accept a single connection and make a file-like object out of it
connection = server_socket.accept()[0].makefile('wb')

try:
    while True:
        # Wait for the device to fill the buffer
        select.select((video,), (), ())

        # Read the frame from the device
        image_data = video.read_and_queue()

        # Convert the raw image data to a PIL Image object
        image = Image.frombytes("RGB", (size_x, size_y), image_data)

        # Convert the PIL Image to a JPEG byte string
        with io.BytesIO() as buffer:
            image.save(buffer, format='JPEG')
            jpeg_bytes = buffer.getvalue()

        # Write the JPEG byte string to the socket
        connection.write(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg_bytes + b'\r\n')

except KeyboardInterrupt:
    # Clean up
    connection.close()
    server_socket.close()
    video.close()