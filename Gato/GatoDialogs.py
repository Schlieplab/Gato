################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/~gato
#
#	file:   GatoDialogs.py
#	author: Alexander Schliep (schliep@zpr.uni-koeln.de)
#
#       Parts of the source from this file has been taken from
#       the Python Tkinter demos.
#
#       This file has version $Revision$ from $Date$. Last change by
#       $Author$.
#
################################################################################
from Tkinter import *
from ScrolledText import *
import tkSimpleDialog 
import sys
import os

class AboutBox(tkSimpleDialog.Dialog):
 
    def buttonbox(self):
	# Stolen from tkSimpleDialog.py
        # add standard button box. override if you don't want the
        # standard buttons
        box = Frame(self)
        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=RIGHT, padx=5, pady=5)
        self.bind("<Return>", self.ok)
        box.pack(side=BOTTOM,fill=X)

   
    def body(self, master):
	self.resizable(0,0)
	self.catIconImage = PhotoImage(file=sys.path[0] + "/catbox-splash.gif")
	self.catIcon = Label(master, image=self.catIconImage)
	self.catIcon.pack(side=TOP)
 	color = self.config("bg")[4]
	self.infoText = ScrolledText(master, relief=FLAT, 
				     padx=3, pady=3,
				     background=color, 
				     #foreground="black",
				     wrap='word',
				     width=60, height=12,
				     font="Times 10")
	self.infoText.pack(expand=0, fill=X)
	self.infoText.delete('0.0', END)
	inputFile=open(sys.path[0] +"/GPL.txt", 'r')
       	text = inputFile.read()
	inputFile.close()
	self.infoText.insert('0.0', text)	
	self.infoText.configure(state=DISABLED)
	self.title("Gato - About")


class SplashScreen(Toplevel):
    """ Provides a splash screen. Usage:
    
        Subclass and override 'CreateWidgets()'

	In constructor of main window/application call
	
        - S = SplashScreen(main=self)        (if caller is Toplevel) 
        - S = SplashScreen(main=self.master) (if caller is Frame) 

        - S.Destroy()  after you are done creating your widgets etc.

    """

    def __init__(self, master=None):
	Toplevel.__init__(self, master, relief=RAISED, borderwidth=5)
	self.main = master
	if self.main.master != None:
	    self.main.master.withdraw()
	self.main.withdraw()
	self.overrideredirect(1)
	self.CreateWidgets()
	self.after_idle(self.CenterOnScreen)
	self.update()

    def CenterOnScreen(self):
	self.update_idletasks()
	xmax = self.winfo_screenwidth()
	ymax = self.winfo_screenheight()
	x0 = (xmax - self.winfo_reqwidth()) / 2
	y0 = (ymax - self.winfo_reqheight()) / 2
	self.geometry("+%d+%d" % (x0, y0))
    
    def CreateWidgets(self):
	self.catIcon = PhotoImage(file=sys.path[0] + "/catbox-splash.gif")
	self.label = Label(self, image=self.catIcon)
	self.label.pack(side=TOP)
		
    def Destroy(self):
	self.main.update()
	self.main.deiconify()
	self.withdraw()


