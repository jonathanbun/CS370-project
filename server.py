import io #buffered binary streams
import picamera #camera API
import socketserver #framework for network server
import logging #needed for streaming handler
from threading import Condition #allow thread to wait until notified
import threading
from http import server #need to impliment server
import sys

#HTML for website
PAGE="""\
<html>
<head>
<title>Pi Camera Video Feed</title>
</head>
<body>
<center><h1>Pi Camera Video Feed</h1></center>
<center><img src="stream.mjpg" width="640" height="480"></center>
</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        #check for new frame
        if buf.startswith(b'\xff\xd8'):
            #resize the stream
            self.buffer.truncate()
            with self.condition:
                #return new frame
                self.frame = self.buffer.getvalue()
                #notify 
                self.condition.notify_all()
            #set stream position to beginning
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    output = None
    #handle HTTP requests that arrive at the server
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with StreamingHandler.output.condition:
                        StreamingHandler.output.condition.wait()
                        frame = StreamingHandler.output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                print("Exceptionnnnnnnnn")
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()




        

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    #daemon threads don't need to be tracked, they will be killed automatically when the program exits
    daemon_threads = True
    def __init__(self, address, handler, output):
        handler.output = output
        super().__init__(address, handler)



   

with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)
    
        server = StreamingServer(address, StreamingHandler, output)
        server.serve_forever()

    finally:
        camera.stop_recording()

