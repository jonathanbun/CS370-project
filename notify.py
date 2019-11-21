"""
notification module
"""
import smtplib
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import os

# for the sake of oop
class notifier:

	def send(self, name ,recipientAddress,tempImage):

		# email we're sending notifications from
		fromEmail = "jgarcia6102@gmail.com"
		# for the sake of security we will add the app password when we're testing it/demoing
		# dont want my email password floating around on github
		appPassword = "zcwvguwdmtkfiuyk"
		# to email is recipient which is an email address
		toEmail = recipientAddress

		# create smtp object, login to the gmail smtp server
		smtpObj = smtplib.SMTP('smtp.gmail.com', 587)

		# enable encryption through tls
		smtpObj.starttls()

		# initial server handshake
		smtpObj.ehlo()

		# login to the email address
		smtpObj.login(fromEmail, appPassword)

		# create a msg
		msg = MIMEMultipart()

		msg['From'] = fromEmail
		# if name is unknown say so, else say who is at the door
		if name == "Unknown":

			msg['Subject'] = "Unknown is at the door!"

		else:

			msg['Subject'] = name + "  is at the door!"
		# read the image
		readImage = open(tempImage, 'rb').read()

		image = MIMEImage(readImage, name=tempImage)
		# attach image to the message
		msg.attach(image)

		smtpObj.sendmail(fromEmail, toEmail, msg.as_string())

		smtpObj.quit()




