import numpy as np
import cv2
import socket

# Address to send requests
SERVER_ADDR = ('127.0.0.1', 8000)
# Port to receive frames
CLIENT_PORT = 8008


def connect():
	print 'Connecting to the server'
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.connect(SERVER_ADDR)
	s.sendall('N')
	s.close()

def disconnect():
	print 'Disconnecting from the server'
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.connect(SERVER_ADDR)
	s.sendall('R')
	s.close()

def shutdown():
	print 'Shutting down the server'
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.connect(SERVER_ADDR)
	s.sendall('Q')
	s.close()


if __name__ == '__main__':
	cv2.namedWindow("Video")

	# Create an UDP socket to receive the frames and bind to the port
	receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	receiver.bind(('', CLIENT_PORT))
	print 'Receiver ready'
	# Request a connection to the cam server
	connect()

	print "--------------------------------------------------------"
	print "-- Press 'q' to close the client"
	print "-- Press 's' to close the client and shutdown the server"
	print "--------------------------------------------------------"
	
	key = -1
	data = ''
	while key != ord('q') and key != ord('s'):
		new_data, addr = receiver.recvfrom(1024)
		data += new_data
		# Try to find the start and end of the jpg bytes and extract the image
		jpg_start = data.find('\xff\xd8')
		jpg_end = data.find('\xff\xd9')
		if jpg_start != -1 and jpg_end != -1:
			# Extract the jpg string and remove it from the buffer
			jpg_img = data[jpg_start:jpg_end + 2]
			data = data[jpg_end + 2:]
			# Try to decode the jpg string to get the image matrix
			img = cv2.imdecode(np.fromstring(jpg_img, dtype=np.uint8), cv2.IMREAD_COLOR)
			if img is not None:
				cv2.imshow("Video", img)
			else:
				print 'Image is None'

		key = cv2.waitKey(1) & 0x00FF

	# Close things
	print 'Closing resources...'
	receiver.close()
	disconnect()
	if (key == ord('s')):
		shutdown()
	cv2.destroyAllWindows()
