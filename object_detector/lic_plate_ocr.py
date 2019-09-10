import sys, os
import keras
import cv2
import traceback

from object_detector.src.keras_utils 			import load_model
from object_detector.src.utils 					import im2single, nms
from object_detector.src.keras_utils 			import load_model, detect_lp
from object_detector.src.label 					import Shape, writeShapes, dknet_label_conversion
import numpy as np
from glob import glob

import darknet.python.darknet as dn
from darknet.python.darknet import detect, nparray_to_image


def adjust_pts(pts,lroi):
	return pts*lroi.wh().reshape((2,1)) + lroi.tl().reshape((2,1))


from copy import deepcopy
from PIL import Image
import pytesseract as tess
import sys
import re
import shutil

def preprocess(img):
	cv2.imshow("Input",img)
	imgBlurred = cv2.GaussianBlur(img, (5,5), 0)
	gray = cv2.cvtColor(imgBlurred, cv2.COLOR_BGR2GRAY)

	sobelx = cv2.Sobel(gray,cv2.CV_8U,1,0,ksize=3)
	#cv2.imshow("Sobel",sobelx)
	#cv2.waitKey(0)
	ret2,threshold_img = cv2.threshold(sobelx,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
	#cv2.imshow("Threshold",threshold_img)
	#cv2.waitKey(0)
	return threshold_img

def cleanPlate(plate):
	# print "CLEANING PLATE. . ."
	gray = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)
	#kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
	#thresh= cv2.dilate(gray, kernel, iterations=1)

	_, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
	contours,hierarchy = cv2.findContours(thresh.copy(),cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

	if contours:
		areas = [cv2.contourArea(c) for c in contours]
		max_index = np.argmax(areas)

		max_cnt = contours[max_index]
		max_cntArea = areas[max_index]
		x,y,w,h = cv2.boundingRect(max_cnt)

		if not ratioCheck(max_cntArea,w,h):
			return plate,None

		cleaned_final = thresh[y:y+h, x:x+w]
		#cv2.imshow("Function Test",cleaned_final)
		return cleaned_final,[x,y,w,h]

	else:
		return plate,None


def extract_contours(threshold_img):
	element = cv2.getStructuringElement(shape=cv2.MORPH_RECT, ksize=(17, 3))
	morph_img_threshold = threshold_img.copy()
	cv2.morphologyEx(src=threshold_img, op=cv2.MORPH_CLOSE, kernel=element, dst=morph_img_threshold)
	cv2.imshow("Morphed",morph_img_threshold)
	cv2.waitKey(0)

	im2,contours, hierarchy= cv2.findContours(morph_img_threshold,mode=cv2.RETR_EXTERNAL,method=cv2.CHAIN_APPROX_NONE)
	return contours


def ratioCheck(area, width, height):
	ratio = float(width) / float(height)
	if ratio < 1:
		ratio = 1 / ratio

	aspect = 4.7272
	min = 15*aspect*15  # minimum area
	max = 125*aspect*125  # maximum area

	rmin = 3
	rmax = 6

	if (area < min or area > max) or (ratio < rmin or ratio > rmax):
		return False
	return True

def isMaxWhite(plate):
	avg = np.mean(plate)
	if(avg>=115):
		return True
	else:
 		return False

def validateRotationAndRatio(rect):
	(x, y), (width, height), rect_angle = rect

	if(width>height):
		angle = -rect_angle
	else:
		angle = 90 + rect_angle

	if angle>15:
	 	return False

	if height == 0 or width == 0:
		return False

	area = height*width
	if not ratioCheck(area,width,height):
		return False
	else:
		return True



def cleanAndRead(plate_img):
	clean_plate = plate_img

	if(isMaxWhite(plate_img)):
		clean_plate, rect = cleanPlate(plate_img)

	plate_im = Image.fromarray(clean_plate)
	text = tess.image_to_string(plate_im, lang='eng')
	return text.encode('ascii', 'ignore')



def licencePlateRecog(root, in_file, output_dir):

	try:

		out_file = in_file.split('/')[-1].split('.')[0] + '_out'
			
		if os.path.exists(output_dir+'/'+out_file) and os.path.isdir(output_dir+'/'+out_file):	
			shutil.rmtree(output_dir+'/'+out_file)
		os.makedirs(output_dir+'/'+out_file)
		file_ptr = open(output_dir + '/' + out_file+'_ocr.txt', 'w+')
		
		lp_threshold = .5
		regx = re.compile('^[A-Z]{2}\\s?[0-9]{2}\\s?[A-Z][A-Z]?\\s?[0-9]{4}$')
		
		wpod_net_path = 'object_detector/data/lp-detector/wpod-net_update1.h5'
		wpod_net = load_model(wpod_net_path)

		writer = None
		cap = cv2.VideoCapture(in_file)

		fps = cap.get(cv2.CAP_PROP_FPS)

		print 'Detecting Number plates...'
		cnt = 0
		matched = ''
		
		while cap.isOpened():

			ret,Ivehicle = cap.read()

			if not ret:
			    root.statusStrVar.set('Done...Video saved at {}'.format(output_dir+'/'+out_file+'.mp4'))
			    break

			print 'Processing %s frame...' % str(cnt)

			root.statusStrVar.set('Processing frame {}..'.format(cnt))

			
			WH = Ivehicle.shape

			ratio = float(max(Ivehicle.shape[:2]))/min(Ivehicle.shape[:2])
			side  = int(ratio*288.)
			bound_dim = min(side + (side%(2**4)),608)
			
			Llp,LlpImgs,_ = detect_lp(wpod_net,im2single(Ivehicle),bound_dim,2**4,(240,80),lp_threshold)

			if len(LlpImgs):
				for j,Ilp in enumerate(LlpImgs):
					## Performing OCR on the image
					Ilp = LlpImgs[j]
					Ilp = Ilp*255
					# Ilp = cv2.cvtColor(Ilp, cv2.COLOR_BGR2GRAY)
					# Ilp = cv2.cvtColor(Ilp, cv2.COLOR_GRAY2BGR)

					tl = Llp[j].tl() * [WH[1], WH[0]] # (int(tlx*WH[1]), int(tly*WH[0]))
					br = Llp[j].br() * [WH[1], WH[0]] # (int(brx*WH[1]), int(bry*WH[0]))

					tl, br = (int(tl[0]), int(tl[1])), (int(br[0]), int(br[1]))
					print '\t Detections : ', tl, br
				
					nplate_txt = cleanAndRead(Ilp.astype(np.uint8))
					# nplate_txt = re.sub('[#!@#$%^&*()_-+|;:\'""<>?/.,`~=]', '', nplate_txt)
					nplate_txt = re.sub(r'[^\w]', '', nplate_txt)	
						
					print 'Detected plate : {}'.format(nplate_txt)

					cv2.putText(Ivehicle, nplate_txt, tl, cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),2, lineType=cv2.LINE_AA)

					cv2.rectangle(Ivehicle, tl, br, (255,0,0),2)
				
					if regx.match(nplate_txt):
						cv2.imwrite(output_dir + '/' + out_file+'/'+str(cnt)+'_'+str(j)+'.png', Ivehicle)
						txt = 'Frame No, Time : '+str(cnt)+', '+str(cnt/fps)+'\n'
						txt += '\tDetections Coords : '+str(tl[0])+', '+str(tl[1])+', '+str(br[0])+', '+str(br[1])+'\n'
						txt += '\tDetected Plate : '+str(nplate_txt)+'\n\n'
						file_ptr.write(txt)

			if writer is None:
				fourcc = cv2.VideoWriter_fourcc(*'DIVX')
				writer = cv2.VideoWriter(output_dir+'/'+out_file+'.mp4', fourcc, 30,(Ivehicle.shape[1],Ivehicle.shape[0]), True)
            
			writer.write(Ivehicle)
			cnt += 1
	except:
		traceback.print_exc()
		sys.exit(1)

	file_ptr.close()

	sys.exit(0)


