#!/usr/bin/env python2.2
################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/~gato
#
#	file:   Gato3D.py
#	author: Alexander Schliep (schliep@zpr.uni-koeln.de)
#
#       Copyright (C) 1998-2002, Alexander Schliep, Winfried Hochstaettler and 
#       ZAIK/ZPR, Universitaet zu Koeln
#                                   
#       Contact: schliep@zpr.uni-koeln.de, wh@zpr.uni-koeln.de             
#
#       Information: http://gato.sf.net
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
#
#
#       This file is version $Revision$ 
#                       from $Date$
#             last change by $Author$.
#
################################################################################
import sys
import traceback
import os
import bdb
import whrandom
import re 
import string
import StringIO
import tokenize
import tkFont

from Tkinter import *
from tkFileDialog import askopenfilename, asksaveasfilename
from tkMessageBox import askokcancel, showerror, askyesno
from ScrolledText import ScrolledText
from GatoConfiguration import GatoConfiguration
from Graph import Graph
from GraphUtil import *
from GraphDisplay3D import GraphDisplay3DToplevel
from GraphDisplay import GraphDisplayToplevel
from GatoUtil import *
from GatoGlobals import *
from GatoDialogs import AboutBox, SplashScreen, HTMLViewer
import GatoIcons

# put someplace else
def WMExtrasGeometry(window):
    """ Returns (top,else) where
        - top is the amount of extra pixels the WM puts on top
          of the window
        - else is the amount of extra pixels the WM puts everywhere
          else around the window 

        NOTE: Does not work with tk8.0 style menus, since those are
              handled by WM (according to Tk8.1 docs) """
    g = string.split(window.geometry(),"+") 
    trueRootx = string.atoi(g[1]) 
    trueRooty = string.atoi(g[2])
    
    rootx = window.winfo_rootx() # top left of our window
    rooty = window.winfo_rooty() # *WITHOUT* WM extras
    topWMExtra = abs(rooty - trueRooty) # WM adds that on top
    WMExtra    = abs(rootx - trueRootx) # and that on all other sides
    return (topWMExtra,WMExtra)

################################################################################
#
#
# Public Methods of class AlgoWin
#
# ShowActive(lineNo)           Display line lineNo as activated 
#
# ShowBreakpoint(lineNo)       Show breakpoint at line lineNo
#
# HideBreakpoint(lineNo)       Hide breakpoint at line lineNo
#
# WaitNextEvent()              Wait for some GUI event
#
# WaitTime(delay)              Wait for delay (in ms)
#


