import server
import facerec
import sys
print("*************************************")
print("*************************************")
print("To run continuous video stream: press 1")
print("To run facial recognition: press 2")
print("To exit: press q")
print("-------------------------------------")

while True:
	response = input()
	if response == "1":
		print("Continuous stream booting...")
		server.run()
	if response == "2":
		print("Facial recognition booting...")
		facerec.run()
	if response == "q":
		print("Shutting down...")
		sys.exit()
	else:
		print("Invalid option selected...")
		print("-------------------------------------")
		print("To run continuous video stream: press 1")
		print("To run facial recognition: press 2")
		print("To exit: press q")
		print("-------------------------------------")