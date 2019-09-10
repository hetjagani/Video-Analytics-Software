import sys
import cv2
import numpy as np
import traceback

import os
import darknet.python.darknet as dn

from src.utils 				import crop_region, image_files_from_folder
from darknet.python.darknet import detect, nparray_to_image

def vehicleCount(root, in_file, output_dir, lineState = 'Horizontal', thresh = 0.5, roiThick = 7, offset = 0):     

    try:
        out_file = in_file.split('/')[-1].split('.')[0] + '_out'
            
        vehicle_threshold = thresh
        roi = roiThick

        vehicle_weights = 'object_detector/data/vehicle-detector/yolov2.weights'
        vehicle_netcfg  = 'object_detector/data/vehicle-detector/yolov2.cfg'
        vehicle_dataset = 'object_detector/data/vehicle-detector/coco.data'

        vehicle_net  = dn.load_net(vehicle_netcfg, vehicle_weights, 0)
        vehicle_meta = dn.load_meta(vehicle_dataset)

        writer = None
        cap = cv2.VideoCapture(in_file)
        cnt = 0
        car_count = 0
        while cap.isOpened():
            
            ret, frame = cap.read()

            if not ret:
                root.statusStrVar.set('Done...Video saved at {}'.format(output_dir+'/'+out_file+'.mp4'))
                break

            WH = frame.shape[:2]
            img = nparray_to_image(frame)            
            R,_ = detect(vehicle_net, vehicle_meta, img, vehicle_threshold)

            if lineState == "Horizontal":
                linel = (0, WH[0] - (WH[0] / 4) - offset)
                liner = (WH[1], WH[0] - (WH[0] / 4) - offset)
            elif lineState == "Vertical":
                lineu = (WH[1] - (WH[1] / 4) - offset, 0)
                lined = (WH[1] - (WH[1] / 4) - offset, WH[1])
        
            R = [r for r in R if r[0] in ['car','bus']]

            print 'Processing frame {}'.format(cnt)
            root.statusStrVar.set('Processing frame {}..'.format(cnt))
            print '\t%d cars found' % len(R)
            
            if len(R):
                WH = np.array(frame.shape[1::-1],dtype=float)
                for i,r in enumerate(R):
                    name = r[0]
                    cx,cy,w,h = (np.array(r[2])/np.concatenate( (WH,WH) )).tolist()
                    tl = (int((cx - w/2.)*WH[0]), int((cy - h/2.)*WH[1]))
                    br = (int((cx + w/2.)*WH[0]), int((cy + h/2.)*WH[1]))
                    print '\t\t{}th car Coodrs : ({}, {})'.format(i, tl, br)
                    
                    cv2.rectangle(frame, tl, br, (255,0,0),2) #crop_region(Iorig,label)
                    
                    if lineState == "Horizontal":
                        cv2.line(frame, linel, liner, (0,0,255), 3)

                        if (cy-h/2)*WH[1] > liner[1] and (cy-h/2)*WH[1] < liner[1] + roi:
                            car_count += 1
                    elif lineState == "Vertical":
                        cv2.line(frame, lineu, lined, (0,0,255), 3)

                        if (cx-w/2)*WH[0] > lineu[0] and (cx-w/2)*WH[0] < lineu[0] + roi:
                            car_count += 1

                    cv2.putText(frame, name, tl, cv2.FONT_HERSHEY_SIMPLEX ,1.5, (0,0,255),3,cv2.LINE_AA)

                    cv2.putText(frame, 'Vehicles crossed : '+str(car_count), (0, int(WH[1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, cv2.LINE_AA)
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
    
    writer.release()
    cap.release()
    sys.exit(0)