class AlgoWin(Frame):
    """ Provide GUI with main menubar for displaying and controlling
        algorithms and the algorithm text widget """

    def __init__(self, parent=None):
	Frame.__init__(self,parent)
	Splash = SplashScreen(self.master)

	self.algoFont = "Courier"
	self.algoFontSize = 10

	self.keywordsList = [
	    "del", "from", "lambda", "return",
	    "and", "elif", "global", "not", "try",
	    "break", "else", "if", "or", "while",
	    "class", "except", "import", "pass",
	    "continue", "finally", "in", "print",
	    "def", "for", "is", "raise"]

	GatoIcons.Init()
	self.config = GatoConfiguration(self)

	# Create widgets
	self.pack()
	self.pack(expand=1,fill=BOTH) # Makes menuBar and toolBar sizeable
	self.makeMenuBar()
	self.makeAlgoTextWidget()
	self.makeToolBar()
	self.master.title("Gato _VERSION_ - Algorithm")
	self.master.iconname("Gato _VERSION_")

	self.algorithm = Algorithm()
	self.algorithm.SetGUI(self) # So that algorithm can call us
	self.graphDisplay = GraphDisplay3DToplevel()
	self.secondaryGraphDisplay = None
	self.AboutAlgorithmDialog = None
	self.AboutGraphDialog = None

	self.lastActiveLine = 0

	self.algorithmIsRunning = 0    # state
	self.commandAfterStop = None   # command to call after forced Stop

	self.goOn = IntVar()           # lock variable to avoid busy idling

	self.master.protocol('WM_DELETE_WINDOW',self.Quit) # Handle WM Kills
	Splash.Destroy()
	# Fix focus and stacking
	if os.name == 'nt' or os.name == 'dos':
	    self.graphDisplay.tkraise()
	    self.master.tkraise()
	    self.master.focus_force()
	else:
	    self.tkraise()

	# Make AlgoWins requested size its minimal size to keep
	# toolbar from vanishing when changing window size
	# Packer has been running due to splash screen
	#wmExtras = WMExtrasGeometry(self.graphDisplay)
	#if os.name == 'nt' or os.name == 'dos':
	#    self.master.minsize(self.master.winfo_reqwidth(),
	#			self.master.winfo_reqheight() +
	#			wmExtras[1])
	#else: # Unix & Mac 
	#    self.master.minsize(self.master.winfo_reqwidth(),
	#			self.master.winfo_reqheight() +
	#			wmExtras[0] + wmExtras[1])
	self.BindKeys(self.master)
	#self.BindKeys(self.graphDisplay)

	self.SetFromConfig() # Set values read in config

    ############################################################
    #
    # Create GUI
    #   	
    def makeMenuBar(self):
	""" *Internal* Now using Tk 8.0 style menues """
        self.menubar = Menu(self, tearoff=0)
	
	# Add file menu
	self.fileMenu = Menu(self.menubar, tearoff=0)
	self.fileMenu.add_command(label='Open Algorithm...',	
				  command=self.OpenAlgorithm)
	self.fileMenu.add_command(label='Open Graph...',	
				  command=self.OpenGraph)
	self.fileMenu.add_command(label='Reload Algorithm & Graph',	
				  command=self.ReloadAlgorithmGraph)
	self.fileMenu.add_command(label='Export Graph as EPS...',	
				  command=self.ExportEPSF)
	self.fileMenu.add_separator()
	self.fileMenu.add_command(label='Preferences...',	
				  command=self.Preferences)
	self.fileMenu.add_separator()
	self.fileMenu.add_command(label='Quit',		
				  command=self.Quit)
	self.menubar.add_cascade(label="File", menu=self.fileMenu, 
				 underline=0)	
	# Add window menu
	self.windowMenu=Menu(self.menubar, tearoff=0)
	self.windowMenu.add_command(label='One graph window',	
				    command=self.OneGraphWindow)
	self.windowMenu.add_command(label='Two graph windows',	
				    command=self.TwoGraphWindow)
	self.menubar.add_cascade(label="Window Layout", menu=self.windowMenu, 
				 underline=0)

	# On a Mac we put our about box under the Apple menu ... 
	if os.name == 'mac':
	    self.apple=Menu(self.menubar, tearoff=0, name='apple')
	    self.apple.add_command(label='About Gato',	
				   command=self.AboutBox)
	    self.apple.add_command(label='Help',	
				   command=self.HelpBox)
	    self.apple.add_separator()
	    self.apple.add_command(label='About Algorithm',	
				   command=self.AboutAlgorithm)
	    self.apple.add_command(label='About Graph',	
				   command=self.AboutGraph)
	    self.menubar.add_cascade(menu=self.apple)
	else: # ... on other systems we add a help menu 
	    self.helpMenu=Menu(self.menubar, tearoff=0, name='help')
	    self.helpMenu.add_command(label='About Gato',	
				      command=self.AboutBox)
	    self.helpMenu.add_command(label='Help',	
				   command=self.HelpBox)
	    self.helpMenu.add_separator()
	    self.helpMenu.add_command(label='About Algorithm',	
				      command=self.AboutAlgorithm)
	    self.helpMenu.add_command(label='About Graph',	
				      command=self.AboutGraph)
	    self.menubar.add_cascade(label="Help", menu=self.helpMenu, 
				     underline=0)

	self.master.configure(menu=self.menubar)


    def makeToolBar(self):
	""" *Internal* Creates Start/Stop/COntinue ... toolbar """
	toolbar = Frame(self, cursor='hand2', relief=FLAT)
	toolbar.pack(side=BOTTOM, fill=X) # Allows horizontal growth
	toolbar.columnconfigure(5,weight=1)

	if os.name == 'nt' or os.name == 'dos':
	    px = 0 
	    py = 0 
	else:  # Unix
	    px = 0 
	    py = 3 

	self.buttonStart    = Button(toolbar, width=8, padx=px, pady=py, 
				     text='Start', command=self.CmdStart)
	self.buttonStep     = Button(toolbar, width=8, padx=px, pady=py, 
				     text='Step', command=self.CmdStep)
	self.buttonTrace    = Button(toolbar, width=8, padx=px, pady=py, 
				     text='Trace', command=self.CmdTrace)
	self.buttonContinue = Button(toolbar, width=8, padx=px, pady=py, 
				     text='Continue', command=self.CmdContinue)
	self.buttonStop     = Button(toolbar, width=8, padx=px, pady=py, 
				     text='Stop', command=self.CmdStop)

	self.buttonStart.grid(row=0, column=0, padx=2, pady=2)
	self.buttonStep.grid(row=0, column=1, padx=2, pady=2)
	self.buttonTrace.grid(row=0, column=2, padx=2, pady=2)
	self.buttonContinue.grid(row=0, column=3, padx=2, pady=2)
	self.buttonStop.grid(row=0, column=4, padx=2, pady=2)
	
	self.buttonStart['state']    = DISABLED
	self.buttonStep['state']     = DISABLED
	self.buttonTrace['state']    = DISABLED
	self.buttonContinue['state'] = DISABLED
	self.buttonStop['state']     = DISABLED	


    def makeAlgoTextWidget(self):
	""" *Internal* Here we also define appearance of 
	    - interactive lines 
	    - breakpoints 
	    - the active line """
	borderFrame = Frame(self, relief=SUNKEN, bd=2) # Extra Frame
	# around widget needed for more Windows-like appearance
	self.algoText = ScrolledText(borderFrame, relief=FLAT, 
				     padx=3, pady=3,
				     background="white", wrap='none',
				     width=15, height=30,
				     )
	self.SetAlgorithmFont(self.algoFont, self.algoFontSize)
	self.algoText.pack(expand=1, fill=BOTH)
	borderFrame.pack(side=TOP, expand=1, fill=BOTH)

	# GUI-related tags
	self.algoText.tag_config('Interactive', foreground='#009900',background="#E5E5E5")
	self.algoText.tag_config('Break',       foreground='#ff0000',background="#E5E5E5")
	self.algoText.tag_config('Active',      background='#bbbbff')

	self.algoText.bind("<ButtonRelease-1>", self.handleMouse)
	self.algoText['state'] = DISABLED  


    def SetAlgorithmFont(self, font, size):
	self.algoFont = font
	self.algoFontSize = size

	f = tkFont.Font(self, (font, size, tkFont.NORMAL))
	bf = tkFont.Font(self, (font, size, tkFont.BOLD))
	itf = tkFont.Font(self, (font, size, tkFont.ITALIC))

	self.algoText.config(font=f)
	# syntax highlighting tags
	self.algoText.tag_config('keyword', font=bf)
	self.algoText.tag_config('string', font=itf)
	self.algoText.tag_config('comment', font=itf)
	self.algoText.tag_config('identifier', font=bf)

    def SetFromConfig(self):
	c = self.config.get
	self.SetAlgorithmFont(c('algofont'), int(c('algofontsize')))
	self.algoText.config(fg=c('algofg'), bg=c('algobg'))
	self.algoText.tag_config('Interactive', 
				 foreground=c('interactivefg'),
				 background=c('interactivebg'))
 	self.algoText.tag_config('Break', 
 				 foreground=c('breakpointfg'),
 				 background=c('breakpointbg'))
 	self.algoText.tag_config('Active', 
 				 foreground=c('activefg'),
 				 background=c('activebg'))
	globals()['gBlinkRate'] = int(c('blinkrate'))
	globals()['gBlinkRepeat'] = int(c('blinkrepeat'))

	
    def OpenSecondaryGraphDisplay(self):
	""" Pops up a second graph window """
	if self.secondaryGraphDisplay == None:
	    self.secondaryGraphDisplay = GraphDisplayToplevel()
	    self.BindKeys(self.secondaryGraphDisplay)
	else:
	    self.secondaryGraphDisplay.Show()


    def WithdrawSecondaryGraphDisplay(self):
	""" Hide window containing second graph """
	if self.secondaryGraphDisplay != None:
	    self.secondaryGraphDisplay.Withdraw()


    ############################################################
    #
    # GUI Helpers
    #   	
	
    # Lock  
    def touchLock(self):
	""" *Internal* The lock (self.goOn) is a variable which
	    is used to control the flow of the programm and to 
	    allow GUI interactions without busy idling.

	    The following methods wait for the lock to be touched:
	    
	    - WaitNextEvent 
	    - WaitTime 

	    The following methods touch it:

	    - CmdStop
	    - CmdStep
	    - CmdContinue """
	self.goOn.set(self.goOn.get() + 1) #XXX possible overflow


    def activateMenu(self):
	""" Make the menu active (i.e., after stopping an algo) """
	self.menubar.entryconfigure(0, state = NORMAL)


    def deactivateMenu(self):
	""" Make the menu inactive (i.e., before running an algo) """
	self.menubar.entryconfigure(0, state = DISABLED) 


    def tagLine(self, lineNo, tag):
	""" Add tag 'tag' to line lineNo """
       	self.algoText.tag_add(tag,'%d.0' % lineNo,'%d.0' % (lineNo + 1))


    def unTagLine(self, lineNo, tag):
	""" Remove tag 'tag' from line lineNo """
	self.algoText.tag_remove(tag,'%d.0' % lineNo,'%d.0' % (lineNo + 1))


    def tagLines(self, lines, tag):
	""" Tag every line in list lines with specified tag """
	for l in lines:
	    self.tagLine(l, tag)

    def tokenEater(self, type, token, (srow, scol), (erow, ecol), line):
	#print "%d,%d-%d,%d:\t%s\t%s" % \
	#     (srow, scol, erow, ecol, type, repr(token))

	if type == 1:    # Name 
	    if token in self.keywordsList:
		self.algoText.tag_add('keyword','%d.%d' % (srow, scol),
				      '%d.%d' % (erow, ecol))
	elif type == 3:  # String
	    self.algoText.tag_add('string','%d.%d' % (srow, scol),
				  '%d.%d' % (erow, ecol))
	elif type == 39: # Comment
	    self.algoText.tag_add('comment','%d.%d' % (srow, scol),
				  '%d.%d' % (erow, ecol))


    ############################################################
    #
    # Menu Commands
    #
    # The menu commands are passed as call back parameters to 
    # the menu items.
    #
    def OpenAlgorithm(self,file=""):
	""" GUI to allow selection of algorithm to open 
            file parameter for testing purposes """
	if self.algorithmIsRunning:
	    self.CmdStop()
	    self.commandAfterStop = self.OpenAlgorithm
	    return

	if file == "": # caller did not specify file
	    file = askopenfilename(title="Open Algorithm",
				   defaultextension=".py",
				   filetypes = ( ("Gato Algorithm", ".alg"),
						 ("Python Code", ".py"))

				   )
	if file is not "": 
	    try:
		self.algorithm.Open(file)
	    except (EOFError, IOError):
		self.HandleFileIOError("Algorithm",file)
		return 

	    self.algoText['state'] = NORMAL 
	    self.algoText.delete('0.0', END)
	    self.algoText.insert('0.0', self.algorithm.GetSource())
	    self.algoText['state'] = DISABLED 

	    self.tagLines(self.algorithm.GetInteractiveLines(), 'Interactive')
	    self.tagLines(self.algorithm.GetBreakpointLines(), 'Break')

	    # Syntax highlighting
	    tokenize.tokenize(StringIO.StringIO(self.algorithm.GetSource()).readline, 
			      self.tokenEater)


	    if self.algorithm.ReadyToStart():
		self.buttonStart['state'] = NORMAL 
	    self.master.title("Gato _VERSION_- " + stripPath(file))

	    if self.AboutAlgorithmDialog:
		self.AboutAlgorithmDialog.Update(self.algorithm.About(),"About Algorithm")



    def OpenGraph(self,file=""):
	""" GUI to allow selection of graph to open 
            file parameter for testing purposes """
	if self.algorithmIsRunning:
	    self.CmdStop()
	    self.commandAfterStop = self.OpenGraph
	    return

  	if file == "": # caller did not specify file 
	    file = askopenfilename(title="Open Graph",
				   defaultextension=".cat",
				   filetypes = ( ("Gato", ".cat"),
						 #("Gato Plus", ".cat"),
						 #("LEDA", ".gph"),
						 ("Graphlet", ".let")
						 )
				   )
	    
	if file is not "":
	    try:
		self.algorithm.OpenGraph(file)
	    except (EOFError, IOError):
		self.HandleFileIOError("Graph",file)
		return 
		
	    if self.algorithm.ReadyToStart():
		self.buttonStart['state'] = NORMAL 
	    if self.AboutGraphDialog:
		self.AboutGraphDialog.Update(self.graphDisplay.About(), "About Graph")


    def ReloadAlgorithmGraph(self):
	if self.algorithmIsRunning:
	    self.CmdStop()
	    self.commandAfterStop = self.ReloadAlgorithmGraph
	    return
	
	if self.algorithm.algoFileName is not "":
	    self.OpenAlgorithm(self.algorithm.algoFileName)
	if self.algorithm.graphFileName is not "":
	    self.OpenGraph(self.algorithm.graphFileName)


    def Preferences(self):
	""" Handle editing preferences """
	self.config.edit()


    def ExportEPSF(self):
	""" GUI to control export of EPSF file  """
	file = asksaveasfilename(title="Export EPSF",
				 defaultextension=".eps",
				 filetypes = ( ("Encapsulated PS", ".eps"),
					       ("Postscript", ".ps")
					       ))
	if file is not "": 
	    self.graphDisplay.PrintToPSFile(file)


    def Quit(self):
	if self.algorithmIsRunning:
	    self.CmdStop()
	    self.commandAfterStop = self.Quit
	    return

	if askokcancel("Quit","Do you really want to quit?"):
	    Frame.quit(self)


    def OneGraphWindow(self):
	""" Align windows nicely for one graph window """
	self.WithdrawSecondaryGraphDisplay()
	self.master.update()
	
	if os.name == 'mac':
	    screenTop = 19 # Take care of menubar
	else:
	    screenTop = 0

	# Keep the AlgoWin fixed in size but move it to 0,0  
	(topWMExtra,WMExtra) = WMExtrasGeometry(self.graphDisplay)
	pad = 1 # Some optional extra space
	trueWidth  = self.master.winfo_width() + 2 * WMExtra + pad

	# Move AlgoWin so that the WM extras will be at 0,0 
	# Silly enough one hast to specify the true coordinate at which
        # the window will appear
	self.master.geometry("+%d+%d" % (pad, screenTop + pad)) 

	# XXX-DEBUG-XXX
	print "OneGraphWindow: screen= (%d * %d), extras = (%d %d)" % (
	    self.master.winfo_screenwidth(),
	    self.master.winfo_screenheight(),
	    WMExtra,
	    topWMExtra)

	# Move graph win to take up the rest of the screen
	screenwidth  = self.master.winfo_screenwidth()
	screenheight = self.master.winfo_screenheight() - screenTop
	self.graphDisplay.geometry("%dx%d+%d+%d" % (
	    screenwidth - trueWidth - 2 * WMExtra - pad - 1,# see 1 below  
	    screenheight - WMExtra - topWMExtra - pad, 
	    trueWidth + 1 + pad, 	    
	    screenTop + pad))
	self.graphDisplay.update()
	self.master.update()
	
	
    def TwoGraphWindow(self):
	""" Align windows nicely for two graph windows """
	self.OpenSecondaryGraphDisplay()
	self.master.update()

	if os.name == 'mac':
	    screenTop = 19 # Take care of menubar
	else:
	    screenTop = 0

	# Keep the AlgoWin fixed in size but move it to 0,0  
	(topWMExtra,WMExtra) = WMExtrasGeometry(self.graphDisplay)
	pad = 1 # Some optional extra space
	trueWidth  = self.master.winfo_width() + 2 * WMExtra + pad

	# Move AlgoWin so that the WM extras will be at 0,0 
	# Silly enough one hast to specify the true coordinate at which
        # the window will appear
	self.master.geometry("+%d+%d" % (pad, screenTop + pad)) 

	# Move GraphWins so that the are stacked dividing vertical
        # space evenly and taking up as much as possible horizontally
	screenwidth  = self.master.winfo_screenwidth()
	screenheight = self.master.winfo_screenheight() - screenTop

	reqGDWidth = screenwidth - trueWidth - 2 * WMExtra - pad - 1
	reqGDHeight = screenheight/2 - WMExtra - topWMExtra - pad

	self.graphDisplay.geometry("%dx%d+%d+%d" % (
	    reqGDWidth,
	    reqGDHeight, 
	    trueWidth + 1 + pad, 	    
	    screenTop + pad))

	self.secondaryGraphDisplay.geometry("%dx%d+%d+%d" % (
	    reqGDWidth,
	    reqGDHeight, 
	    trueWidth + 1 + pad, 	    
	    screenTop + reqGDHeight + WMExtra + topWMExtra + 2 * pad))
			   
	self.master.update()

    def AboutBox(self):
	d = AboutBox(self.master)

    def HelpBox(self):
	d = HTMLViewer(gGatoHelp, "Help", self.master)

    def AboutAlgorithm(self):
	d = HTMLViewer(self.algorithm.About(), "About Algorithm", self.master)
	self.AboutAlgorithmDialog = d

    def AboutGraph(self):
	d = HTMLViewer(self.graphDisplay.About(), "About Graph", self.master)
	self.AboutGraphDialog = d

    ############################################################
    #
    # Tool bar Commands
    #
    # The tool bar commands are passed as call back parameters to 
    # the tool bar buttons.
    #
    def CmdStart(self):
	""" Command linked to toolbar 'Start' """
	# self.deactivateMenu()
	self.buttonStart['state']    = DISABLED 
	self.buttonStep['state']     = NORMAL 
	self.buttonTrace['state']    = NORMAL
	self.buttonContinue['state'] = NORMAL
	self.buttonStop['state']     = NORMAL
	self.algorithmIsRunning = 1
	self.algorithm.Start()

	
    def CmdStop(self):
	""" Command linked to toolbar 'Stop' """
	self.algorithm.Stop()
	self.clickResult = ('abort',None) # for aborting interactive
	# selection of vertices/edges
	self.touchLock()


    def CommitStop(self):
	""" Commit a stop for the GUI """
	self.buttonStart['state']    = NORMAL
	self.buttonStep['state']     = DISABLED
	self.buttonTrace['state']    = DISABLED
	self.buttonContinue['state'] = DISABLED
	self.buttonStop['state']     = DISABLED

	# Un-activate last line 
	if self.lastActiveLine != 0:
	    self.unTagLine(self.lastActiveLine,'Active')
	self.update() # Forcing redraw
	self.algorithmIsRunning = 0
	if self.commandAfterStop != None:
	    self.commandAfterStop()
	    self.commandAfterStop = None
	# self.activateMenu()
	

    def CmdStep(self):
	""" Command linked to toolbar 'Step' """
	self.algorithm.Step()
	self.clickResult = ('auto',None) # for stepping over interactive
	# selection of vertices/edges
	self.touchLock()


    def CmdContinue(self):
	""" Command linked to toolbar 'Continue' """
	# Should we disable continue buton here ?
	self.algorithm.Continue()
	self.clickResult = ('auto',None) # for stepping over interactive
	# selection of vertices/edges
	self.touchLock()


    def CmdTrace(self):
	""" Command linked to toolbar 'Trace' """
	self.algorithm.Trace()
	self.touchLock()


    ############################################################
    #
    # Key commands for Tool bar Commands
    #

    def BindKeys(self, widget):
        # self.master.bind_all screws up EPSF save dialog
	widget.bind('s', self.KeyStart)
	widget.bind('x', self.KeyStop)
	widget.bind('<space>', self.KeyStep)
	widget.bind('c', self.KeyContinue)
	widget.bind('t', self.KeyTrace)
	widget.bind('b', self.KeyBreak)

  
    def KeyStart(self, event):
	""" Command linked to toolbar 'Start' """
	if self.buttonStart['state'] != DISABLED:
	    self.CmdStart()

    def KeyStop(self, event):
	if self.buttonStop['state'] != DISABLED:
	    self.CmdStop()

    def KeyStep(self, event):
	""" Command linked to toolbar 'Step' """
	if self.buttonStep['state'] != DISABLED:
	    self.CmdStep()
	else:
	    self.KeyStart(event)

    def KeyContinue(self, event):
	""" Command linked to toolbar 'Continue' """
	if self.buttonContinue['state'] != DISABLED:
	    self.CmdContinue()

    def KeyTrace(self, event):
	""" Command linked to toolbar 'Trace' """
	if self.buttonTrace['state'] != DISABLED:
	    self.CmdTrace() 

    def KeyBreak(self, event):
	""" Command for toggling breakpoints """
	self.algorithm.ToggleBreakpoint()


    ############################################################
    #
    # Mouse Commands
    #		
    
    #
    # handleMouse 
    def handleMouse(self, event):
	""" Callback for canvas to allow toggeling of breakpoints """
	currLine  = string.splitfields(self.algoText.index(CURRENT),'.')[0]
       	self.algorithm.ToggleBreakpoint(string.atoi(currLine))


    ############################################################
    #
    # Public methods (for callbacks from algorithm)
    #
    def ShowActive(self, lineNo):
	""" Show  lineNo as active line """
	if self.lastActiveLine != 0:
	    self.unTagLine(self.lastActiveLine,'Active')
	self.lastActiveLine = lineNo
	self.tagLine(lineNo,'Active')	
	self.algoText.yview_pickplace('%d.0' % lineNo)
	self.update() # Forcing redraw
    

    def ShowBreakpoint(self, lineNo):
	""" Show  lineNo as breakpoint """
	self.tagLine(lineNo,'Break')	


    def HideBreakpoint(self, lineNo):
	""" Show lineNo w/o breakpoint """
	self.unTagLine(lineNo,'Break')	


    def WaitNextEvent(self):
	""" Stop Execution until user does something. This avoids
	    busy idling. See touchLock() """
       	self.wait_variable(self.goOn)


    def WaitTime(self, delay):
	""" Stop Execution until delay is passed. This avoids
	    busy idling. See touchLock() """
	self.after(delay,self.touchLock)
       	self.wait_variable(self.goOn)

    def ClickHandler(self,type,t):
	""" *Internal* Callback for GraphDisplay """ 
	self.clickResult = (type,t)
	self.touchLock()
	    		
    def PickInteractive(self, type, filterChoice=None):
	""" Pick a vertex or an edge (specified by 'type') interactively 

            GUI blocks until
            - a fitting object is clicked 
            - the algorithm is stopped
            - 'Step' is clicked which will randomly select a vertex or an 
              edge

	    filterChoice is an optional method (only argument: the vertex or edge).
            It returns true if the choice is acceptable 
 
            NOTE: To avoid fatal blocks randomly selected objects are not 
                  subjected to filterChoice
            """
	self.graphDisplay.RegisterClickhandler(self.ClickHandler)
	self.graphDisplay.UpdateInfo("Select a " + type + 
				     " or click 'Step' or 'Continue' for random selection")
	self.clickResult = (None,None)
	goOn = 1
	while goOn == 1:
	    self.wait_variable(self.goOn)
	    if self.clickResult[0] == type:
		if filterChoice != None:
		    if filterChoice(self.clickResult[1]):
			goOn = 0
		else:
		    goOn = 0
	    if self.clickResult[0] in ['abort','auto']:
		goOn = 0
				
	self.graphDisplay.UnregisterClickhandler()
	
	self.graphDisplay.DefaultInfo()
	if self.clickResult[0] == 'auto':
	    return None
	else:
	    return self.clickResult[1]


    def HandleFileIOError(self, fileDescription, fileName):
	print fileDescription," file named: ",fileName, " produced an error"


