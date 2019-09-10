import sys
import cv2
import numpy as np
import traceback

import darknet.python.darknet as dn

from src.label 				import Label, lwrite
from os.path 				import splitext, basename, isdir
from os 					import makedirs
from src.utils 				import crop_region, image_files_from_folder
from darknet.python.darknet import detect, nparray_to_image
from PIL import Image
from color_detector import *
from gender import *


def objectDetection(root, in_file, output_dir, classes):
    try:
        out_file = in_file.split('/')[-1].split('.')[0] + '_out'

        vehicle_threshold = .5

        vehicle_weights = 'object_detector/data/vehicle-detector/yolov2.weights'
        vehicle_netcfg  = 'object_detector/data/vehicle-detector/yolov2.cfg'
        vehicle_dataset = 'object_detector/data/vehicle-detector/coco.data'

        file_ptr = open(output_dir + '/' + out_file+'_obj.txt', 'w+')

        vehicle_net  = dn.load_net(vehicle_netcfg, vehicle_weights, 0)
        vehicle_meta = dn.load_meta(vehicle_dataset)

        if 'person' in classes:
            gen_model = import_gender_model('./gender_model.h5')

        writer = None
        cap = cv2.VideoCapture(in_file)
        cnt = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                root.statusStrVar.set('Done...Video saved at {}'.format(output_dir+'/'+out_file+'.mp4'))
                break

            print 'Processing frame {}..'.format(cnt)
            root.statusStrVar.set('Processing frame {}..'.format(cnt))

            img = nparray_to_image(frame)            
            R,_ = detect(vehicle_net, vehicle_meta, img, vehicle_threshold)
            R = [r for r in R if r[0] in classes]
            print '\t%d objects found' % len(R)
            
            txt = 'Frame No : {}\n'.format(cnt)
            
            if len(R):
                WH = np.array(frame.shape[1::-1],dtype=float)
                
                for i,r in enumerate(R):
                    name = r[0]
                    confidence = r[1]*100
                    cx,cy,w,h = (np.array(r[2])/np.concatenate( (WH,WH) )).tolist()
                    tl = (int((cx - w/2.)*WH[0]), int((cy - h/2.)*WH[1]))
                    br = (int((cx + w/2.)*WH[0]), int((cy + h/2.)*WH[1]))

                    object_img = frame[tl[1]:tl[1]+int(w*WH[1]), tl[0]:tl[0]+int(h*WH[0])]
                    
                    if name == 'car':
                        color = ''
                        if object_img.shape[0] > 0 and object_img.shape[1] > 0:
                            color = process_image(Image.fromarray(object_img))
                            # color = get_color(object_img)
                        
                        txt += '\t Object Name, Coords : {}, ({}, {})\n'.format(name, tl, br)
                        txt += '\t Object confidence : '+'{:.2f}'.format(confidence)+'\n'
                        txt += '\t Vehicle Color : {}\n\n'.format(color)
                        
                        cv2.putText(frame, '{} ('.format(name)+'{:.2f}'.format(confidence)+', {})'.format(color), tl, cv2.FONT_HERSHEY_SIMPLEX ,1, (0,0,255),2,cv2.LINE_AA)
                    if name == 'person':
                        gender = ''
                        if object_img.shape[0] > 0 and object_img.shape[1] > 0:
                            gender = gender_detect(object_img, gen_model)

                        txt += '\t Object Name, Coords : {}, ({}, {})\n'.format(name, tl, br)
                        txt += '\t Object confidence : '+'{:.2f}'.format(confidence)+'\n'
                        txt += '\t Person gender : {}\n\n'.format(gender)
                        
                        cv2.putText(frame, '{} ('.format(name)+'{:.2f}'.format(confidence)+', {})'.format(gender), tl, cv2.FONT_HERSHEY_SIMPLEX ,1, (0,0,255),1,cv2.LINE_AA)
                    if name != 'car' and name != 'person':
                        txt += '\t Object Name, Coords : {}, ({}, {})\n'.format(name, tl, br)
                        txt += '\t Object confidence : '+'{:.2f}'.format(confidence)+'\n\n'
                        
                        cv2.putText(frame, '{} ('.format(name)+'{:.2f}'.format(confidence)+')', tl, cv2.FONT_HERSHEY_SIMPLEX ,1, (0,0,255),2,cv2.LINE_AA)

                    print '\t\t{}th Coodrs : ({}, {})'.format(i, tl, br)
                    cv2.rectangle(frame, tl, br, (255,0,0),2) #crop_region(Iorig,label)

                file_ptr.write(txt)
                print '\n'
            
            if writer is None:
                fourcc = cv2.VideoWriter_fourcc(*'DIVX')
                writer = cv2.VideoWriter(output_dir+'/'+out_file+'.mp4', fourcc, 30,(frame.shape[1], frame.shape[0]), True)
            
            writer.write(frame)            
            del frame
            cnt += 1

    except:
        traceback.print_exc()
        sys.exit(1)
    
    file_ptr.close()
    writer.release()
    cap.release()
    sys.exit(0)
