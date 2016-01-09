""" TODO: Docs
"""

import cv2
from picamera import PiCamera
from picamera.array import PiRGBArray
from time import sleep
import socket
from threading import Thread



# Port to listen connection requests
SERVER_PORT = 8000
# Port where cam clients will listen to receive frames
CLIENT_PORT = 8008

connected_clients = []

class CamThread(Thread):
	""" Thread to continuously read incoming frames from the raspberry pi camera
		and send those frames to all the clients connected to the server.
	"""
	def __init__(self):
		print 'init CamThread'
		self.cam = PiCamera()
		self.cam.resolution = (480,320)
		self.cam.framerate = 25
		self.rawCap = PiRGBArray(self.cam)
		# Wait for the webcam to open
		sleep(0.2)

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		Thread.__init__(self)
		self.daemon = True
		self.running = True

	def run(self):
		print 'CamThread running'
		for frame in self.cam.capture_continuous(self.rawCap, format='bgr', use_video_port=True):
			if not self.running:
				break

			img = self.rawCap.array
			rows, cols, channels = img.shape

			if rows > 0 and cols > 0:
				# 180 degrees rotation
				img = self.rotate(img, 180)

				# Serialize and send
				img_ser = self.encode(img, '.jpg')
				for c in connected_clients:
					self.send(img_ser, (c, CLIENT_PORT))
			# Clear the camera buffer begore grabbing the next frame
			self.rawCap.truncate(0)
		self.sock.close()
		self.cam.close()

	def encode(self, img, ext='.jpg'):
		return cv2.imencode(ext, img)[1].tostring()

	def rotate(self, frame, angle):
		rows, cols, channels = frame.shape
		RotMat = cv2.getRotationMatrix2D((cols/2, rows/2), angle, 1)
		return cv2.warpAffine(frame, RotMat, (cols, rows))

	def send(self, data, addr):
		# Send the data splitted in oackets of 1024 bytes
		while len(data) > 1024:
			self.sock.sendto(data[:1024], addr)
			data = data[1024:]
		if len(data) > 0:
			self.sock.sendto(data, addr)

	def stop(self):
		self.running = False


if __name__ == '__main__':
	cam_server = CamThread()
	cam_server.start()

	# Listen to connections and connect the clients with the cam server thread
	print 'Creating socket...'
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind(('', SERVER_PORT))
	server_socket.listen(2)
	print 'Socket bound and listening'
	
	while True:
		cli, addr = server_socket.accept()
		print 'New connection from: {}'.format(addr)
		# handle request
		data = cli.recv(8)
		data = data.rstrip()

		if data == 'Q':		# Close server
			break
		elif data == 'N':	# New cam client
			if (addr[0] not in connected_clients):
				connected_clients.append(addr[0]) # Save the host addr
		elif data == 'R':	# Remove client addr from list
			try:
				connected_clients.remove(addr[0])
			except ValueError, ve:
				# Addr not in list. Do nothing
				pass


	print 'Shutting down...'
	server_socket.shutdown(socket.SHUT_RDWR)
	server_socket.close()
	cam_server.stop()