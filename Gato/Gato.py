#!/usr/bin/env python2.6
################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#	file:   Gato.py
#	author: Alexander Schliep (alexander@schliep.org)
#
#       Copyright (C) 1998-2013, Alexander Schliep, Winfried Hochstaettler and 
#       Copyright 1998-2001 ZAIK/ZPR, Universitaet zu Koeln
#                                   
#       Contact: alexander@schliep.org, winfried.hochstaettler@fernuni-hagen.de
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
import tempfile
import traceback
import os
import bdb
import random
import re 
import string
import StringIO
import tokenize
import tkFont
import copy
import webbrowser
import getopt

import Gred

from Tkinter import *
from tkFileDialog import askopenfilename, asksaveasfilename
from tkMessageBox import askokcancel, showerror, askyesno
#from ScrolledText import ScrolledText
from GatoConfiguration import GatoConfiguration
import Graph #from Graph import Graph
from GraphUtil import *
from GraphDisplay import GraphDisplayToplevel, GraphDisplayFrame
from GatoUtil import *
import GatoGlobals
from GatoDialogs import AboutBox, SplashScreen, HTMLViewer, AutoScrolledText
import GatoIcons
# Only needed for Trial-Solution version. 
#import GatoSystemConfiguration
from AnimationHistory import AnimationHistory, AnimationCommand

# Workaround for bug in py2exe which mangles linecache on Windows
# On Windows put a copy of linecache.py included in your Python's 
# standard lib into the same directory as Gato.py and name it
# linecacheCopy
# Same problem exists with py2app on Mac, only py2app is smarter
# in sabotaging linecache
try:
    import linecacheCopy as linecache
except:
    import linecache



g = GatoGlobals.AnimationParameters


class AbortProlog(Exception):
    """Phony exception to about execution of prolog."""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

# put someplace else
def parsegeometry(geometry):
    m = re.match("(\d+)x(\d+)([-+]\d+)([-+]\d+)", geometry)
    if not m:
        raise ValueError("failed to parse geometry string")
    return map(int, m.groups())

