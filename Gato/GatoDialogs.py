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
#       This file is version $Revision$ 
#                       from $Date$
#             last change by $Author$.
#
################################################################################
from Tkinter import *
from ScrolledText import *
from GatoUtil import gatoPath
import tkSimpleDialog 
import sys
import os

crnotice1 = "Copyright (C) 1998-1999, ZAIK/ZPR, Universität zu Köln\n"\
	    "Gato version _VERSION_ from _BUILDDATE_"
crnotice2 = "Written by Alexander Schliep (schliep@zpr.uni-koeln.de)\n" \
            "For Information see http://www.zpr.uni-koeln.de/~gato\n" \
 	    "Gato comes with ABSOLUTELY NO WARRANTY.\n" \
            "This is free software, and you are welcome to redistribute\n" \
            "it under certain conditions. For details see 'LGPL.txt'.\n"


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
	self.catIconImage = PhotoImage(file=os.path.join(gatoPath(), 'gato.gif'))
	self.catIcon = Label(master, image=self.catIconImage)
	self.catIcon.pack(side=TOP)
	label = Label(master, text=crnotice1)
	label.pack(side=TOP)
	label = Label(master, font="Helvetica 10", text=crnotice2, justify=LEFT)
	label.pack(side=TOP)
 	color = self.config("bg")[4]
	self.infoText = ScrolledText(master, relief=FLAT, 
				     padx=3, pady=3,
				     background=color, 
				     #foreground="black",
				     wrap='word',
				     width=60, height=12,
				     font="Times 10")
	self.infoText.pack(expand=0, fill=X, side=BOTTOM)
	self.infoText.delete('0.0', END)
	inputFile=open(os.path.join(gatoPath(), 'LGPL.txt'), 'r')
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
	self.catIcon = PhotoImage(file=os.path.join(gatoPath(), 'gato.gif'))
	self.label = Label(self, image=self.catIcon)
	self.label.pack(side=TOP)
	self.label = Label(self, text=crnotice1)
	self.label.pack(side=TOP)
	label = Label(self, font="Helvetica 10", text=crnotice2, justify=LEFT)
	label.pack(side=TOP)

		
    def Destroy(self):
	self.main.update()
	self.main.deiconify()
	self.withdraw()


class AboutAlgorithm(tkSimpleDialog.Dialog):
    
    def __init__(self, text, master=None):
	self.text = text
	tkSimpleDialog.Dialog.__init__(self, master)

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
	#self.resizable(0,0)
	#self.catIconImage = PhotoImage(file=os.path.join(gatoPath(), 'gato.gif'))
	#self.catIcon = Label(master, image=self.catIconImage)
	#self.catIcon.pack(side=TOP)
	#label = Label(master, text=crnotice1)
	#label.pack(side=TOP)
	#label = Label(master, font="Helvetica 10", text=crnotice2, justify=LEFT)
	#label.pack(side=TOP)
 	color = self.config("bg")[4]
	self.infoText = ScrolledText(master, relief=FLAT, 
				     padx=3, pady=3,
				     background=color, 
				     #foreground="black",
				     wrap='word',
				     width=60, height=12,
				     font="Times 10")
	self.infoText.pack(expand=0, fill=BOTH, side=BOTTOM)
	self.infoText.delete('0.0', END)
	self.infoText.insert('0.0', self.text)	
	self.infoText.configure(state=DISABLED)
	self.title("About Algorithm")
