import cv2

cap = cv2.VideoCapture()
cap.open(0)
ret, img = cap.read()

if not ret:
	print "Could not read the image"
	exit(1)

img_str = cv2.imencode('.jpg', img)[1].tostring()
print 'Length: {}'.format(len(img_str)) 
with open('img.str', 'w') as f:
	f.write(img_str)