# Endof: AlgoWin ---------------------------------------------------------------


class AlgorithmDebugger(bdb.Bdb):
    """*Internal* Bdb subclass to allow debugging of algorithms 
        REALLY UGLY CODE: Written before I understood the Debugger.
        Probably should use sys.settrace() directly with the different
        modes of debugging encoded in appropriate methods"""

    def __init__(self,dbgGUI):
	""" *Internal* dbgGUI is the GUI for the debugger """
	self.GUI = dbgGUI
	bdb.Bdb.__init__(self)
	self.doTrace = 0
	self.lastLine = -1

    def dispatch_line(self, frame):
	""" *Internal* Only dispatch if we are in the algorithm file """
	fn = frame.f_code.co_filename
	if fn != self.GUI.algoFileName:
	    return None
        line = self.currentLine(frame)
	if line == self.lastLine:
	    return self.trace_dispatch	    
	self.lastLine = line
	self.user_line(frame)
	if self.quitting: 
	    raise bdb.BdbQuit
	return self.trace_dispatch
    
    def dispatch_call(self, frame, arg):
	fn = frame.f_code.co_filename
        line = self.currentLine(frame)
	doTrace = self.doTrace # value of self.doTrace might change
	# No tracing of functions defined outside of our algorithmfile 
	if fn != self.GUI.algoFileName:
	    return None
	#import inspect
	#print "dispatch_call",fn, line, frame, self.stop_here(frame), self.break_anywhere(frame), self.break_here(frame)
	#print inspect.getframeinfo(frame)
	frame.f_locals['__args__'] = arg
	if self.botframe is None:
	    # First call of dispatch since reset()
	    self.botframe = frame
	    return self.trace_dispatch

	#if self.stop_here(frame) or self.break_anywhere(frame):
        #    return self.trace_dispatch

	self.user_call(frame, arg)
	if self.quitting: raise bdb.BdbQuit
	if doTrace == 1:
	    self.doTrace = 0
	    return self.trace_dispatch
	if self.break_anywhere(frame):
	    self.doTrace = 0
	    return self.trace_nofeedback_dispatch	    
	return None

    def trace_nofeedback_dispatch(self, frame, event, arg):
        if self.quitting:
            return # None
        if event == 'line':
	    line = self.currentLine(frame)
	    if line in self.GUI.breakpoints:
                self.GUI.mode = 2
                return self.dispatch_line(frame)
            else:
                return None
        if event == 'call':
            return self.dispatch_call(frame, arg)
        if event == 'return':
            return self.dispatch_return(frame, arg)
        if event == 'exception':
            return self.dispatch_exception(frame, arg)
        print 'bdb.Bdb.dispatch: unknown debugging event:', `event`

    def reset(self):
	""" *Internal* Put debugger into initial state, calls forget() """
	bdb.Bdb.reset(self)
	self.forget()

 
    def forget(self):
	self.lineno = None
	self.stack = []
	self.curindex = 0
	self.curframe = None

 
    def setup(self, f, t):
	#self.forget()
	self.stack, self.curindex = self.get_stack(f, t)
	self.curframe = self.stack[self.curindex][0]

    
    def user_call(self, frame, argument_list): 
	""" *Internal* This function is called when we stop or break
  	    at this line """
        line = self.currentLine(frame)
        # DEBUG print "*user_call*", line, argument_list
	if self.doTrace == 1:
	    line = self.currentLine(frame)
	    if line in self.GUI.breakpoints:
		self.GUI.mode = 2
	    self.GUI.GUI.ShowActive(line)
	    # TO Avoid multiple steps in def line of called fun
            #self.interaction(frame, None)	
	    self.doTrace = 0
	else:
	    pass

    def user_line(self, frame):
	""" *Internal* This function is called when we stop or break at this line  """
	self.doTrace = 0 # XXX
	line = self.currentLine(frame)
	# DEBUG print "*user_line*", line
	if line in self.GUI.breakpoints:
            self.GUI.mode = 2
	self.GUI.GUI.ShowActive(line)
	self.interaction(frame, None)

 
    def user_return(self, frame, return_value):
	""" *Internal* This function is called when a return trap is set here """
	frame.f_locals['__return__'] = return_value
	#print '--Return--'
	#self.doTrace = 0 #YYY
	# TO Avoid multiple steps in return line of called fun
	#self.interaction(frame, None)

 
    def user_exception(self, frame, (exc_type, exc_value, exc_traceback)):
	""" *Internal* This function is called if an exception occurs,
	    but only if we are to stop at or just below this level """ 
	frame.f_locals['__exception__'] = exc_type, exc_value
	if type(exc_type) == type(''):
	    exc_type_name = exc_type
	else: exc_type_name = exc_type.__name__
	#print exc_type_name + ':', repr.repr(exc_value)
	self.interaction(frame, exc_traceback)


    def interaction(self, frame, traceback):
	""" *Internal* This function does all the interaction with the user
	    depending on self.GUI.mode
	    
	    - Step (self.GUI.mode == 2)
	    - Quit (self.GUI.mode == 0)
	    - Auto-run w/timer (self.GUI.mode == 1)"""
 
	self.setup(frame, traceback)
	# 
	#line = self.currentLine(frame)
	if self.GUI.mode == 2:
	    old = self.GUI.mode
	    self.GUI.GUI.WaitNextEvent() # user event -- might change self.GUI.mode
	    #print "self.GUI.mode: ",old, "-> ",self.GUI.mode
	    #if self.GUI.mode == 2: 
	    #self.do_next()

	if self.GUI.mode == 0:
	    self.do_quit()
	    return # Changed

	if self.GUI.mode == 1:
	    self.GUI.GUI.WaitTime(10)   # timer event was 100
	    #self.do_next()
		
	self.forget()
 

    def do_next(self):
	self.set_next(self.curframe)

    def do_quit(self):
	self.set_quit()
	
    def currentLine(self, frame):
	""" *Internal* returns the current line number  """ 
