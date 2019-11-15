# import necessary modules

# we can edit this as needed

import smtplib
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


def notify():
	# email address we're sending notifications from
	fromEmail = "jgarcia6102@gmail.com"

	# app password to login to email
	appPassword = "vctmzkyasctpgeut"
	# this is just a test
	toEmail = "jgarc110@rams.colostate.edu"

	# create smtp object, login to gmail smtp server
	smtpObj = smtplib.SMTP('smtp.gmail.com',587)
	# enable encryption
	smtpObj.starttls()
	# initial server hello
	smtpObj.ehlo()

	smtpObj.login(fromEmail,appPassword)

	msg = MIMEMultipart()

	msg['From'] = fromEmail
	msg['Subject'] = "i think there is a stabber"
	msg['To'] = toEmail

	readImage = open("stabber.jpg",'rb').read()

	image = MIMEImage(readImage, name="stabber.jpg")

	msg.attach(image)

	smtpObj.sendmail(fromEmail, toEmail, msg.as_string())

	smtpObj.quit()



def main():

	notify()

if __name__ == '__main__':
	main()





	



