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
import GatoUtil
import GatoGlobals
import GatoIcons
import tkSimpleDialog 
import sys
import os
import htmllib, formatter


# Should be in GatoGlobals 
crnotice1 = "Copyright (C) 1998-2002, ZAIK/ZPR, Universität zu Köln\n"\
	    "Gato version _VERSION_ from _BUILDDATE_"
crnotice2 = "Written by Alexander Schliep (schliep@zpr.uni-koeln.de).\n" \
 	    "Application Design: Alexander Schliep and \n" \
	    "Winfried Hochstaettler. Additional developers: Torsten\n" \
	    "Pattberg, Ramazan Buzdemir and Achim Gaedke.\n\n" \
            "For Information see http://www.zpr.uni-koeln.de/~gato\n" \
 	    "Gato comes with ABSOLUTELY NO WARRANTY.\n" \
            "This is free software, and you are welcome to redistribute\n" \
            "it under certain conditions. For details see 'LGPL.txt'.\n"


class AboutBox(tkSimpleDialog.Dialog):
    """ The application's about box """
 
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
	self.catIconImage = PhotoImage(data=GatoIcons.gato) # statt file=
	self.catIcon = Label(master, image=self.catIconImage)
	self.catIcon.pack(side=TOP)
	label = Label(master, text=crnotice1)
	label.pack(side=TOP)
	label = Label(master, font="Helvetica 10", text=crnotice2, justify=CENTER)
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
	self.infoText.insert('0.0', GatoGlobals.gLGPLText)	
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
	self.catIconImage = PhotoImage(data=GatoIcons.gato) # statt file=
	self.label = Label(self, image=self.catIconImage)
	self.label.pack(side=TOP)
	self.label = Label(self, text=crnotice1)
	self.label.pack(side=TOP)
	label = Label(self, font="Helvetica 10", text=crnotice2, justify=CENTER)
	label.pack(side=TOP)

		
    def Destroy(self):
	self.main.update()
	self.main.deiconify()
	self.withdraw()

class HTMLWriter(formatter.DumbWriter):
    
    def __init__(self, textWidget, viewer):
	formatter.DumbWriter.__init__(self, self)
	self.textWidget = textWidget
	self.viewer = viewer
	self.indent = ""

    def write(self, data):
	self.textWidget.insert( 'insert', data)

    def new_margin(self, margin, level):
	self.indent = '\t' * level

    def send_label_data(self, data):
	self.write(self.indent + data + ' ')


class MyHTMLParser(htmllib.HTMLParser):
    """ Basic parser with image support added. output is supposed to be
        the textwidget for output """

    def __init__(self, formatter, output):
	htmllib.HTMLParser.__init__(self, formatter)
	self.output = output

    def handle_image(self, source, alt, ismap, align, width, height):
	imageCache = GatoUtil.ImageCache() # ImageCache is a singleton
	self.output.image_create('insert', image=imageCache[source], align='baseline') 


class HTMLViewer(Toplevel):
    """ Basic class which provides a scrollable area for viewing HTML
        text and a Dismiss button """
    
    def __init__(self, htmlcode, title, master=None):

	Toplevel.__init__(self, master)
	#self.protocol('WM_DELETE_WINDOW',self.withdraw)
	self.titleprefix = title
	color = self.config("bg")[4]
	borderFrame = Frame(self, relief=SUNKEN, bd=2) # Extra Frame
	self.text = ScrolledText(borderFrame, relief=FLAT, 
				 padx=3, pady=3,
				 #background='white', 
				 background=color, 
				 #foreground="black",
				 wrap='word',
				 width=60, height=12,
				 font="Times 10")
	self.text.pack(expand=1, fill=BOTH)
	#self.text.insert('0.0', text)
	self.text['state'] = DISABLED 
	borderFrame.pack(side=TOP,expand=1,fill=BOTH)
        box = Frame(self)
        w = Button(box, text="Dismiss", width=10, command=self.withdraw, default=ACTIVE)
        w.pack(side=RIGHT, padx=5, pady=5)
        self.bind("<Return>", self.withdraw)
        box.pack(side=BOTTOM,fill=BOTH)
	self.insert(htmlcode)


    def Update(self,htmlcode, title):
	self.titleprefix = title
	self.insert(htmlcode)

    def insert(self, htmlcode):
	self.text['state'] = NORMAL
	self.text.delete('0.0', END)

	writer = HTMLWriter(self.text, self)
	format = formatter.AbstractFormatter(writer)
	#parser = htmllib.HTMLParser(format)
	parser = MyHTMLParser(format, self.text)

	parser.feed(htmlcode)
	parser.close()
	
	self.text['state'] = DISABLED 
	if parser.title != None:
	    self.title(self.titleprefix + " - " + parser.title)
	else:
	    self.title(self.titleprefix)

#---------------------------------- test code -----------------------------------
about = """<HTML>
<HEAD>
<TITLE>Breadth-First-Search</TITLE>
</HEAD>
<BODY>

<H2>Description</H2>

This algorithm traverses a graph in breadth-first
order.
<P>

<H2>Visualisation</H2>

You see


<H4>Implementation</h4>
 
This was done by 

<pre>
asasdadasdasdaaasssssssssssssssssssssssssssssssssssssssssssssssss
</pre>
<tt>Blaeh</tt>
<a href="module-sgmllib.html">sgmllib</a><a name="l2h-1953"></a>. 
<P>
The following is a summary of the interface defined by
<tt class=class>sgmllib.SGMLParser</tt>:

<P>

<ol>
<LI>The interface

<LI>Its <b>implementation</b>

<LI>WHat not
</OL>



<UL>
<LI><img src="Icons/vertex.gif">The interface

<LI><img src="Icons/edge.gif">Its implementation

<LI>WHat not
</UL>
<img src="Icons/vertex.gif">
<img src="Icons/edge.gif">
<img src="Icons/delete.gif">
<dl>
<dt>x</dt> <dd>does wild things</dd>
<dt>y</dt> <dd>is even wilder</dd>
</dl>


</BODY></HTML>
"""
if __name__ == '__main__':
    
    win = HTMLViewer(about, "Dummy")
    import Tkinter
    Tkinter.Tk().mainloop()
