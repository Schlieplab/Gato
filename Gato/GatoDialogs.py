################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#       You can find more information at http://gato.sf.net
#
#	file:   GatoDialogs.py
#	author: Alexander Schliep (alexander@schlieplab.org)
#       Copyright (C) 2016-2020 Alexander Schliep and
#	Copyright (C) 1998-2015 Alexander Schliep, Winfried Hochstaettler and 
#       Copyright (C) 1998-2001 ZAIK/ZPR, Universitaet zu Koeln
#                                   
#       Contact: alexander@schlieplab.org             
#
#
#       This library is free software; you can redistribute it and/or
#       modify it under the terms of the GNU Library General Public
#       License as published by the Free Software Foundation; either
#       version 2 of the License, or (at your option) any later version.
#
#       This library is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#       Library General Public License for more details.
#
#       You should have received a copy of the GNU Library General Public
#       License along with this library; if not, write to the Free
#       Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#
#       This file is version $Revision$ 
#                       from $Date$
#             last change by $Author$.
#
################################################################################
from Tkinter import *
from Tkinter import _cnfmerge
from ScrolledText import *
import GatoUtil
import GatoGlobals
import GatoIcons
import tkSimpleDialog 
import sys
import os
import htmllib, formatter


# Should be in GatoGlobals 
crnotice1 = "Copyright (C) 2016-2020 Alexander Schliep.\n"\
            "Copyright (C) 1998-2015 Alexander Schliep\n"\
            "and Winfried Hochstaettler. Copyright (C)\n"\
            "1998-2001 ZPR, University of Cologne\n"\
            "Gato version %s from %s" % (GatoGlobals.gatoVersion,
                                         GatoGlobals.gatoBuildDate)

crnotice2 = "Written by Alexander Schliep (%s).\n" \
            "Application Design: Alexander Schliep and \n" \
            "Winfried Hochstaettler. Additional developers: Torsten\n" \
            "Pattberg, Ramazan Buzdemir, Achim Gaedke,\n" \
            "Scott Merkling, Janne Grunau and Wasinee Rungsarityotin.\n" \
            "Screen Design: Heidrun Krimmel.\n\n" \
            "For Information see %s\n" \
            "Gato comes with ABSOLUTELY NO WARRANTY.\n" \
            "This is free software, and you are welcome to redistribute\n" \
            "it under certain conditions. For details see 'LGPL.txt'.\n" %(GatoGlobals.gatoAuthorEmail,
                                                                           GatoGlobals.gatoURL)

class AutoScrollbar(Scrollbar):
    """ Code taken from a comp.lang.python posting by
        Fredrik Lundh.
        
        A scrollbar that hides itself if it's not needed.  Only
        works if you use the grid geometry manager.
    """
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        Scrollbar.set(self, lo, hi)
    def pack(self, **kw):
        raise TclError, "cannot use pack with this widget"
    def place(self, **kw):
        raise TclError, "cannot use place with this widget"


class AutoScrolledText(Text):
    """ Code taken from Tkinter's ScrolledText.py. 

        Modified to use a grid layout and AutoScrollbars
    """
    def __init__(self, master=None, cnf=None, **kw):
        if cnf is None:
            cnf = {}
        if kw:
            cnf = _cnfmerge((cnf, kw))
        fcnf = {}
        for k in cnf.keys():
            if type(k) == ClassType or k == 'name':
                fcnf[k] = cnf[k]
                del cnf[k]
        self.frame = Frame(master, **fcnf)
        self.vbar = AutoScrollbar(self.frame, name='vbar')
        self.vbar.grid(row=0, column=1, sticky=N+S)
        #self.vbar.pack(side=RIGHT, fill=Y)
        cnf['name'] = 'text'
        Text.__init__(self, self.frame, **cnf)        
        self.grid(row=0, column=0, sticky=N+S+E+W)
        #self.pack(side=LEFT, fill=BOTH, expand=1)
        self['yscrollcommand'] = self.vbar.set
        self.vbar['command'] = self.yview

        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)


        # Copy geometry methods of self.frame -- hack!
        methods = Pack.__dict__.keys()
        methods = methods + Grid.__dict__.keys()
        methods = methods + Place.__dict__.keys()

        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))



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
        # XXX Stupid hack. Now DumbWriter wordwraps at 9999999 columns  
        formatter.DumbWriter.__init__(self, self, 9999999)
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
        self.tag_start = {}
        
    def handle_image(self, source, alt, ismap, align, width, height):
        imageCache = GatoUtil.ImageCache() # ImageCache is a singleton
        self.output.image_create('insert', image=imageCache[source], align='baseline') 

    def do_colordef(self,attrs):
        colordef = Frame(self.output,width=40,height=18,background=attrs[0][1])
        self.output.window_create(INSERT, window=colordef)
        self.output.insert(INSERT, ' ')

    def start_h1(self,attrs):
        self.output.insert(INSERT,'\n\n')
        self.tag_start['h1'] = self.output.index(INSERT)

    def end_h1(self):
        self.output.tag_add('h1',self.tag_start['h1'],self.output.index(INSERT))
        self.output.insert(INSERT,'\n\n')

    def start_h2(self,attrs):
        self.output.insert(INSERT,'\n\n')
        self.tag_start['h2'] = self.output.index(INSERT)

    def end_h2(self):
        self.output.tag_add('h2',self.tag_start['h2'],self.output.index(INSERT))
        self.output.insert(INSERT,'\n\n')

    def start_h3(self,attrs):
        self.output.insert(INSERT,'\n\n')
        self.tag_start['h3'] = self.output.index(INSERT)

    def end_h3(self):
        self.output.tag_add('h3',self.tag_start['h3'],self.output.index(INSERT))
        self.output.insert(INSERT,'\n')

    def start_h4(self,attrs):
        self.output.insert(INSERT,'\n\n')
        self.tag_start['h4'] = self.output.index(INSERT)

    def end_h4(self):
        self.output.tag_add('h4',self.tag_start['h4'],self.output.index(INSERT))
        self.output.insert(INSERT,'\n')

    def start_h5(self,attrs):
        self.tag_start['h5'] = self.output.index(INSERT)

    def end_h5(self):
        self.output.tag_add('h5',self.tag_start['h5'],self.output.index(INSERT))
        self.output.insert(INSERT,'\n')

    def start_b(self,attr):
        self.tag_start['b'] = self.output.index(INSERT)

    def end_b(self):
        self.output.tag_add('b',self.tag_start['b'],self.output.index(INSERT))
            
    def start_em(self,attr):
        self.tag_start['em'] = self.output.index(INSERT)

    def end_em(self):
        self.output.tag_add('em',self.tag_start['em'],self.output.index(INSERT))
    
    def start_p(self,attr):
        self.output.insert(INSERT,'\n')

    def end_p(self):
        self.output.insert(INSERT,'\n\n')
        
    def start_pre(self,attr):
        self.tag_start['pre'] = self.output.index(INSERT)

    def end_pre(self):
        self.output.tag_add('pre',self.tag_start['pre'],self.output.index(INSERT))
        self.output.insert(INSERT,'\n\n')

    def start_tt(self,attr):
        self.tag_start['tt'] = self.output.index(INSERT)

    def end_tt(self):
        self.output.tag_add('tt',self.tag_start['tt'],self.output.index(INSERT))

        
        