def WMExtrasGeometry(window):
    """ Returns (top,else) where
        - top is the amount of extra pixels the WM puts on top
          of the window
        - else is the amount of extra pixels the WM puts everywhere
          else around the window 
    
        NOTE: Does not work with tk8.0 style menus, since those are
              handled by WM (according to Tk8.1 docs)
    
        NOTE: Some window managers return bad geometry definition
              Handle in caller
              """
    try:
        window.geometry() # XXX Sometimes first produced wrong results ...
        g = string.split(window.geometry(),"+")
    except TclError:
        # bad geometry specifier: e.g. ... "-1949x260+1871+1"
        return (32,32) 
    trueRootx = string.atoi(g[1]) 
    trueRooty = string.atoi(g[2])
    
    rootx = window.winfo_rootx() # top left of our window
    rooty = window.winfo_rooty() # *WITHOUT* WM extras
    topWMExtra = abs(rooty - trueRooty) # WM adds that on top
    WMExtra    = abs(rootx - trueRootx) # and that on all other sides
    
    # XXX KLUDGE topWMExtra,WMExtra should always be in 0...32 pixels, or?
    topWMExtra = min(32,topWMExtra)
    WMExtra = min(32, WMExtra)
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
    
    def __init__(self, parent=None, graph_panes=None, paned=False, experimental=False):
        self.graph_panes = graph_panes
        self.experimental = experimental
        if parent:
            parent.report_callback_exception = self.ReportCallbackException
        Frame.__init__(self,parent)

        #XXX import tkoptions
        #tkoptions.tkoptions(self)

        Splash = SplashScreen(self.master)
        # Need to change things a bit for Tk running on MacOS X
        # using the native drawing environment (TkAqua)
        self.windowingsystem = self.tk.call("tk", "windowingsystem")

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
        # Only needed for Trial-Solution version. 
        #self.gatoInstaller=GatoSystemConfiguration.GatoInstaller()
        
        # Create widgets
        self.pack()
        self.pack(expand=1,fill=BOTH) # Makes menuBar and toolBar sizeable
        self.makeMenuBar()
        self.makeAlgoTextWidget()
        self.makeToolBar()
        self.master.title("Gato %s - Algorithm" % GatoGlobals.gatoVersion)
        self.master.iconname("Gato %s" % GatoGlobals.gatoVersion)
        
        self.algorithm = Algorithm()
        self.algorithm.SetGUI(self) # So that algorithm can call us

        if self.graph_panes:
            self.graphDisplay = GraphDisplayFrame(self.graph_panes)
        else:
            self.graphDisplay = GraphDisplayToplevel()
        
        self.secondaryGraphDisplay = None
        self.AboutAlgorithmDialog = None
        self.AboutGraphDialog = None
        
        self.lastActiveLine = 0
        self.codeLineHistory = []

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

        if self.graph_panes is None:
            # Make AlgoWins requested size its minimal size to keep
            # toolbar from vanishing when changing window size
            # Packer has been running due to splash screen
            wmExtras = WMExtrasGeometry(self.graphDisplay)
            width = self.master.winfo_reqwidth()
            height = self.master.winfo_reqheight()

            # XXX Some WM + packer combinatios ocassionally produce absurd requested sizes
            #log.debug(os.name + str(wmExtras) + " width = %f height = %f " % (width, height))
            width = min(600, self.master.winfo_reqwidth())
            height = min(750, self.master.winfo_reqheight())
            if os.name == 'nt' or os.name == 'dos':
                self.master.minsize(width, height + wmExtras[1])
            else: # Unix & Mac 
                self.master.minsize(width, height + wmExtras[0] + wmExtras[1])
            
        self.BindKeys(self.master)
        self.BindKeys(self.graphDisplay)
        
        self.SetFromConfig() # Set values read in config
        
    ############################################################
    #
    # Create GUI
    #   	
    def makeMenuBar(self):
        """ *Internal* """
        self.menubar = Menu(self, tearoff=0)

        # Cross-plattform accelerators
        if self.windowingsystem == "aqua":
            accMod = "command"
        else:
            accMod = "Ctrl"
        
        # --- FILE menu ----------------------------------------
        self.fileMenu = Menu(self.menubar, tearoff=0)
        self.fileMenu.add_command(label='Open Algorithm...',	
                                  command=self.OpenAlgorithm)
        self.fileMenu.add_command(label='Open Graph...',	
                                  command=self.OpenGraph)
        # On the Mac starting gred from Gato will not create a seperate process
        # It is just one app where the menu bar switches based on which window has focus
        if self.windowingsystem != 'aqua':
            self.fileMenu.add_command(label='New Graph...',	
                                  command=self.NewGraph)
        # Only used for TRIAL-SOLUTION Gato version. Might be reused for easy
        # web-deployment
        #self.fileMenu.add_command(label='Open GatoFile...',
        #			  command=self.OpenGatoFile)
        #self.fileMenu.add_command(label='Save GatoFile...',
        #			  command=self.SaveGatoFile)
        self.fileMenu.add_command(label='Reload Algorithm & Graph',	
                                  command=self.ReloadAlgorithmGraph)
        self.fileMenu.add_command(label='Export Graph as EPS...',	
                                  command=self.ExportEPSF)

        if self.experimental:
            self.fileMenu.add_command(label='Export Graph as SVG...',	
                                      command=self.ExportSVG)
            self.fileMenu.add_command(label='Export Animation as SVG...',	
                                      command=self.ExportSVGAnimation)
        if self.windowingsystem != 'aqua':
            self.fileMenu.add_separator()
            self.fileMenu.add_command(label='Preferences...',
                                      command=self.Preferences,
                                      accelerator='%s-,' % accMod)
            #self.gatoInstaller.addMenuEntry(self.fileMenu)
            self.fileMenu.add_separator()
            self.fileMenu.add_command(label='Quit',		
                                      command=self.Quit,
                                      accelerator='%s-Q' % accMod)
        self.menubar.add_cascade(label="File", menu=self.fileMenu, 
                                 underline=0)	
        # --- WINDOW menu ----------------------------------------
        self.windowMenu=Menu(self.menubar, tearoff=0)
        self.windowMenu.add_command(label='One graph window',	
                                    accelerator='%s-1' % accMod,
                                    command=self.OneGraphWindow)
        self.windowMenu.add_command(label='Two graph windows',	
                                    accelerator='%s-2' % accMod,
                                    command=self.TwoGraphWindow)
        self.menubar.add_cascade(label="Window Layout", menu=self.windowMenu, 
                                 underline=0)
        
        
        # --- HELP menu ----------------------------------------
        self.helpMenu=Menu(self.menubar, tearoff=0, name='help')
        
        if self.windowingsystem != 'aqua':
            self.helpMenu.add_command(label='About Gato',
                                      command=self.AboutBox)
                                      
        self.helpMenu.add_command(label='Help',
                                  accelerator='%s-?' % accMod,
                                  command=self.HelpBox)        
        self.helpMenu.add_separator()
        self.helpMenu.add_command(label='Go to Gato website',
                                  command=self.GoToGatoWebsite)
        self.helpMenu.add_command(label='Go to CATBox website',
                                  command=self.GoToCATBoxWebsite)       
        self.helpMenu.add_separator()
        self.helpMenu.add_command(label='About Algorithm',	
                                  command=self.AboutAlgorithm)
        self.helpMenu.add_command(label='About Graph',	
                                  command=self.AboutGraph)
        self.menubar.add_cascade(label="Help", menu=self.helpMenu, 
                                 underline=0)


        # --- MacOS X application menu --------------------------
        # On a Mac we put our about box under the Apple menu ... 
        if self.windowingsystem == 'aqua':
            self.apple=Menu(self.menubar, tearoff=0, name='apple')
            self.apple.add_command(label='About Gato',	
                                   command=self.AboutBox)
            self.apple.add_separator()
            self.apple.add_command(label='Preferences...',
                                   accelerator='command-,',
                                   command=self.Preferences)
            self.menubar.add_cascade(menu=self.apple)

            
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

        if self.windowingsystem == 'aqua':
            bWidth = 7
        else:
            bWidth = 8
            
        self.buttonStart    = Button(toolbar, width=bWidth, padx=px, pady=py, 
                                     text='Start', command=self.CmdStart,
                                     highlightbackground='#DDDDDD')
        self.buttonStep     = Button(toolbar, width=bWidth, padx=px, pady=py, 
                                     text='Step', command=self.CmdStep,
                                     highlightbackground='#DDDDDD')
        self.buttonTrace    = Button(toolbar, width=bWidth, padx=px, pady=py, 
                                     text='Trace', command=self.CmdTrace,
                                     highlightbackground='#DDDDDD')
        if self.windowingsystem == 'aqua':
            text = 'Cont.'
        else:
             text = 'Continue'           
        self.buttonContinue = Button(toolbar, width=bWidth, padx=px, pady=py, 
                                     text=text, command=self.CmdContinue,
                                     highlightbackground='#DDDDDD')
        self.buttonStop     = Button(toolbar, width=bWidth, padx=px, pady=py, 
                                     text='Stop', command=self.CmdStop,
                                     highlightbackground='#DDDDDD')
        
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

        if self.windowingsystem == 'aqua':
            dummy = Frame(toolbar, relief=FLAT, bd=2)
            dummy.grid(row=0, column=5, padx=6, pady=2)
        
    def makeAlgoTextWidget(self):
        """ *Internal* Here we also define appearance of 
            - interactive lines 
            - breakpoints 
            - the active line """
        if self.windowingsystem == 'aqua':
            borderFrame = Frame(self, relief=FLAT, bd=1, background='#666666') # Extra Frame
        else:
            borderFrame = Frame(self, relief=SUNKEN, bd=2) # Extra Frame            
            # around widget needed for more Windows-like appearance

        if self.graph_panes:
            w, h = 1,1
        else:
            w, h = 43, 30
            
        self.algoText = AutoScrolledText(borderFrame, relief=FLAT, 
                                         padx=3, pady=3,
                                         background="white", wrap='none',
                                         width=w, height=h
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
        c = self.config.get # Shortcut to accessor
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
        g.BlinkRate = int(c('blinkrate'))
        g.BlinkRepeat = int(c('blinkrepeat'))
        
        
    def OpenSecondaryGraphDisplay(self):
        """ Pops up a second graph window or pane"""
        if self.secondaryGraphDisplay is None:
            if self.graph_panes:
                # We only get here during startup as show/hide is handled by
                # moving the sash
                self.secondaryGraphDisplay = GraphDisplayFrame(self.graph_panes)
            else:
                self.secondaryGraphDisplay = GraphDisplayToplevel()
            self.BindKeys(self.secondaryGraphDisplay)
            # Provide undo and logging of animations if required
            if self.algorithm.logAnimator == 1:
                self.secondaryGraphDisplay = AnimationHistory(self.secondaryGraphDisplay, displayNum=2)
            elif self.algorithm.logAnimator == 2:
                self.secondaryGraphDisplay = AnimationHistory(self.secondaryGraphDisplay,
                                                          'disp2\t', displayNum=2)
                #self.secondaryGraphDisplay.auto_print = 1
        else:
            if self.graph_panes:
                self.setSash(0.5)
            else:
                self.secondaryGraphDisplay.Show()

    def setSash(self, proportion):
        x,dummy = self.graph_panes.sash_coord(0)
        win_height = parsegeometry(self.master.geometry())[1]
        self.graph_panes.sash_place(0, x, int(win_height * proportion))        
            
    def WithdrawSecondaryGraphDisplay(self):
        """ Hide window containing second graph """
        if self.secondaryGraphDisplay is not None:
            if self.graph_panes:
                self.setSash(1.0)
            else:
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
        #log.debug("%d,%d-%d,%d:\t%s\t%s" % \
        #     (srow, scol, erow, ecol, type, repr(token)))
    
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
            # Windows screws up order 
            if self.windowingsystem == "win32":
                ft = [("Gato Algorithm", ".alg")]
            else:
                ft = [("Gato Algorithm", ".alg")
                      ,("Python Code", ".py")
                      ]
            file = askopenfilename(title="Open Algorithm",
                                   defaultextension=".py",
                                   filetypes = ft)
        if file is not "" and file is not ():
            try:
                self.algorithm.Open(file)
            except (EOFError, IOError), (errno, strerror):
                self.HandleFileIOError("Algorithm",file,errno,strerror)
                return 

            self.codeLineHistory = []
               
            self.algoText['state'] = NORMAL 
            self.algoText.delete('0.0', END)
            self.algoText.insert('0.0', self.algorithm.GetSource())
            self.algoText['state'] = DISABLED 
            
            self.tagLines(self.algorithm.GetInteractiveLines(), 'Interactive')
            self.tagLines(self.algorithm.GetBreakpointLines(), 'Break')
            
            # Syntax highlighting
            tokenize.tokenize(StringIO.StringIO(self.algorithm.GetSource()).readline, self.tokenEater)
            
            if self.algorithm.ReadyToStart():
                self.buttonStart['state'] = NORMAL 
            else:
                self.buttonStart['state'] = DISABLED                
            self.master.title("Gato %s - %s" % (GatoGlobals.gatoVersion, stripPath(file)))
            
            if self.AboutAlgorithmDialog:
                self.AboutAlgorithmDialog.Update(self.algorithm.About(),"About Algorithm")
                
    def NewGraph(self):
        Gred.Start()
        
    def OpenGraph(self,file=""):
        """ GUI to allow selection of graph to open 
            file parameter for testing purposes """
        if self.algorithmIsRunning:
            self.CmdStop()
            self.commandAfterStop = self.OpenGraph
            return
            
        if file == "": # caller did not specify file 
            file = askopenfilename(title="Open Graph",
                                   defaultextension=".gato",
                                   filetypes = [  ("Gred", ".cat")
                                                 #,("Gato Plus", ".cat")
                                                 #,("LEDA", ".gph")
                                                 #,("Graphlet", ".let")
                                                 #,("Gato",".gato")
                                               ]
                                   )
            
        if file is not "" and file is not ():
            try:
                self.algorithm.OpenGraph(file)
            except (EOFError, IOError),(errno, strerror):
                self.HandleFileIOError("Graph",file,errno, strerror)
                return 
                
            if self.algorithm.ReadyToStart():
                self.buttonStart['state'] = NORMAL 
            if self.AboutGraphDialog:
                self.AboutGraphDialog.Update(
                    self.graphDisplay.About(stripPath(self.algorithm.graphFileName)),
                    "About Graph")
                
    def SaveGatoFile(self,filename=""):
        """
        under Construction...
        """
        import GatoFile
        
        # ToDo
        if not askyesno("Ooops...",
                        "...this feature is under developement.\nDo you want to proceed?"):
            return
            
        if self.algorithmIsRunning:
            # variable file is lost here!
            self.CmdStop()
            self.commandAfterStop = self.SaveGatoFile
            return
            
        if filename == "": # caller did not specify file 
            filename = asksaveasfilename(title="Save Graph and Algorithm",
                                         defaultextension=".gato",
                                         filetypes = [  ("Gato",".gato")
                                                       #,("xml",".xml")
                                                     ]
                                         )
            
            
    def OpenGatoFile(self,filename=""):
        """
        menu command
        """
        
        import GatoFile
        
        if self.algorithmIsRunning:
            # variable file is lost here!
            self.CmdStop()
            self.commandAfterStop = self.OpenGatoFile
            return
            
        if filename == "": # caller did not specify file 
            filename = askopenfilename(title="Open Graph and Algorithm",
                                       defaultextension=".gato",
                                         filetypes = [  ("Gato",".gato")
                                                       #,("xml",".xml")
                                                     ]
                                       )
            
        if filename is not "":
            select={}
            try:
                # open xml file
                f=GatoFile.GatoFile(filename)
                select=f.getDefaultSelection()
                
                if not select:
                    # select the graph
                    select=f.displaySelectionDialog(self)
                    
            except GatoFile.FileException, e:
                self.HandleFileIOError("GatoFile: %s"%e.reason,filename)
                return
                
                # nothing selected
            if select is None:
                return
                
                # a graph is selected
            if select.get("graph"):
                try:
                    # open graph
                    graphStream=select["graph"].getGraphAsStringIO()
                    self.algorithm.OpenGraph(graphStream,
                                             fileName="%s::%s"%(filename,
                                                                select["graph"].getName()))
                except (EOFError, IOError),(errno, strerror):
                    self.HandleFileIOError("Gato",filename,errno,strerror)
                    return
                    
                if self.algorithm.ReadyToStart():
                    self.buttonStart['state'] = NORMAL 
                if self.AboutGraphDialog:
                    self.AboutGraphDialog.Update(
                        self.graphDisplay.About(stripPath(self.algorithm.graphFileName)),
                        "About Graph")
            # great shit! create files to get old gato running
            if select.get("algorithm"):
                xmlAlgorithm=select.get("algorithm")
                # save last algorithm tmp_name
                lastAlgoFileName=None
                if hasattr(self,"tmpAlgoFileName"):
                    lastAlgoFileName=self.tmpAlgoFileName
                lastAlgoDispalyName=None
                if hasattr(self,"algoDisplayFileName"):
                    lastAlgoDispalyName=self.algoDisplayFileName
                    # provide a temporary files for algortihm and prologue
                tmpFileName=tempfile.mktemp()
                self.tmpAlgoFileName="%s.alg"%tmpFileName
                self.algoDisplayFileName="%s::%s"%(filename,xmlAlgorithm.getName())
                tmp=file(self.tmpAlgoFileName,"w")
                tmp.write(xmlAlgorithm.getText())
                tmp.close()
                proFileName="%s.pro"%tmpFileName
                tmp=file(proFileName,"w")
                tmp.write(xmlAlgorithm.getProlog())
                tmp.close()
                # open it!
                # text copied from AlgoWin.OpenAlgorithm
                try:
                    self.algorithm.Open(self.tmpAlgoFileName)
                except (EOFError, IOError),(errno, strerror):
                    os.remove(self.tmpAlgoFileName)
                    os.remove(proFileName)
                    self.HandleFileIOError("Algorithm",self.tmpAlgoFileName,errno, strerror)
                    self.algoDisplayFileName=lastAlgoDispalyName
                    self.tmpAlgoFileName=lastAlgoFileName
                    return
                    
                    # handle old tempfile
                if lastAlgoFileName:
                    os.remove(lastAlgoFileName)
                    os.remove(lastAlgoFileName[:-3]+'pro')
                    
                    # prepare algorithm text widget
                self.algoText['state'] = NORMAL 
                self.algoText.delete('0.0', END)
                self.algoText.insert('0.0', self.algorithm.GetSource())
                self.algoText['state'] = DISABLED
                self.tagLines(self.algorithm.GetInteractiveLines(), 'Interactive')
                self.tagLines(self.algorithm.GetBreakpointLines(), 'Break')
                # Syntax highlighting
                tokenize.tokenize(StringIO.StringIO(self.algorithm.GetSource()).readline, 
                                  self.tokenEater)
                
                # set the state
                if self.algorithm.ReadyToStart():
                    self.buttonStart['state'] = NORMAL
                self.master.title("Gato %s - %s" % (GatoGlobals.gatoVersion,
                                                    stripPath(self.algoDisplayFileName)))
                
                if self.AboutAlgorithmDialog:
                    # to do ... alright for xml about ?!
                    self.AboutAlgorithmDialog.Update(self.algorithm.About(),
                                                     "About Algorithm")
                    
    def CleanUp(self):
        """
        removes the temporary files...
        """
        if hasattr(self,"tmpAlgoFileName") and self.tmpAlgoFileName:
            os.remove(self.tmpAlgoFileName)
            os.remove(self.tmpAlgoFileName[:-3]+'pro')
            
    def ReloadAlgorithmGraph(self):
        if self.algorithmIsRunning:
            self.CmdStop()
            self.commandAfterStop = self.ReloadAlgorithmGraph
            return
            
        if self.algorithm.algoFileName is not "":
            self.OpenAlgorithm(self.algorithm.algoFileName)
        if self.algorithm.graphFileName is not "":
            self.OpenGraph(self.algorithm.graphFileName)
            
            
    def Preferences(self,event=None):
        """ Handle editing preferences """
        self.config.edit()
        
        
    def ExportEPSF(self):
        """ GUI to control export of EPSF file  """
        file = asksaveasfilename(title="Export EPSF",
                                 defaultextension=".eps",
                                 filetypes = [  ("Encapsulated PS", ".eps"),
                                                ("Postscript", ".ps")
                                                ]
                                 )
        if file is not "": 
            self.graphDisplay.PrintToPSFile(file)

    def ExportSVG(self):
        """ GUI to control export of SVG file  """
        fileName = asksaveasfilename(title="Export SVG",
                                 defaultextension=".svg",
                                 filetypes = [("SVG", ".svg")]
                                 )
        if fileName is not "":
            import GatoExport
            GatoExport.ExportSVG(fileName, self, self.algorithm,
                                 self.graphDisplay,
                                 self.secondaryGraphDisplay.animator, #XXX potential bug
                                 # self.secondaryGraphDisplay is AnimationHistory(sec...)
                                 showAnimation=False)

    def ExportSVGAnimation(self, fileName=None):
        """ GUI to control export of SVG file  """
        if not fileName:
            fileName = asksaveasfilename(title="Export SVG",
                                         defaultextension=".svg",
                                         filetypes = [("SVG", ".svg")]
                                         )
        if fileName is not "":
            import GatoExport
            
            # We never destroy the secondary graph display (and create it from the beginning
            # for the paned viewed. graphDisplays is set from prolog
            if not self.secondaryGraphDisplay or self.algorithm.graphDisplays == None or self.algorithm.graphDisplays == 1:
                GatoExport.ExportSVG(fileName, self, self.algorithm, self.graphDisplay, None, None, showAnimation=True, 
                    init_edge_infos=self.algorithm.DB.init_edge_infos, init_vertex_infos=self.algorithm.DB.init_vertex_infos,
                    init_graph_infos=self.algorithm.DB.init_graph_infos)
            else:
                GatoExport.ExportSVG(fileName, self, self.algorithm, self.graphDisplay,
                    self.secondaryGraphDisplay.animator, #XXX potential bug: self.secondaryGraphDisplay is AnimationHistory(sec...),
                    self.secondaryGraphDisplay, showAnimation=True,
                    init_edge_infos=self.algorithm.DB.init_edge_infos, init_vertex_infos=self.algorithm.DB.init_vertex_infos,
                    init_graph_infos=self.algorithm.DB.init_graph_infos)
            
    def Quit(self,event=None):
        if self.algorithmIsRunning == 1:
            self.commandAfterStop = self.Quit
            self.CmdStop()
            return
            
        if askokcancel("Quit","Do you really want to quit?"):
            self.CleanUp()
            #self.quit() ## WORKS, except when the algorithm is
            ## started from the command line. So we do it by hand
            if self.graphDisplay != None:
                self.graphDisplay.destroy()
            if self.secondaryGraphDisplay is not None:
                self.secondaryGraphDisplay.destroy()
            self.destroy()
            os._exit(0)

            
    def OneGraphWindow(self,event=None):
        """ Align windows nicely for one graph window """
        self.WithdrawSecondaryGraphDisplay()
        self.master.update()
        if self.graph_panes: # Pane is already moved by Withdraw ...
            # XXX Restrain window size: Bigger Problem on MacOS X/Aqua
            return        
        if self.windowingsystem == 'aqua':
            screenTop = 22 # Take care of menubar
        else:
            screenTop = 0 
            
        # Keep the AlgoWin fixed in size but move it to 0,0  
        (topWMExtra,WMExtra) = WMExtrasGeometry(self.graphDisplay)
        pad = 1 # Some optional extra space
        trueWidth  = self.master.winfo_width() + 2 * WMExtra + pad
        
        # Move AlgoWin so that the WM extras will be at 0,0 
        # Silly enough one hast to specify the true coordinate at which
        # the window will appear
        try:
            self.master.geometry("+%d+%d" % (pad, screenTop + pad)) 
        except TclError:
            log.debug("OneGraphWindow: self.master.geometry failed for +%d+%d" % (pad, screenTop + pad)) 
            
        log.debug("OneGraphWindow: screen= (%d * %d), extras = (%d %d)" % (
            self.master.winfo_screenwidth(),
            self.master.winfo_screenheight(),
            WMExtra,
            topWMExtra)
                  )
        
        # Move graph win to take up the rest of the screen
        screenwidth  = self.master.winfo_screenwidth()
        screenheight = self.master.winfo_screenheight() - screenTop
        self.graphDisplay.geometry("%dx%d+%d+%d" % (
            screenwidth - trueWidth - 2 * WMExtra - pad - 1,# see 1 below  
            screenheight - WMExtra - topWMExtra - pad, 
            trueWidth + 1 + pad, 	    
            screenTop + pad))
        self.graphDisplay.update()
        self.graphDisplay.tkraise()
        self.master.update()
        
        
    def TwoGraphWindow(self,event=None):
        """ Align windows nicely for two graph windows """
        self.OpenSecondaryGraphDisplay()
        self.master.update()
        if self.graph_panes: # Pane is already moved by Open ...
            return        
        
        if self.windowingsystem == 'aqua':
            screenTop = 22 # Take care of menubar
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
        
        self.graphDisplay.tkraise()
        self.secondaryGraphDisplay.tkraise()
        self.master.update()
        
    def AboutBox(self):
        d = AboutBox(self.master)
        
    def HelpBox(self,event=None):
        d = HTMLViewer(gGatoHelp, "Help", self.master)

    def GoToGatoWebsite(self):
        webbrowser.open(gGatoURL, new=1, autoraise=1)

    def GoToCATBoxWebsite(self):
        webbrowser.open(gCATBoxURL, new=1, autoraise=1)

    def AboutAlgorithm(self):
        d = HTMLViewer(self.algorithm.About(), "About Algorithm", self.master)
        self.AboutAlgorithmDialog = d
        
    def AboutGraph(self):
        d = HTMLViewer(self.graphDisplay.About(stripPath(self.algorithm.graphFileName)),
                       "About Graph", self.master)
        self.AboutGraphDialog = d
        
    ############################################################
    #    # Tool bar Commands
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
        self.algorithmIsRunning = 0
        self.buttonStart['state']    = NORMAL
        self.buttonStep['state']     = DISABLED
        self.buttonTrace['state']    = DISABLED
        self.buttonContinue['state'] = DISABLED
        self.buttonStop['state']     = DISABLED
        
        # Un-activate last line 
        if self.lastActiveLine != 0:
            self.unTagLine(self.lastActiveLine,'Active')
        self.update() # Forcing redraw
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
        #widget.bind('<DESTROY>',self.OnQuitMenu)
        # self.master.bind_all screws up EPSF save dialog
        widget.bind('s', self.KeyStart)
        widget.bind('x', self.KeyStop)
        widget.bind('<space>', self.KeyStep)
        widget.bind('c', self.KeyContinue)
        widget.bind('t', self.KeyTrace)
        widget.bind('b', self.KeyBreak)        
        if self.experimental:
            widget.bind('r', self.KeyReplay)
            widget.bind('u', self.KeyUndo)
            widget.bind('d', self.KeyDo)
        
        # Cross-plattform accelerators
        if self.windowingsystem == 'aqua':
            accMod = "Command"
        else:
            accMod = "Control"
       
        widget.bind('<%s-q>' % accMod,  self.Quit)
        widget.bind('<%s-comma>' % accMod,  self.Preferences)
        widget.bind('<%s-KeyPress-1>' % accMod,  self.OneGraphWindow)
        widget.bind('<%s-KeyPress-2>' % accMod,  self.TwoGraphWindow)
        widget.bind('<%s-question>' % accMod,  self.HelpBox)

              
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
        
    def KeyReplay(self, event):
        """ Command for Replaying last animation """
        self.algorithm.Replay()
        
    def KeyUndo(self, event):
        """ Command for Replaying last animation """
        self.algorithm.Undo()
        
    def KeyDo(self, event):
        """ Command for Replaying last animation """
        self.algorithm.Do()
        
        
        
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
        self.codeLineHistory.append(AnimationCommand(self.ShowActive, (lineNo,), []))
        
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
        
    def PickInteractive(self, type, filterChoice=None, default=None):
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
        if default == "None":
            self.graphDisplay.UpdateInfo("Select a " + type + 
                                         " or click 'Step' or 'Continue' for no selection")
        elif default == None:
            self.graphDisplay.UpdateInfo("Select a " + type + 
                                         " or click 'Step' or 'Continue' for random selection")
        else:
            self.graphDisplay.UpdateInfo("Select a " + type + 
                                         " or click 'Step' or 'Continue' for default selection")
            
        self.clickResult = (None,None)
        goOn = 1
        while goOn == 1:
            self.wait_variable(self.goOn)
            if self.clickResult[0] == type:
                if filterChoice:
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
            
            
    def HandleFileIOError(self,fileDesc,fileName,errNo="",strError=""):
        if errNo == "":
            msg = "I/O error occured for file %s: %s" % (fileName, fileDesc)
        else:
            msg = "I/O error(%s) occured for %s file %s: %s" % (errNo, fileDesc,
                                                                fileName, strError)
        log.error(msg)
        showerror("Gato - File Error",msg)

    def HandleError(self, short_msg, long_msg, log_function):
        log_function(short_msg)
        if g.Interactive:
            showerror("Gato - Error", short_msg + '\n' + long_msg)

    def ReportCallbackException(self, *args):
        short_msg = "Internal Gato error"
        long_msg = ''.join(traceback.format_exception(*args))
        self.HandleError(short_msg, long_msg, log.exception)

    def ClearHistory(self):
        self.lastActiveLine = 0
        self.codeLineHistory = []

                
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
        self.init_edge_infos = [None, None]
        self.edge_infos = [None, None]
        self.init_vertex_infos = [None, None]
        self.vertex_infos = [None, None]
        self.init_graph_infos = [None, None]
        self.graph_infos = [None, None]
        
    def dispatch_line(self, frame):
        """ *Internal* Only dispatch if we are in the algorithm file """
        fn = frame.f_code.co_filename
        #XXX print frame.f_locals. Could extract values here.
        # What do do about vars going out of scope?
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
        #import inspect
        fn = frame.f_code.co_filename
        line = self.currentLine(frame)
        #log.debug("dispatch_call %s %s %s %s %s %s" % (fn, line, frame, self.stop_here(frame), self.break_anywhere(frame), self.break_here(frame)))
        #log.debug("%s" % inspect.getframeinfo(frame))
        doTrace = self.doTrace # value of self.doTrace might change
        # No tracing of functions defined outside of our algorithmfile 
        if fn != self.GUI.algoFileName:
            return None
            #import inspect
            #log.debug("dispatch_call %s %s %s %s %s %s" % (fn, line, frame, self.stop_here(frame), self.break_anywhere(frame), self.break_here(frame)))
            #log.debug("%s" % inspect.getframeinfo(frame))
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
            self.doTrace = 0 #1 # We will break if there is a breakpoint set in
            # function called (set to self.doTrace = 1 if you don't want that)
            return self.trace_nofeedback_dispatch	    
        #log.debug("%s" % inspect.getframeinfo(frame))
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
        log.debug("bdb.Bdb.dispatch: unknown debugging event: %s" % event)
        
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
        #log.debug("*user_call* %s %s" % (line, argument_list))
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
        # XXX No idea why this is here
        #import inspect
        #log.debug("%s" % inspect.getframeinfo(frame))
            
    def user_line(self, frame):
        """ *Internal* This function is called when we stop or break at this line  """
        self.doTrace = 0 # XXX
        line = self.currentLine(frame)
        # log.debug("*user_line* %s" % line)
        if line in self.GUI.breakpoints:
            self.GUI.mode = 2
        self.GUI.GUI.ShowActive(line)
        self.interaction(frame, None)
        
    def user_return(self, frame, return_value):
        """ *Internal* This function is called when a return trap is set here """
        #import inspect
        frame.f_locals['__return__'] = return_value
        #log.debug('--Return--')
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
        #log.debug("exc_type_name: %s" repr.repr(exc_value))
        self.interaction(frame, exc_traceback)
      
    def add_info_commands_to_history(self):
        ''' Inspects the graphInformer of each graph display to look for changes to 
            the edge, graph, and vertex info.  If there are changes then we execute 
            the relevant command in GraphDisplay so it shows up in the animation history
        '''

        # TODO: PASS IN INITIAL GRAPH AND VERTEX INFO LIKE WE DO INITIAL EDGE INFO
        # TODO: WHY AREN'T UPDATEVERTEXINFO COMMANDS MAKING IT IN?

        def construct_initial_graph_infos():
            for i in xrange(num_graphs):
                if self.init_graph_infos[i] is None:
                    self.init_graph_infos[i] = informers[i].DefaultInfo()
                    self.graph_infos[i] = copy.deepcopy(self.init_graph_infos[i])

        def construct_initial_edge_infos():
            for i in xrange(num_graphs):
                if self.init_edge_infos[i] is None:
                    self.init_edge_infos[i] = {}
                    for e in edges[i]:
                        self.init_edge_infos[i][e] = informers[i].EdgeInfo(e[0], e[1])
                    self.edge_infos[i] = copy.deepcopy(self.init_edge_infos[i])

        def construct_initial_vertex_infos():
            for i in xrange(num_graphs):
                if self.init_vertex_infos[i] is None:
                    self.init_vertex_infos[i] = {}
                    for v in vertices[i]:
                        self.init_vertex_infos[i][v] = informers[i].VertexInfo(v)
                    self.vertex_infos[i] = copy.deepcopy(self.init_vertex_infos[i])

        def check_for_edge_info_changes():
            for i in xrange(num_graphs):
                edge_infos = self.edge_infos[i]
                history = histories[i]
                informer = informers[i]
                for e in edges[i]:
                    if e not in edge_infos:
                        edge_infos[e] = informer.EdgeInfo(e[0], e[1])
                        history.UpdateEdgeInfo(e[0], e[1], edge_infos[e])
                    else:
                        past_info = edge_infos[e]
                        curr_info = informer.EdgeInfo(e[0], e[1])
                        if past_info != curr_info:
                            edge_infos[e] = curr_info
                            history.UpdateEdgeInfo(e[0], e[1], curr_info)
                
                for e in edge_infos.keys():
                    if e not in edges[i]:
                        del edge_infos[e]

        def check_for_vertex_info_changes():
            for i in xrange(num_graphs):
                vertex_infos = self.vertex_infos[i]
                history = histories[i]
                informer = informers[i]
                for v in vertices[i]:
                    if v not in vertex_infos:
                        vertex_infos[v] = informer.VertexInfo(v)
                        history.UpdateVertexInfo(v, vertex_infos[v])
                    else:
                        past_info = vertex_infos[v]
                        curr_info = informer.VertexInfo(v)
                        if past_info != curr_info:
                            vertex_infos[v] = curr_info
                            history.UpdateVertexInfo(v, curr_info)

                for v in vertex_infos.keys():
                    if v not in vertices[i]:
                        del vertex_infos[v]

        def check_for_graph_info_changes():
            for i in xrange(num_graphs):
                if self.graph_infos[i] != informers[i].DefaultInfo():
                    self.graph_infos[i] = informers[i].DefaultInfo()
                    histories[i].UpdateGraphInfo(self.graph_infos[i])

        # Note since naming is weird: self.GUI is the Algorithm() instance.  self.GUI.GUI is the AlgoWin instance
        num_graphs = 1
        informers = [self.GUI.GUI.graphDisplay.graphInformer]
        vertices = [self.GUI.graph.vertices]
        edges = [self.GUI.graph.edgeWeights[0].keys()]    # list of tuples that are edges
        histories = [self.GUI.animation_history]
        if self.GUI.GUI.secondaryGraphDisplay is not None and self.GUI.GUI.secondaryGraphDisplay.graphInformer is not None:
            num_graphs = 2
            histories.append(self.GUI.GUI.secondaryGraphDisplay)
            informers.append(self.GUI.GUI.secondaryGraphDisplay.graphInformer)
            edges.append(self.GUI.GUI.secondaryGraphDisplay.drawEdges.keys())
            vertices.append(self.GUI.GUI.secondaryGraphDisplay.drawVertex.keys())

        construct_initial_graph_infos()
        construct_initial_edge_infos()
        construct_initial_vertex_infos()
        check_for_graph_info_changes()
        check_for_edge_info_changes()
        check_for_vertex_info_changes()
        

    def interaction(self, frame, traceback):
        """ *Internal* This function does all the interaction with the user
            depending on self.GUI.mode
        
            - Step (self.GUI.mode == 2)
            - Quit (self.GUI.mode == 0)
            - Auto-run w/timer (self.GUI.mode == 1)
        """
        self.add_info_commands_to_history()
    
        self.setup(frame, traceback)
        # 
        #line = self.currentLine(frame)
        if self.GUI.mode == 2:
            old = self.GUI.mode
            self.GUI.GUI.WaitNextEvent() # user event -- might change self.GUI.mode
            #log.debug("self.GUI.mode: %s -> %s " % (old, self.GUI.mode))
            #if self.GUI.mode == 2: 
            #self.do_next()
            
        if self.GUI.mode == 0:
            self.do_quit()
            return # Changed
            
        if self.GUI.mode == 1:
            self.GUI.GUI.WaitTime(4 * g.BlinkRate)   # timer event was 10
            #self.do_next()
            
        self.forget()
        
        
    def do_next(self):
        self.set_next(self.curframe)
        
    def do_quit(self):
        self.set_quit()
        
    def currentLine(self, frame):
        """ *Internal* returns the current line number  """ 
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
        self.graph = None           # graph for the algorithm
        self.cleanGraphCopy = None  # this is the backup of the graph
        self.graphIsDirty = 0       # If graph was changed by running
        self.algoGlobals = {}       # Sandbox for Algorithm
        self.logAnimator = 1
        self.about = None
        self.animation_history = None

        self.commentPattern = re.compile('[ \t]*#')
        self.blankLinePattern = re.compile('[ \t]*\n')
        
        
    def SetGUI(self, itsGUI):
        """ Set the connection to its GUI """
        self.GUI = itsGUI
        
        
    def Open(self,file):
        """ Read in an algorithm from file. """
        input=open(file, 'r')
        self.source = input.read()
        input.close()
        self.ClearBreakpoints()
        self.algoFileName = file
        
        # Now read in the prolog as a module to get access to the following data
        # Maybe should obfuscate the names ala xxx_<bla>, have one dict ?
        try:
            input = open(os.path.splitext(self.algoFileName)[0] + ".pro", 'r')
            options = self.ReadPrologOptions(input)
            input.close()
        except (EOFError, IOError),(errno, strerror):
            self.GUI.HandleFileIOError("prolog",os.path.splitext(self.algoFileName)[0] + ".pro",
                                       errno, strerror)
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
        try:
            self.noGraphNeeded = options['noGraphNeeded']
        except:
            self.noGraphNeeded = 0
            
            
        if self.graphDisplays != None:
            if self.graphDisplays == 1 and hasattr(self,"GUI"):
                self.GUI.WithdrawSecondaryGraphDisplay()
                
                
    def ReadPrologOptions(self, file):
        """ Prolog files should contain the following variables:
            - breakpoints = [] a list of line numbers which are choosen as default
                               breakpoints
            - interactive = [] a list of line numbers which contain interactive commands
                               (e.g., PickVertex)
            - graphDisplays = 1 | 2 the number of graphDisplays needed by the algorithm
            - about = \"\"\"<HTML-code>\"\"\" information about the algorithm
        
            Parameter: filelike object
        """
        import re
        import sys
        
        text = file.read()
        options = {}
        optionPattern = {'breakpoints':'breakpoints[ \t]*=[ \t]*(\[[^\]]+\])',
                         'interactive':'interactive[ \t]*=[ \t]*(\[[^\]]+\])',
                         'graphDisplays':'graphDisplays[ \t]*=[ \t]*([1-2])',
                         'noGraphNeeded':'noGraphNeeded[ \t]*=[ \t]*([0-1])'}
        # about is more complicated
        
        for patternName in optionPattern.keys():
            compPattern = re.compile(optionPattern[patternName])
            match = compPattern.search(text) 
            
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
        if self.about:
            return self.about
        else:
            return "<HTML><BODY> <H3>No information available</H3></BODY></HTML>"
            
    def OpenGraph(self,file,fileName=None):
        """ Read in a graph from file and open the display """
        if type(file) in types.StringTypes:
            self.graphFileName = file
        elif type(file)==types.FileType or issubclass(file.__class__,StringIO.StringIO):
            self.graphFileName = fileName
        else:
            raise Exception("wrong types in argument list: expected string or file like object")
        self.cleanGraphCopy = OpenCATBoxGraph(file)
        self.restoreGraph()
        self.GUI.graphDisplay.Show() # In case we are hidden
        self.GUI.graphDisplay.ShowGraph(self.graph, stripPath(self.graphFileName))
        self.GUI.graphDisplay.RegisterGraphInformer(WeightedGraphInformer(self.graph))
        self.GUI.graphDisplay.UpdateScrollRegion(auto=1)
        
    def restoreGraph(self):
        self.graph=copy.deepcopy(self.cleanGraphCopy)
        self.graphIsDirty = 0
        
    def OpenSecondaryGraph(self,G,title,informer=None):
        """ Read in graph from file and open the the second display """
        self.GUI.OpenSecondaryGraphDisplay()
        self.GUI.secondaryGraphDisplay.ShowGraph(G, title)
        self.GUI.secondaryGraphDisplay.UpdateScrollRegion(auto=1)
        if informer is not None:
            self.GUI.secondaryGraphDisplay.RegisterGraphInformer(informer)
            
            
    def ReadyToStart(self):
        """ Return 1 if we are ready to run. That is when we user
            has opened both an algorithm and a graph.  """
        if self.algoFileName != "": # Algorithm openend
            if self.graphFileName != "":
                return 1
            elif self.noGraphNeeded == 1:
                # If no graph is loaded then we still have to show an empty
                # graph. Otherwise the GraphDisplay is unhappy.
                self.graphIsDirty = 1
                self.cleanGraphCopy = Graph.Graph()
                return 1
            else:
                return 0
        else:
            return 0
            
    def Start(self, prologOnly=False):
        """ Start an loaded algorithm. It firsts execs the prolog and
            then starts the algorithm in the debugger. The algorithms
            globals (i.e., the top-level locals are in a dict we supply
            and for which we preload the packages we want to make available)"""
        if self.graphIsDirty == 1:
            self.restoreGraph()
            # Does show 
            self.GUI.graphDisplay.Show() # In case we are hidden
            self.GUI.graphDisplay.ShowGraph(self.graph, stripPath(self.graphFileName))
            self.GUI.graphDisplay.RegisterGraphInformer(WeightedGraphInformer(self.graph))
            self.GUI.graphDisplay.UpdateScrollRegion(auto=1)
        else:
            self.GUI.graphDisplay.Show() # In case we are hidden
        self.graphIsDirty = 1
        self.mode = 1
        
        # Set global vars ...
        self.algoGlobals = {}
        self.algoGlobals['self'] = self
        self.algoGlobals['G'] = self.graph
        
        self.animation_history = None
        self.GUI.ClearHistory()
        if self.logAnimator > 0 and self.GUI.secondaryGraphDisplay:
            self.GUI.secondaryGraphDisplay.Clear()

        #XXX Take care of second graph window
        if self.logAnimator == 1:
            self.animation_history = AnimationHistory(self.GUI.graphDisplay)
            self.algoGlobals['A'] = self.animation_history
        elif self.logAnimator == 2:
            self.animation_history = AnimationHistory(self.GUI.graphDisplay,
                                                      'disp1\t')
            self.animation_history.auto_print = 1
            self.algoGlobals['A'] = self.animation_history
        else:
            self.algoGlobals['A'] = self.GUI.graphDisplay

        # Explictely load packages we want to make available to the algorithm
        # NOTE: algorithm prologs should not import Gato modules directly
        # see below
        modules = ['DataStructures', 
                   'AnimatedDataStructures', 
                   'AnimatedAlgorithms',
                   'GraphUtil',
                   'GatoUtil',
                   'Graph']
        
        try:
            # The binaries behave as if you are starting Gato.py in the directory
            # containing it
            for m in modules:
                exec("from %s import *" % m, self.algoGlobals, self.algoGlobals)
        except:
            # For a Gato installed in <some-path>/lib/site-packages/Gato/ with
            # <some-path>/lib/site-packages on the Python path.
            for m in modules:
                exec("from Gato.%s import *" % m, self.algoGlobals, self.algoGlobals)
            
            
        # transfer required globals
        self.algoGlobals['gInteractive'] = g.Interactive
        # Read in prolog and execute it
        try:
            execfile(os.path.splitext(self.algoFileName)[0] + ".pro", 
                     self.algoGlobals, self.algoGlobals)
        except AbortProlog as e:
            # Only get here because NeededProperties was canceled by user
            log.info(e.value)
            self.GUI.CommitStop()
            return
        except (EOFError, IOError), (errno, strerror):
            self.GUI.HandleFileIOError("prolog",
                                       os.path.splitext(self.algoFileName)[0] + ".pro",
                                       errno,strerror)
            self.GUI.CommitStop()
            return
        except: # Bug in the prolog
            short_msg = "Error in %s.pro" % os.path.splitext(self.algoFileName)[0]
            long_msg = traceback.format_exc()
            self.GUI.HandleError(short_msg, long_msg, log.exception)            
            self.GUI.CommitStop()
            return
        
        if prologOnly:
            return
        # Read in algo and execute it in the debugger
        file = self.algoFileName
        # Filename must be handed over in a very safe way
        # because of \ and ~1 under windows
        self.algoGlobals['_tmp_file']=self.algoFileName
        
        # Switch on all shown breakpoints
        for line in self.breakpoints:
            self.DB.set_break(self.algoFileName,line)
        try:
            command = "execfile(_tmp_file)"
            self.DB.run(command, self.algoGlobals, self.algoGlobals)
        except:
            short_msg = "Error in %s.alg" % os.path.splitext(self.algoFileName)[0]
            long_msg = traceback.format_exc()
            self.GUI.HandleError(short_msg, long_msg, log.exception)            
            
        self.GUI.CommitStop()
        
    def Stop(self):
        self.mode = 0
        
    def Step(self):
        if self.animation_history is not None:
            self.animation_history.DoAll()        
        self.DB.doTrace = 0
        self.mode = 2 
        
    def Continue(self):
        if self.animation_history is not None:
            self.animation_history.DoAll()
        self.DB.doTrace = 0
        self.mode = 1
        
    def Trace(self):
        if self.animation_history is not None:
            self.animation_history.DoAll()
        self.mode = 2 
        self.DB.doTrace = 1
        
    def Replay(self):
        #self.GUI.CmdStep()
        if self.animation_history is not None:
            self.animation_history.DoAll()
            self.animation_history.Replay()
            
    def Undo(self):
        #self.GUI.CmdStep()
        if self.animation_history is not None:
            self.animation_history.Undo()
            
    def Do(self):
        #self.GUI.CmdStep()
        if self.animation_history is not None:
            self.animation_history.Do()    
            
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
        log.info("SetBreakpoints() is depreciated. Use 'breakpoint' var in prolog instead. ")
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
            codeline = linecache.getline(self.algoFileName,line)
            if codeline != '' and self.commentPattern.match(codeline) == None and \
                   self.blankLinePattern.match(codeline) == None:
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
        
            Proper names for properties are defined in gProperty
        """
        for property,requiredValue in propertyValueDict.iteritems():
            failed = 0
            value = self.graph.Property(property)
            if value != 'Unknown':   
                try:
                    c = cmp(value,requiredValue)
                    if gProperty[property][0] < 0 and c > 0:
                        failed = 1
                    elif gProperty[property][0] == 0 and c != 0:
                        failed = 1
                    if gProperty[property][0] > 0 and c < 0:
                        failed = 1                            
                except ValueError:
                    failed = 1
            
            if failed or value == 'Unknown':
                # For GatoTest: Abort if needed property is missing from graph 
                if not g.Interactive:
                    raise AbortProlog, "Not running interactively. Aborting due to" \
                          " check for property %s" % property                    
                errMsg = "The algorithm %s requires that the graph %s has %s" % \
                         (stripPath(self.algoFileName),
                          stripPath(self.graphFileName),
                          gProperty[property][1])
                if gProperty[property][0] < 0:
                    errMsg += " of %s or less" % str(requiredValue)
                elif gProperty[property][0] > 0:
                    errMsg += " of %s or more" % str(requiredValue)
                if value == "Unknown":
                    errMsg += ". This is not known"
                errMsg += ".\nDo you still want to proceed ?"                          
                r = askokcancel("Gato - Error", errMsg)
                if r == False:
                    raise AbortProlog, "User aborted at check for property %s" % property
                    
    def PickVertex(self, default=None, filter=None, visual=None):
        """ Pick a vertex interactively. 
        
            - default: specifies the vertex returned when user does not
              want to select one. If default==None, a random
              vertex not subject to filter will be returned.
        
            - filter: a function which should return a non-None value
              if the passed vertex is acceptable
        
            - visual is a function which takes the vertex as its 
              only argument and cause e.g. some visual feedback """
        v = None
        if g.Interactive:
            v = self.GUI.PickInteractive('vertex', filter, default)
        if not v:
            v = default if default else random.choice(self.graph.vertices)
        if visual:
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
        if g.Interactive:
            e = self.GUI.PickInteractive('edge', filter, default)
        if not e:
            e = default if default else random.choice(self.graph.Edges())
        if visual:
            visual(e)
        return e
        
        
################################################################################
def usage():
    print "Usage: Gato.py"
    print "       Gato.py -v algorithm.alg graph.cat | gato-file"
    print "               -v or --verbose switches on the debugging/logging information"


def main(argv=None):
    if not argv: 
        argv = sys.argv    
    try:
        opts, args = getopt.getopt(argv[1:], "pvdx", ["verbose","paned","debug","experimental"])
    except getopt.GetoptError:
        usage()
        return 2

    paned = False
    debug = False
    verbose = False        
    experimental = False

    if len(args) < 4:
        import logging
        log = logging.getLogger("Gato")
        for o, a in opts:
            if o in ("-v", "--verbose"):
                verbose = True
                if sys.version_info[0:2] < (2,4):
                    log.addHandler(logging.StreamHandler(sys.stdout))
                    log.setLevel(logging.DEBUG)
                else:
                    logging.basicConfig(level=logging.DEBUG,
                                        stream=sys.stdout,
                                        format='%(name)s %(levelname)s %(message)s')
            if o in ("-p", "--paned"):
                paned = True
            if o in ("-d", "--debug"):
                debug = True
            if o in ("-x", "--experimental"):
                experimental = True

        tk = Tk()
        # Prevent the Tcl console from popping up in standalone apps on MacOS X
        # Checking for hasattr(sys,'frozen') does not work for bundelbuilder
        try:
            tk.tk.call('console','hide')
        except tkinter.TclError:
            pass

        #tk.option_add('*ActiveBackground','#EEEEEE')
        tk.option_add('*background','#DDDDDD')
        #XXX Buttons look ugly with white backgrounds on MacOS X, added directly to Button(...)
        # The option not working is might be a known bug 
        # http://aspn.activestate.com/ASPN/Mail/Message/Tcl-bugs/2131881
        # Still present in the 8.4.7 that comes with 10.4  
        tk.option_add('*Highlightbackground','#DDDDDD')
        tk.option_add('*Button.highlightbackground','#DDDDDD')
        tk.option_add('*Button.background','#DDDDDD')
        tk.option_add('Tk*Scrollbar.troughColor','#CACACA')        

        if paned:
            # We want a three paned left | right top / right bottom layout
            pw = PanedWindow(tk)
            pw.pack(fill=BOTH, expand=1)
            graph_panes = PanedWindow(pw, orient=VERTICAL)
            app = AlgoWin(tk, graph_panes, experimental=experimental)
            if debug:
                app.algorithm.logAnimator = 2
            app.OpenSecondaryGraphDisplay()
            graph_panes.add(app.graphDisplay)
            graph_panes.add(app.secondaryGraphDisplay)                        
            pw.add(app)
            pw.add(graph_panes)
            #if app.windowingsystem == 'aqua':
            app.master.geometry("%dx%d+%d+%d" % (
                880,
                600, 
                50, 	    
                50))
            app.tkraise()
            app.master.update()            
            app.OneGraphWindow()
        else:
            app = AlgoWin(tk,experimental=experimental)
            if debug:
                app.algorithm.logAnimator = 2

        # On MacOS X the Quit menu entry otherwise bypasses our Quit
        # Handler According to
        # http://mail.python.org/pipermail/pythonmac-sig/2006-May/017432.html
        # this should work
        if not paned and app.windowingsystem == 'aqua':
            tk.tk.createcommand("::tk::mac::Quit",app.Quit)
            
        # XXX Here we should actually provide our own buffer and a Tk
        # Textbox to write to. NullHandler taken from
        # http://docs.python.org/library/logging.html
        if not verbose:
            if app.windowingsystem == 'win32':
               class NullHandler(logging.Handler):
                   def emit(self, record):
                       pass
               h = NullHandler()
               logging.getLogger("Gato").addHandler(h)
            else:
                logging.basicConfig(level=logging.WARNING,
                                    filename='/tmp/Gato.log',
                                    filemode='w',
                                    format='%(name)s %(levelname)s %(message)s')
        
        # We get here if Gato.py <algorithm> <graph>
        if len(args) == 2:
            algorithm, graph = args[0:2]
            app.OpenAlgorithm(algorithm)
            app.update_idletasks()
            app.update()
            app.OpenGraph(graph)
            app.update_idletasks()
            app.update()
            app.after_idle(app.CmdContinue) # after idle needed since CmdStart
            app.CmdStart()
            app.update_idletasks()
            
        # We get here if Gato.py <gatofile-name|url>
        elif len(args)==1:
            fileName=args[0]
            app.OpenGatoFile(fileName)
            app.update_idletasks()
            app.update()
        app.mainloop()
    else:
        usage()
        return 2
    
if __name__ == '__main__':
    sys.exit(main())
