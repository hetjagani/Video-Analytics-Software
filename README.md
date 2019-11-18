# Video Analytics Software



## Description

        General purpose video analytics software is an easy to use software that includes functionalities which are Object Detection, Object Counting, Number Plate Recognition and provides general analytic information about any video.
    

        Object detection is a computer technology related to computer vision and image processing that deals with detecting instances of semantic objects of a certain class (such as humans, buildings, or cars) in digital images and videos. Object Counting is a method of counting the detected objects of certain class in digital images and videos. Number Plate Recognition is the method used by a computer to conver digital images of vehicle license plates into electronic text.
    

        The general analytic information for Object Detection includes information such as frame number, gender, color, bounding box coordinates and confidence score for the object detected in the video. In Number Plate Recognition, the software outputs all the recognized License plates and corresponding bounding boxes.


        The software is built in a modular way, providing a simple graphical user interface which is easy to use and understand. The core software module relies on the library Darknet which is written in C and CUDA for better performance on GPUs. The output of above-mentioned functionalities is a video and a text file containing analytical information about the provided video.



## Dependencies

* Open CV for python

* Numpy

* Python Imaging Library (PIL)

* Keras

* Pytesseract

* Darknet Library (for setup goto [darknet](https://pjreddie.com/darknet/). I advice to build with GPU)

* Tkinter (for GUI stuff)



        To run the software run `python2 vas.py`. But first you have to setup all the dependencies that are mentioned. 

        

        One can use different modules from the code. The code is simple to understand and different implementations of the modules are implemented in `object_detector` directory. Different pretrained models are stored in `object_detector/data/` directory. You have to download weights for the models. The weights can be downloaded from above darknet link.


