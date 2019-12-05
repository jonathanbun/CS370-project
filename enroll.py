import face_recognition
import cv2
import numpy as np
import os
import shutil


def main():
	img_name = ""
	name = input("Welcome to enrollment! Please enter your name:\n")
	img_name = input("Please enter image name with extension and place into folder:\n")


	f = open("enrolled.txt", "a")
	f.write("\n"+name + "^^" + img_name)
	f.close()

if __name__== "__main__":
	main()
