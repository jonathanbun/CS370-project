import face_recognition
import cv2
import numpy as np
import os

def main():
	print("Welcome to enrollment! Please enter your name:\n")
	name = input()
	print("Enter '1' for uploading an image or '2' for taking an image with the webcam\n")
	decision = input()
	if decision == 1:
		print("Please enter image name with extension and place into folder:\n")
		img_name = input()
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
	f.write(name + "^^" + img_name)
	f.close()
	for img_name in os.listdir(getcwd()):
		if os.path.isfile(os.path.join(getcwd(), img_name)):
			os.rename(os.path.join(getcwd(), img_name), os.path.join(os.getcwd() + "/Images", img_name))

if __name__== "__main__":
	main()
