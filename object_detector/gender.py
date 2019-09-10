from keras.models import load_model
import numpy as np
import matplotlib.pyplot as plt
import cv2
import imutils
import dlib
from imutils.face_utils import FaceAligner

proto_path = 'deploy.prototxt.txt'
model_path = 'res10_300x300_ssd_iter_140000.caffemodel'
predictor_path = 'shape_predictor_68_face_landmarks.dat'

predictor = dlib.shape_predictor(predictor_path)
net = cv2.dnn.readNetFromCaffe(proto_path, model_path)
detector = dlib.get_frontal_face_detector()
fa = FaceAligner(predictor, desiredFaceWidth=160)

def detect_face_dl(image):
	(h, w) = image.shape[:2]
	blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
	net.setInput(blob)
	detections = net.forward()
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	for i in range(0, detections.shape[2]):
		confidence = detections[0, 0, i, 2]
		if confidence > 0:
			box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
			(start_x, start_y, end_x, end_y) = box.astype("int")
			y = (start_y - 10) if (start_y - 10) > 10 else (start_y + 10)
			# cv2.rectangle(image, (start_x, start_y), (end_x, end_y), (0, 0, 255), 2)
			rect = dlib.rectangle(left=int(start_x), top=int(start_y), right=int(end_x), bottom=int(end_y))
			image_centered = fa.align(image, gray, rect)

			return image_centered


def detect_face_dlib(image, gray, rects):
	for (i, rect) in enumerate(rects):
		image_centered = fa.align(image, gray, rect)
		return image_centered


def get_face(image):
    image_low = imutils.resize(image, width=150)
    gray = cv2.cvtColor(image_low, cv2.COLOR_BGR2GRAY)
    rects = detector(image_low, 1)
    if len(rects) > 0:
        face = detect_face_dlib(image_low, gray, rects)
    else:
        face = detect_face_dl(image_low)
    return face

def import_gender_model(path):
	model = load_model(path)
	model._make_predict_function()
	# print model.summary()
	return model

def gender_detect(image, model):
	face = get_face(image)
	gray_face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
	gray_face = cv2.resize(gray_face, (64,64))
	gray_face = gray_face.reshape(1, 64, 64, 1)
	ans = model.predict(gray_face)
	# print ans
	if ans[0][0] > ans[0][1]:
		return 'female'
	else:
		return 'male'
