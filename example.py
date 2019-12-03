import face_recognition
import cv2
import numpy as np
from notify import *
from datetime import *
import imutils
from imutils.video import VideoStream
from imutils.io import TempFile
import sys
import time
from vidgear import *

class securityCamera(object):



    def __init__(self):

        self.video_capture = cv2.VideoCapture(0)
        time.sleep(2.0)
     

    def __del__(self):

        self.video_capture.release()
        cv2.destroyAllWindows()

    def get_frame(self):

      

        ret, frame = self.video_capture.read()

        frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        success, jpeg = cv2.imencode('.jpg', frame)

        return jpeg.tobytes()

    
    def process(self,frame):

        print("test1")


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

    
        # Grab a single frame of video
        ret, frame = self.video_capture.read()

     

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.2, fy=0.2)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if process_this_frame == 2:

            print("processing frame")
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


            print("found face")
            

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            cv2.imwrite("capture.jpg",frame)

            if (time.time()-timePeriod) > notifyInterval:

                timePeriod = time.time()
                
                notify.send("capture.jpg")
