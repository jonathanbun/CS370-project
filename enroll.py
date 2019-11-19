import face_recognition
import cv2
import numpy as np
import os
import shutil

def main():
	img_name = ""
	name = input("Welcome to enrollment! Please enter your name:\n")
	decision = input("Enter '1' for uploading an image or '2' for taking an image with the webcam\n")
	if decision == 1:
		img_name = input("Please enter image name with extension and place into folder:\n")
	elif decision == 2: 
		print("Camera is opening, press spacebar to take image\n")
		cam = cv2.VideoCapture(0)
		cv2.namedWindow("Enrollment")
		while True:
			ret, frame = cam.read()
			cv2.imshow("Enrollment", frame)
			if not ret:
				break
			k = cv2.waitKey(1)

			if k%256 == 27:
		        # ESC pressed
				print("Escape hit, closing...")
				break
			elif k%256 == 32:
		        # SPACE pressed
				img_name = "{}.jpg".format(name)
				cv2.imwrite(img_name, frame)
				print("{} added to enrolled list!".format(img_name))

			cam.release()

			cv2.destroyAllWindows()

	f = open("enrolled.txt", "a")
	f.write("\n"+name + "^^" + img_name + "\n")
	f.close()
	for file in os.listdir(os.getcwd()):
		if file.endswith(".jpg"):
			shutil.move(os.getcwd(), os.path.join(os.getcwd() + "/Images", file))

if __name__== "__main__":
	main()
