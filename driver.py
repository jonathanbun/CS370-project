import server
import facerec
print("#####################################")
print("#####################################")
print("#####################################")
print("To run continuous video stream: press 1")
print("To run facial recognition: press 2")
print("To exit: press q")
print("-------------------------------------")

while True:
	response = input()
	if response == "2":
		print("Continuous stream booting...")
		server.run()
	if response == "2":
		print("Facial recognition booting..")
		facerec.run()
	if response == "3":
		print("Shutting down...")
		sys.exit()