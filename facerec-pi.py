import face_recognition
import cv2
import numpy as np
import os
# from picamera.array import PiRGBArray
# from picamera import PiCamera
import picamera
from datetime import *
from notify import *
import time

# video_capture = cv2.VideoCapture(0)

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

camera = picamera.PiCamera()
camera.resolution = (320, 240)
camera.framerate = 32
output = np.empty((240, 320, 3), dtype=np.uint8)
# rawCapture = PiRGBArray(camera, size=(1280, 720))

# notify = notifier()

# notifyInterval = 600

timePeriod = 0 

time.sleep(.1)

while True:
    # Grab a single frame of video
    # ret, frame = video_capture.read()

    camera.capture(output, format="rgb")

    # Resize frame of video to 1/4 size for faster face recognition processing
    # frame = cv2.imread(frame)
    frame = output
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    # rgb_small_frame = small_frame[:, :, ::-1]
    rgb_small_frame = small_frame

    # Only process every other frame of video to save time
    if process_this_frame == 2:
        print("processing")
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        print("checked frame")


        face_names = []
        for face_encoding in face_encodings:
            print("face found")
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
        process_this_frame == 0

    process_this_frame = process_this_frame + 1


    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        cv2.imwrite("caputure.jpg", frame)

        if(time.time() - timePeriod > notifyInterval):


            timePeriod = time.time()

            notify.send(name, "jgarc110@rams.colostate.edu", "capture.jpg")

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()