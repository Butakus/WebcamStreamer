import numpy as np
import cv2


with open('img.str', 'r') as f:
	img_str = f.read()

img = cv2.imdecode(np.fromstring(img_str, dtype=np.uint8), cv2.IMREAD_COLOR)
cv2.imwrite("img.jpg", img)