class HTMLViewer(Toplevel):
    """ Basic class which provides a scrollable area for viewing HTML
        text and a Dismiss button """
    
    def __init__(self, htmlcode, title, master=None):
    
        Toplevel.__init__(self, master)
        self.protocol('WM_DELETE_WINDOW',self.withdraw)
        self.titleprefix = title
        color = self.config("bg")[4]
        borderFrame = Frame(self, relief=SUNKEN, bd=2) # Extra Frame
        self.text = ScrolledText(borderFrame, relief=FLAT, 
                                 padx=3, pady=3,
                                 background='white', 
                                 #background=color, 
                                 #foreground="black",
                                 wrap='word',
                                 width=60, height=20,
                                 spacing1=3,
                                 spacing2=2,
                                 spacing3=3)
        self.text.pack(expand=1, fill=BOTH)
        #self.text.insert('0.0', text)
        self.text['state'] = DISABLED 
        borderFrame.pack(side=TOP,expand=1,fill=BOTH)
        box = Frame(self)
        w = Button(box, text="Dismiss", width=10, command=self.doWithdraw, default=ACTIVE)
        w.pack(side=RIGHT, padx=5, pady=5)
        self.bind("<Return>", self.doWithdraw)
        box.pack(side=BOTTOM,fill=BOTH)
        self.setStyle()
        self.insert(htmlcode)

    def setStyle(self):
        baseSize = 14
        self.text.config(font="Times %d" % baseSize)
        
        self.text.tag_config('h1', font="Times %d bold" % (baseSize + 8))
        self.text.tag_config('h2', font="Times %d bold" % (baseSize + 6))
        self.text.tag_config('h3', font="Times %d bold" % (baseSize + 4))
        self.text.tag_config('h4', font="Times %d bold" % (baseSize + 2))
        self.text.tag_config('h5', font="Times %d bold" % (baseSize + 1))
        self.text.tag_config('b', font="Times %d bold" % baseSize)
        self.text.tag_config('em', font="Times %d italic" % baseSize)
        self.text.tag_config('pre', font="Courier %d" % baseSize)
        self.text.tag_config('tt', font="Courier %d" % baseSize)
       


    def doWithdraw(self, event=None):
        # Need to eat optional event so that we can use is in both button and bind callback
        self.withdraw()
        
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
        parser.nofill=False
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

<H1>Description 1</H1>

<H2>Description 2</H2>

<H3>Description 3</H3>

<H4>Description 4</H4>

<H5>Description 5</H5>

<P>This algorithm traverses a graph in breadth-first
order. </P>

<p>Visu We provide archive files which contain the CATBox algorithms and
graphs and one binary executable each for Gato and Gred. Since we
cannot rely on Python being available on Linux and Windows XP the
executables are rather large, since they contain their own Python
interpreter.  However, the installation is pretty much just one copy
and a double-click.
alisation</p>

<p>We provide archive files which contain the CATBox algorithms and
graphs and one binary executable each for Gato and Gred. Since we
cannot rely on Python being available on Linux and Windows XP the
executables are rather large, since they contain their own Python
interpreter.  However, the installation is pretty much just one copy
and a double-click.
alisation</p>


<colordef color="#ACDEFA">This color you will see</colordef>


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
<LI> <colordef color="red"> Processed Vertices

<LI> <colordef color="#ACDEFA"> Visited Vertices

<LI> <colordef color="grey"> Ignored Edges
</OL>

<Ul>
<LI> <colordef color="red"> Processed Vertices

<LI> <colordef color="#ACDEFA"> Visited Vertices

<LI> <colordef color="grey"> Ignored Edges
</UL>


<UL>
<LI><img src="Icons/vertex.gif">The interface

<LI><img src="Icons/edge.gif">Its implementation

<LI>WHat not
</UL>


<img src="Icons/vertex.gif">
<img src="Icons/edge.gif">
<img src="Icons/delete.gif">
<dl>
<dt>x</dt> <dd>does <b>wild</b> things</dd>
<dt>y</dt> <dd>is even wilder</dd>
</dl>


</BODY></HTML>
"""
if __name__ == '__main__':
    win = HTMLViewer(about, "Dummy")
    Tk().mainloop()
