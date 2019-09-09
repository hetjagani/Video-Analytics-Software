#! /usr/bin/env python
#  -*- coding: utf-8 -*-

import sys
import os
from motion_detector_video import *
from object_detector.detection import objectDetection
from object_detector.lic_plate_ocr import licencePlateRecog 
from object_detector.vehicle_count import vehicleCount
from object_detector.person_count import personCount

from Tkinter import * 
import Tkinter as tk
import Tkinter, Tkconstants, tkFileDialog
import threading
import tkMessageBox

try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    py3 = True

global inputFileName, outputFileName

class CheckBox:
    def __init__(self):
        self.state = IntVar()
        
    def createCheckBox(self, parent, text):
        self.state.set(0)
        self.checkbutton1 = tk.Checkbutton(parent, text=text, variable=self.state, 
                                            command=self.callBackFunc, onvalue=1, offvalue=0)        
        self.checkbutton1.pack(fill=X)

    def callBackFunc(self):
        self.state.set(self.state.get() ^ 1)

    def getState(self):
        return self.state.get()

class CountComboBox:
	def __init__(self):
		pass

	def createComboBox(self, parent, labels):
		self.countComboBox = ttk.Combobox(parent)
		self.countComboBox.pack(fill=X)
		self.countComboBox.configure(values=labels)
		self.countComboBox.configure(takefocus="")	

	def getCountComVal(self):
		return self.countComboBox.get()

class CountWinEntry:
	def __init__(self):
		pass

	def createEntry(self, parent):
		self.input = tk.Entry(parent)
		self.input.pack(fill=X)

	def getValue(self):
		return self.input.get()

def set_Tk_var():
    global combobox
    combobox = tk.StringVar()
    global personCheckBtn
    personCheckBtn = CheckBox()
    global vehicleCheckBtn   
    vehicleCheckBtn = CheckBox() 
    global animalCheckBtn
    animalCheckBtn = CheckBox()
    global countComboBox 

    countComboBox = CountComboBox()
    global countLineVal
    countLineVal = StringVar()

    global countLineROI
    countLineROI = CountWinEntry()
    global countLineROIVal
    countLineROIVal = StringVar()
    global countLineOff
    countLineOff = CountWinEntry()
    global countLineOffVal
    countLineOffVal = StringVar()
    global countThresh
    countThresh = CountWinEntry()
    global countThreshVal
    countThreshVal = StringVar()



def browseInput(root):

    inputFileName = tkFileDialog.askopenfilename(initialdir = "~/HD/VAS_Project",title = "Select file",filetypes = (("mp4 files","*.mp4"),("all files","*.*")))
    
    root.inputEntry.delete(0,'end')
    root.inputEntry.insert(0,inputFileName)

    sys.stdout.flush()

def browseOutput(root):

    outputFileName = tkFileDialog.askdirectory()

    root.outputEntry.delete(0,'end')
    root.outputEntry.insert(0,outputFileName)

    sys.stdout.flush()

def runFunction(root):

    function = root.functionComboBox.get() 
    inputFileName = root.inputEntry.get()
    outputFileName = root.outputEntry.get()

    if inputFileName == '' or outputFileName == '':
        tkMessageBox.showinfo('Warning!', 'Please select input file and output folder to continue!')
    else:
        if function == "Motion Detection":
            thr1 = threading.Thread(target = detect_motion, args = (root,inputFileName, outputFileName))
            thr1.start()

        if function == "Object Detection":
			pState = personCheckBtn.getState()
			vState = vehicleCheckBtn.getState()
			aState = animalCheckBtn.getState()

			pArr = ['person']
			vArr = ['bicycle', 'car', 'motorbike', 'aeroplane', 'bus', 'train', 'truck', 'boat']
			aArr = ['bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe']

			param = []
			stateArr = [pState, vState, aState]
			for i,s in enumerate(stateArr):
			    if s & 1:
			        if i == 0:
			            param += pArr
			        elif i == 1:
			            param += vArr
			        elif i == 2:
			            param += aArr

			thr2 = threading.Thread(target = objectDetection, args = (root, inputFileName, outputFileName, param))
			thr2.start()

        if function == "Number Plate Recognition":
            thr3 = threading.Thread(target = licencePlateRecog, args = (root, inputFileName, outputFileName))
            thr3.start()

        if function == "Vehicle Counting":
			thr4 = threading.Thread(target = vehicleCount, args = (root, inputFileName, outputFileName, countLineVal.get(), float(countThreshVal.get()), int(countLineROIVal.get()), int(countLineOffVal.get())))
			thr4.start()
			
        if function == "Person Counting":
			thr5 = threading.Thread(target = personCount, args = (root, inputFileName, outputFileName, countLineVal.get(), float(countThreshVal.get()), int(countLineROIVal.get()), int(countLineOffVal.get())))
			thr5.start()

    sys.stdout.flush()


