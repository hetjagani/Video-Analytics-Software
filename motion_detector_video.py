# -*- coding: utf-8 -*-

import imutils
import cv2
import numpy as np
import sys

# Number of frames to pass before changing the frame to compare the current
# frame against
FRAMES_TO_PERSIST = 10

# Minimum boxed area for a detected motion to count as actual motion
# Use to filter out noise or small objects
MIN_SIZE_FOR_MOVEMENT = 2000

# Minimum length of time where no motion is detected it should take
#(in program cycles) for the program to declare that there is no movement
MOVEMENT_DETECTED_PERSISTENCE = 100

# =============================================================================
# CORE PROGRAM
# =============================================================================
def detect_motion(root,file_name, out_dir):
    
    out_file = file_name.split('/')[-1].split('.')[0] + '_out'

    # Create capture object
    cap = cv2.VideoCapture(file_name) # Then start the webcam

    fps = cap.get(cv2.CAP_PROP_FPS)
    root.statusStrVar.set('FPS : {}'.format(fps))

    # Init frame variables
    first_frame = None
    next_frame = None

    # Init display font and timeout counters
    font = cv2.FONT_HERSHEY_SIMPLEX
    delay_counter = 0
    movement_persistent_counter = 0
    cnt = 0
    writer = None

    # LOOP!
    while True:

        # Set transient motion detected as false
        transient_movement_flag = False
        
        # Read frame
        ret, frame = cap.read()
        text = "Unoccupied"

        # If there's an error in capturing
        if not ret:
            break
            
        # Resize and save a greyscale version of the image
        frame = imutils.resize(frame, width = 750)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Blur it to remove camera noise (reducing false positives)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # If the first frame is nothing, initialise it
        if first_frame is None: first_frame = gray    

        delay_counter += 1

        # Otherwise, set the first frame to compare as the previous frame
        # But only if the counter reaches the appriopriate value
        # The delay is to allow relatively slow motions to be counted as large
        # motions if they're spread out far enough
        if delay_counter > FRAMES_TO_PERSIST:
            delay_counter = 0
            first_frame = next_frame

            
        # Set the next frame to compare (the current frame)
        next_frame = gray

        # Compare the two frames, find the difference
        frame_delta = cv2.absdiff(first_frame, next_frame)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]

        # Fill in holes via dilate(), and find contours of the thesholds
        thresh = cv2.dilate(thresh, None, iterations = 2)
        cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # loop over the contours
        for c in cnts:

            # Save the coordinates of all found contours
            (x, y, w, h) = cv2.boundingRect(c)
            
            # If the contour is too small, ignore it, otherwise, there's transient
            # movement
            if cv2.contourArea(c) > MIN_SIZE_FOR_MOVEMENT:
                transient_movement_flag = True
                
                # Draw a rectangle around big enough movements
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # The moment something moves momentarily, reset the persistent
        # movement timer.
        if transient_movement_flag == True:
            movement_persistent_flag = True
            movement_persistent_counter = MOVEMENT_DETECTED_PERSISTENCE

        # As long as there was a recent transient movement, say a movement
        # was detected

        if writer is None:
            fourcc = cv2.VideoWriter_fourcc(*'DIVX')
            writer = cv2.VideoWriter(out_dir+'/'+out_file+'.mp4', fourcc, 30,(frame.shape[1],frame.shape[0]), True)

        if movement_persistent_counter > 0:
            text = "Movement Detected (Seconds): " + str(cnt / fps)
            cv2.putText(frame, str(text), (10,35), font, 0.75, (255,255,255), 2, cv2.LINE_AA)
            writer.write(frame)
            movement_persistent_counter -= 1
        root.statusStrVar.set('Processing frame {}'.format(cnt))
        cnt += 1
    root.statusStrVar.set('Done...Video saved at {}'.format(out_dir+'/'+out_file+'.mp4'))