# 	import linecache, string
# 	name = frame.f_code.co_name
# 	if not name: 
# 	    name = '???'
# 	fn = frame.f_code.co_filename
# 	line = linecache.getline(fn, frame.f_lineno)
# 	#print '+++', fn, frame.f_lineno, name, ':', string.strip(line)
	return frame.f_lineno 

# Endof: AlgorithmDebugger  ----------------------------------------------------

class Algorithm:
    """ Provides all services necessary to load an algorithm, run it
        and provide facilities for visualization """

    def __init__(self):
	self.DB = AlgorithmDebugger(self)
       	self.source = ""            # Source as a big string
       	self.interactive = []  
       	self.breakpoints = []       # Doesnt debugger take care of it ?
	self.algoFileName = ""
	self.graphFileName = ""
	self.mode = 0
	# mode = 0  Stop
	# mode = 1  Running
	# mode = 2  Stepping
	self.graph = None
	self.graphIsDirty = 0       # If graph was changed by running
	self.algoGlobals = {}       # Sandbox for Algorithm
	self.logAnimator = 0
	self.about = None

	self.commentPattern = re.compile('[ \t]*#')
	self.blankLinePattern = re.compile('[ \t]*\n')
	

    def SetGUI(self, itsGUI):
	""" Set the connection to its GUI """
	self.GUI = itsGUI


    def Open(self,file):
	""" Read in an algorithm from file. """
	self.ClearBreakpoints()
	self.algoFileName = file
	input=open(file, 'r')
       	self.source = input.read()
	input.close()
	 
	
	# Now read in the prolog as a module to get access to the following data
	# Maybe should obfuscate the names ala xxx_<bla>, have one dict ?
	try:
	    input = open(os.path.splitext(self.algoFileName)[0] + ".pro", 'r')
	    options = self.ReadPrologOptions(input)
	    input.close()
	except EOFError, IOError:
	    self.GUI.HandleFileIOError("Prolog",file)
	    return 	

	try:
	    self.breakpoints   = options['breakpoints']
	except:
	    self.breakpoints   = []
	try:
	    self.interactive   = options['interactive']
	except:
	    self.interactive   = []
	try:
	    self.graphDisplays = options['graphDisplays']
	except:
	    self.graphDisplays = None
	try:
	    self.about         = options['about']
	except:
	    self.about         = None


	if self.graphDisplays != None:
	    if self.graphDisplays == 1:
		self.GUI.WithdrawSecondaryGraphDisplay()


    def ReadPrologOptions(self, file):
	""" Prolog files should contain the following variables:
	    - breakpoints = [] a list of line numbers which are choosen as default
                               breakpoints
            - interactive = [] a list of line numbers which contain interactive commands
                               (e.g., PickVertex)
	    - graphDisplays = 1 | 2 the number of graphDisplays needed by the algorithm
            - about = \"\"\"<HTML-code>\"\"\" information about the algorithm

	"""
 	import re
	import sys

	text = file.read()
	options = {}
	optionPattern = {'breakpoints':'breakpoints[ \t]*=[ \t]*(\[[^\]]+\])',
			 'interactive':'interactive[ \t]*=[ \t]*(\[[^\]]+\])',
			 'graphDisplays':'graphDisplays[ \t]*=[ \t]*([1-2])'}
	# about is more complicated

	for patternName in optionPattern.keys():
	    compPattern = re.compile(optionPattern[patternName])
	    match = compPattern.search(text) 

	    #print patternName, match.group()

	    if match != None:
		options[patternName] = eval(match.group(1))	

	# Special case with about (XXX: assuming about = """ ... """)

	try:
	    aboutStartPat = re.compile('about[ \t]*=[ \t]*"""')
	    aboutEndPat   = re.compile('"""')
	    left = aboutStartPat.search(text).end() 
	    right = aboutEndPat.search(text, left).start()

	    options['about'] = text[left:right]
	except:
	    pass

	return options


    def About(self):
	""" Return a HTML-page giving information about the algorithm """
	if self.about != None:
	    return self.about
	else:
	    return "<HTML><BODY> <H3>No information available</H3></BODY></HTML>"

    def OpenGraph(self,file):
	""" Read in a graph from file and open the display """
	self.graphFileName = file
 	self.graph = OpenCATBoxGraph(file)
	self.GUI.graphDisplay.Show() # In case we are hidden
	self.GUI.graphDisplay.ShowGraph(self.graph, stripPath(file))
	self.GUI.graphDisplay.RegisterGraphInformer(WeightedGraphInformer(self.graph))
	self.graphIsDirty = 0


    def OpenSecondaryGraph(self,G,title,informer=None):
	""" Read in graph from file and open the the second display """
	self.GUI.OpenSecondaryGraphDisplay()
	self.GUI.secondaryGraphDisplay.ShowGraph(G, title)
	if informer != None:
	    self.GUI.secondaryGraphDisplay.RegisterGraphInformer(informer)
	    

    def ReadyToStart(self):
	""" Return 1 if we are ready to run. That is when we user
            has opened both an algorithm and a graph.  """
	if self.graphFileName != "" and self.algoFileName != "":
	    return 1
	else:
	    return 0

    def Start(self):
	""" Start an loaded algorithm. It firsts execs the prolog and
	    then starts the algorithm in the debugger. The algorithms
            globals (i.e., the top-level locals are in a dict we supply
            and for which we preload the packages we want to make available)"""
	if self.graphIsDirty == 1:
	    self.OpenGraph(self.graphFileName) # Does show 
	else:
	    self.GUI.graphDisplay.Show() # In case we are hidden
	self.graphIsDirty = 1
	self.mode = 1

	# Set global vars ...
	self.algoGlobals = {}
	self.algoGlobals['self'] = self
	self.algoGlobals['G'] = self.graph

	if self.logAnimator:
	    self.algoGlobals['A'] = MethodLogger(self.GUI.graphDisplay)
	else:
	    self.algoGlobals['A'] = self.GUI.graphDisplay
	# XXX
	# explictely loading packages we want to make available to the algorithm
	modules = ['DataStructures', 
		   'AnimatedDataStructures', 
		   'AnimatedAlgorithms',
		   'GraphUtil',
		   'GatoUtil']

	for m in modules:
	    exec("from %s import *" % m, self.algoGlobals, self.algoGlobals)

	# transfer required globals
	self.algoGlobals['gInteractive'] = globals()['gInteractive']
	
	# Read in prolog and execute it
	try:
	    execfile(os.path.splitext(self.algoFileName)[0] + ".pro", 
		     self.algoGlobals, self.algoGlobals)
	except:
	    print "*** Bug in", os.path.splitext(self.algoFileName)[0] + ".pro"
	    traceback.print_exc()

	# Read in algo and execute it in the debugger
	file = self.algoFileName

	# Switch on all shown breakpoints
	for line in self.breakpoints:
	    self.DB.set_break(self.algoFileName,line)

	try:
	    command = "execfile(\"" +file +"\")"
	    self.DB.run(command, self.algoGlobals, self.algoGlobals)
	except:
	    # Do somethin useful here
	    print "OOOppps bug in", self.algoFileName
	    traceback.print_exc()
	self.GUI.CommitStop()

    def Stop(self):
	self.mode = 0

    def Step(self):
	self.DB.doTrace = 0
	self.mode = 2 
    
    def Continue(self):
	self.DB.doTrace = 0
	self.mode = 1

    def Trace(self):
	self.mode = 2 
	self.DB.doTrace = 1

    def ClearBreakpoints(self):
	""" Clear all breakpoints """
	for line in self.breakpoints:
	    self.GUI.HideBreakpoint(line)
	    self.DB.clear_break(self.algoFileName,line)
	self.breakpoints = []

    def SetBreakpoints(self, list):
	""" SetBreakpoints is depreciated 
            NOTE: Use 'breakpoint' var in prolog instead. 

            Set all breakpoints in list: So an algorithm prolog
            can set a bunch of pre-assigned breakpoints at once """
        print "SetBreakpoints() is depreciated. Use 'breakpoint' var in prolog instead. "
	for line in list:
	    self.GUI.ShowBreakpoint(line)
	    self.breakpoints.append(line)
	    self.DB.set_break(self.algoFileName,line)
	    

    def ToggleBreakpoint(self,line = None):
	""" If we have a breakpoint on line, delete it, else add it. 
            If no line is passed we ask the DB for it"""

        if line == None:
	    line = self.DB.lastLine

	if line in self.breakpoints:
	    self.GUI.HideBreakpoint(line)
	    self.breakpoints.remove(line)
	    self.DB.clear_break(self.algoFileName,line)
	else: # New Breakpoint

	    # check for not breaking in comments nor on empty lines. 
	    import linecache
	    codeline = linecache.getline(self.algoFileName,line)
	    if codeline != '' and self.commentPattern.match(codeline) == None and self.blankLinePattern.match(codeline) == None:
		self.GUI.ShowBreakpoint(line)
		self.breakpoints.append(line)
		self.DB.set_break(self.algoFileName,line)

	    
    def GetInteractiveLines(self):
	""" Return lines on which user interaction (e.g., choosing a 
	    vertex occurrs. """
	return self.interactive
	
    def GetBreakpointLines(self):
	""" Return lines on which user interaction (e.g., choosing a 
	    vertex occurrs. """
	return self.breakpoints
	
    def GetSource(self):
	""" Return the algorithms source """  
	return self.source
 
    def NeededProperties(self, propertyValueDict):
	""" Check that graph has that value for each property
            specified in the dictionary 'propertyValueDict' 

            If check fails algorithm is stopped 

            Proper names for properties are defined in gProperty """
        for property in propertyValueDict.keys():
	    value = self.graph.Property(property)
	    if value != propertyValueDict[property]:
		r = askokcancel("Gato - Error", 
				"The algorithm you started requires that the graph " +
				"it works on has certain properties. The graph does " + 
				"not have the correct value " +
				"for the property '" + property + "'.\n" +
				"Do you still want to proceed ?")
		if not r:
		    self.GUI.CmdStop()

    def PickVertex(self, default=None, filter=None, visual=None):
	""" Pick a vertex interactively. 

	    - default: specifies the vertex returned when user does not
              want to select one. If default==None, a random
              vertex not subject to filter will be returned

            - filter: a function which should return a non-None value
              if the passed vertex is acceptable

            - visual is a function which takes the vertex as its 
              only argument and cause e.g. some visual feedback """
        v = None

	#print "pickVertex ",globals()['gInteractive']
        if globals()['gInteractive'] == 1:
	    v = self.GUI.PickInteractive('vertex', filter)

	if v == None:
	    if default == None:
		v = whrandom.choice(self.graph.vertices)
	    else:
		v = default
 	if visual is not None:
	    visual(v)
 	return v
	
    def PickEdge(self, default=None, filter=None, visual=None):
	""" Pick an edge interactively  
	    - default: specifies the edge returned when user does not
              want to select one. If default==None, a random
              edge not subject to filter will be returned

            - filter: a function which should return a non-None value
              if the passed edge is acceptable

            - visual is a function which takes the edge as its 
              only argument and cause e.g. some visual feedback """ 
        e = None

        if globals()['gInteractive'] == 1:
	    e = self.GUI.PickInteractive('edge', filter)

	if e == None:
	    if default == None:
		e = whrandom.choice(self.graph.Edges())
	    else:
		e = default

	if visual is not None:
	    visual(e)
  	return e


################################################################################
if __name__ == '__main__':
    #root = Tk()
    #print sys.path
    #import sys
    #print sys.path

    if (len(sys.argv) == 1 or  len(sys.argv) == 3):

	app = AlgoWin()    
	#======================================================================
	#
	# Gato.py <algorithm> <graph>
	#
	if (len(sys.argv) == 3):
	    algorithm = sys.argv[1]
	    graph = sys.argv[2]

	    app.OpenAlgorithm(algorithm)
	    app.update_idletasks()
	    app.update()
	    app.OpenGraph(graph)
	    app.update_idletasks()
	    app.update()
	    app.after_idle(app.CmdContinue) # after idle needed since CmdStart
	    app.CmdStart()
	    app.update_idletasks()

	app.mainloop()
    else:
	print "Usage: gato algorithm.alg graph.cat"