def aboutUs(self):

    window = tk.Tk()
    window.title("VAS")
    window.geometry("400x225")

    F = tk.Frame(window)
    F.pack()

    w = Label(window, text="About Us", fg = "black", font=("Helvetica", 20)).pack()
    wn = Label(window, text="\n").pack()
    w1 = Label(window, text="Video Analytics Software\n This software is free to use.", fg = "black", anchor='center').pack()
    w2 = Label(window, text="Creators : HD and HJ.\n Feel free to contact us at abc@gmail.com", fg = "black", anchor='s').pack(side=BOTTOM)
    window.mainloop()

def showObjectWindow(root):
    function = root.functionComboBox.get() 

    if function == "Object Detection":
        root1 = tk.Tk()
        root1.title("Object Detection")
        root1.geometry('300x150')

        objectFrame = tk.Frame(root1)
        objectFrame.pack()

        label1 = tk.Label(root1)
        label1.pack(side=TOP) 
        label1.configure(text='''Select objects for detection : ''', anchor='nw')

        personCheckBtn.createCheckBox(root1, 'Person')
        vehicleCheckBtn.createCheckBox(root1, 'Vehicle')
        animalCheckBtn.createCheckBox(root1, 'Animal')

        okayBtn = tk.Button(root1)
        okayBtn.pack(side=BOTTOM)
        okayBtn.configure(command=lambda : destroyObjectWindow(root1,root))
        okayBtn.configure(text='''Okay''')

        root1.mainloop()

    if function == "Vehicle Counting" or function == "Person Counting":
    	# rVar = StringVar()
        root1 = tk.Tk()
        root1.title("Line option")
        root1.geometry('400x200')

        objectFrame = tk.Frame(root1)
        objectFrame.pack()

        label1 = tk.Label(root1)
        label1.pack(fill=X) 
        label1.configure(text='''Select vertical or horizontal line as per requirement : ''', anchor='nw')

        value_list = ["Horizontal","Vertical"]
        countComboBox.createComboBox(root1, value_list)

        label2 = tk.Label(root1)
        label2.pack(fill=X) 
        label2.configure(text='''Detection Threshold (0-1): ''', anchor='nw')

        countThresh.createEntry(root1)

        label3 = tk.Label(root1)
        label3.pack(fill=X) 
        label3.configure(text='''Detection ROI Thickness (in pixels): ''', anchor='nw')

        countLineROI.createEntry(root1)

        label4 = tk.Label(root1)
        label4.pack(fill=X) 
        label4.configure(text='''Detection ROI Offset (original at [screen-size / 4]): ''', anchor='nw')

        countLineOff.createEntry(root1)

        okayBtn = tk.Button(root1)
        okayBtn.pack(side=BOTTOM)
        okayBtn.configure(command=lambda : destroyCountSelect(root1,root))
        # okayBtn.configure(command=countSelect)
        okayBtn.configure(text='''Okay''')

        root1.mainloop() 

def destroyCountSelect(root1, root):
	countLineVal.set(str(countComboBox.getCountComVal()))
	countLineOffVal.set(str(countLineOff.getValue()))
	countThreshVal.set(str(countThresh.getValue()))
	countLineROIVal.set(str(countLineROI.getValue()))

	root.statusStrVar.set("You have selected ({}, {}, {}, {}) parameters.".format(countLineVal.get(), countThreshVal.get(), countLineROIVal.get(), countLineOffVal.get()))

	root1.destroy()

# def printState():
#     print personCheckBtn.getState()    

def init(top, gui, *args, **kwargs):
    global w, top_level, root
    w = gui
    top_level = top
    root = top

def destroyObjectWindow(root1, root):
    root1.destroy()

    pState = personCheckBtn.getState()
    vState = vehicleCheckBtn.getState()
    aState = animalCheckBtn.getState()

    sArr = ""
    if pState == 1:
        sArr += "Person "
    if vState == 1:
        sArr += "Vehicle "
    if aState == 1:
        sArr += "Animal "

    outStr = sArr.split(" ")
    if outStr == ['']:
    	root.statusStrVar.set("Please select at least one object to continue...")
    else:
    	root.statusStrVar.set('Selected Objects are - '+ ', '.join(outStr[:-1]))

if __name__ == '__main__':
    import vac
    vac.vp_start_gui()