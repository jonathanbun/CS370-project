
from flask import Flask, render_template, Response
from example import securityCamera
import time
import threading
import sys
from notify import *

app = Flask(__name__)

video_stream = securityCamera()


@app.route('/')
def index():
    return render_template('index.html')

def gen(example):
    while True:
        frame = example.process()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(video_stream),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':



	app.run(host='0.0.0.0', debug=False, threaded=True)
