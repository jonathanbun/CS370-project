import server
print("#####################################")
print("Type live for Live Stream or fr for facial recognition")
while True:
	response = input()
	if response == "live":
		server.run()
	if response == "fr":
		facerec.run()