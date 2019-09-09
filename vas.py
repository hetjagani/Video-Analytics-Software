#! /usr/bin/env python
#  -*- coding: utf-8 -*-

import sys

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    py3 = True

import vas_support

def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root
    root = tk.Tk()
    vac_support.set_Tk_var()
    top = Toplevel1 (root)
    vac_support.init(root, top)
    root.mainloop()

w = None
def create_Toplevel1(root, *args, **kwargs):
    '''Starting point when module is imported by another program.'''
    global w, w_win, rt
    rt = root
    w = tk.Toplevel (root)
    vac_support.set_Tk_var()
    top = Toplevel1 (w)
    vac_support.init(w, top, *args, **kwargs)
    return (w, top)

def destroy_Toplevel1():
    global w
    w.destroy()
    w = None

class Toplevel1:
    
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#ececec' # Closest X11 color: 'gray92'
        self.style = ttk.Style()
        if sys.platform == "win32":
            self.style.theme_use('winnative')
        self.style.configure('.',background=_bgcolor)
        self.style.configure('.',foreground=_fgcolor)
        self.style.configure('.',font="TkDefaultFont")
        self.style.map('.',background=
            [('selected', _compcolor), ('active',_ana2color)])

        top.geometry("600x450+496+326")
        top.title("VAS - Video Analytics Software")
        top.configure(highlightcolor="black")

        self.Frame1 = tk.Frame(top)
        self.Frame1.place(relx=0.033, rely=0.044, relheight=0.878
                , relwidth=0.942)
        self.Frame1.configure(relief='groove')
        self.Frame1.configure(borderwidth="2")
        self.Frame1.configure(relief="groove")
        self.Frame1.configure(width=565)

        self.my_menu = tk.Menu(root)
        root.config(menu=self.my_menu)

        #dropdown menu - file menu (submenu)
        self.fileMenu = tk.Menu(self.my_menu)
        self.my_menu.add_cascade(label="File", menu=self.fileMenu)
        self.fileMenu.add_command(label="Open input file", command=self.inputFile)
        self.fileMenu.add_command(label="Open output folder", command=self.outputDir)
        self.fileMenu.add_separator()  
        self.fileMenu.add_command(label="Exit", command=root.destroy)

        #dropdown menu - help menu
        self.helpMenu = tk.Menu(self.my_menu)
        self.my_menu.add_cascade(label="Help", menu=self.helpMenu)
        self.helpMenu.add_command(label="About us", command=self.aboutUs)


        self.inputEntry = tk.Entry(self.Frame1)
        self.inputEntry.place(relx=0.212, rely=0.076,height=23, relwidth=0.595)
        self.inputEntry.configure(text="",background="white")
        self.inputEntry.configure(font="TkFixedFont")
        self.inputEntry.configure(selectbackground="#c4c4c4")

        self.Label1 = tk.Label(self.Frame1)
        self.Label1.place(relx=0.035, rely=0.089, height=21, width=81)
        self.Label1.configure(activebackground="#f9f9f9")
        self.Label1.configure(text='''Input File :''')

        self.inputBrowseBtn = tk.Button(self.Frame1)
        self.inputBrowseBtn.place(relx=0.85, rely=0.076, height=31, width=76)
        self.inputBrowseBtn.configure(activebackground="#f9f9f9")
        self.inputBrowseBtn.configure(command=self.inputFile)
        self.inputBrowseBtn.configure(text='''Browse''')

        self.Label1_1 = tk.Label(self.Frame1)
        self.Label1_1.place(relx=0.018, rely=0.228, height=21, width=91)
        self.Label1_1.configure(activebackground="#f9f9f9")
        self.Label1_1.configure(text='''Output Dir  :''')

        self.outputEntry = tk.Entry(self.Frame1)
        self.outputEntry.place(relx=0.212, rely=0.215, height=23, relwidth=0.595)
        self.outputEntry.configure(background="white")
        self.outputEntry.configure(font="TkFixedFont")
        self.outputEntry.configure(selectbackground="#c4c4c4")

        self.outputBrowseBtn = tk.Button(self.Frame1)
        self.outputBrowseBtn.place(relx=0.85, rely=0.203, height=31, width=76)
        self.outputBrowseBtn.configure(activebackground="#f9f9f9")
        self.outputBrowseBtn.configure(command=self.outputDir)
        self.outputBrowseBtn.configure(text='''Browse''')

        self.functionComboBox = ttk.Combobox(self.Frame1)
        self.functionComboBox.place(relx=0.221, rely=0.43, relheight=0.053
                , relwidth=0.579)
        self.value_list = ["Object Detection","Number Plate Recognition","Motion Detection","Vehicle Counting","Person Counting"]
        self.functionComboBox.configure(values=self.value_list)
        self.functionComboBox.configure(textvariable=vac_support.combobox)

        self.functionComboBox.configure(takefocus="")
        self.functionComboBox.bind("<<ComboboxSelected>>", self.objectWindow)

        self.Label1_4 = tk.Label(self.Frame1)
        self.Label1_4.place(relx=0.035, rely=0.43, height=21, width=81)
        self.Label1_4.configure(activebackground="#f9f9f9")
        self.Label1_4.configure(text='''Function :''')

        self.runBtn = tk.Button(self.Frame1)
        self.runBtn.place(relx=0.841, rely=0.418, height=31, width=76)
        self.runBtn.configure(activebackground="#f9f9f9")
        self.runBtn.configure(command=self.run)
        self.runBtn.configure(text='''Run''')

        self.Label5 = tk.Label(top)
        self.Label5.place(relx=0.033, rely=0.933, height=21, width=57)
        self.Label5.configure(text='''Status :''')

        self.statusStrVar = tk.StringVar()
        self.statusStrVar.set('Welcome to VAS!')
        self.statusLbl = tk.Label(top)
        self.statusLbl.place(relx=0.142, rely=0.933, height=21, width=600)
        self.statusLbl.configure(text='''Welcome...''', textvariable=self.statusStrVar, anchor='w')

    def inputFile(self):
        vac_support.browseInput(self)

    def outputDir(self):
        vac_support.browseOutput(self)

    def run(self):
        vac_support.runFunction(self)

    def aboutUs(self):
        vac_support.aboutUs(self)          

    def objectWindow(self, event):
        vac_support.showObjectWindow(self)

if __name__ == '__main__':
    vp_start_gui()





