import face_recognition
import cv2
import numpy as np
import os
import time
from notify import *
import io #buffered binary streams
import picamera #camera API
import socketserver #framework for network server
import logging #log error messages
from threading import Condition #allow thread to wait until notified
from http import server #need to impliment server

#HTML for website
PAGE="""\
<html>
<head>
<title>Pi Camera Video Feed</title>
</head>
<body>
<center><h1>Pi Camera Video Feed</h1></center>
<center><img src="stream.mjpg" width="640" height="480"></center>
</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        #check for new frame
        if buf.startswith(b'\xff\xd8'):
            #resize the stream
            self.buffer.truncate()
            with self.condition:
                #return new frame
                self.frame = self.buffer.getvalue()
                #notify 
                self.condition.notify_all()
            #set stream position to beginning
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    #handle HTTP requests that arrive at the server
    #no explict constructor is necessary 
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    #daemon threads don't need to be tracked, they will be killed automatically when the program exits
    daemon_threads = True

video_capture = cv2.VideoCapture(0)

# # Load a sample picture and learn how to recognize it.
# obama_image = face_recognition.load_image_file("obama.jpg")
# obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

# # Load a second sample picture and learn how to recognize it.
# biden_image = face_recognition.load_image_file("biden.jpg")
# biden_face_encoding = face_recognition.face_encodings(biden_image)[0]

# # Create arrays of known face encodings and their names
# known_face_encodings = [
#     obama_face_encoding,
#     biden_face_encoding
# ]
# known_face_names = [
#     "Barack Obama",
#     "Joe Biden"
# ]

known_face_encodings = []
known_face_names = []
# Will open text file of names/images and add line by line to model
with open('enrolled.txt') as fp:
    for person in fp:
        data = person.split("^^")
        known_face_names.append(data[0])

        image = face_recognition.load_image_file(os.getcwd() + "/Images/" + data[1].replace("\n",""))

        image_encoding = face_recognition.face_encodings(image)[0]
        known_face_encodings.append(image_encoding)


face_locations = []
face_encodings = []
face_names = []
process_this_frame = 0

notify = notifier()

timePeriod = 0

notifyInterval = 600
with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    while True:
        # Grab a single frame of video
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
        ret, frame = video_capture.read()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.2, fy=0.2)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if process_this_frame == 4:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                # # If a match was found in known_face_encodings, just use the first one.
                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

                face_names.append(name)
            process_this_frame = 0

        process_this_frame = process_this_frame + 1


        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 5
            right *= 5
            bottom *= 5
            left *= 5

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            cv2.imwrite("capture.jpg",frame)

            if (time.time()-timePeriod) > notifyInterval:

                timePeriod = time.time()
                
                notify.send(name, "suyashhiray@gmail.com","capture.jpg")

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
camera.stop_recording()