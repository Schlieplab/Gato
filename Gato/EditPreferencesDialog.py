import tkSimpleDialog 
import sys
import os
import tkFont
from Tkinter import *
from EditObjectAttributesDialog import TkIntEntry, TkStringPopupSelector, TkColorSelector

class TkTestFrame(Frame):

    def __init__(self, parent=None):
	Frame.__init__(self,parent)
        Pack.config(self)
	self.createWidgets()

    def createWidgets(self):
        self.QUIT = Button(self, text='QUIT', foreground='red', 
                           command=self.quit)
        self.QUIT.pack(side=LEFT)
        self.About = Button(self, text='Preferences', foreground='red', 
                           command=self.About)
        self.About.pack(side=LEFT)

    def About(self):
	prefs = {}
	aboutBox = EditPreferencesDialog(self.master, prefs)


class EditPreferencesDialog(tkSimpleDialog.Dialog):
    def __init__(self, master, preferences):
        self.preferences = preferences
	self.widgets = {}
	tkSimpleDialog.Dialog.__init__(self, master, "Preferences")


    def pane(self, master, name, desc):
	result = Frame(master, relief=RIDGE, borderwidth=2)
	labelframe = Frame(result, bg="black")
	label = Label(labelframe, font="Helvetica 12 bold", text=name, justify=LEFT, fg="white", bg="black")
	label.pack(expand=1, fill=BOTH, side=LEFT, anchor=W)
	label = Label(labelframe, font="Helvetica 12 bold", text=desc, justify=RIGHT, fg="white", bg="black")
	label.pack(expand=1, fill=BOTH, side=RIGHT, anchor=E)
	labelframe.grid(column=0, row=0, columnspan=2)
	return result

    def body(self, master):
	#self.resizable(0,0)	

	pane = self.pane(master, "Animation", "Speed and Visuals")
	row = 1

	Label(pane, text="Delay between instructions").grid(row=row, column=0, sticky=E)	
	self.widgets['BlinkRate'] = TkIntEntry(pane, 3)
	self.widgets['BlinkRate'].tkWidget().grid(row=row, column=1, sticky=W)
	self.widgets['BlinkRate'].set(100)

	row += 1
	Label(pane, text="Number of blinks").grid(row=row, column=0, sticky=E)	
	self.widgets['BlinkRepeat'] = TkIntEntry(pane, 2)
	self.widgets['BlinkRepeat'].tkWidget().grid(row=row, column=1, sticky=W)
	self.widgets['BlinkRepeat'].set(4)

	pane.pack(expand=1, fill=BOTH)
	
	pane = self.pane(master, "Algorithm", "Fonts and Colors")
	row = 1
	self.fonts = tkFont.families(master)
	Label(pane, text="Font").grid(row=row, column=0, sticky=E)	
	self.widgets['BlinkRate'] = TkStringPopupSelector(pane, self.fonts)
	self.widgets['BlinkRate'].tkWidget().grid(row=row, column=1, sticky=W)

	row += 1
	Label(pane, text="Font Size").grid(row=row, column=0, sticky=E)	
	self.widgets['FontSize'] = TkIntEntry(pane, 2)
	self.widgets['FontSize'].tkWidget().grid(row=row, column=1, sticky=W)
	self.widgets['FontSize'].set(12)

	row += 1
	Label(pane, text="Font Color").grid(row=row, column=0, sticky=E)	
	self.widgets['AlgoFontColor'] = TkColorSelector(pane, 'black')
	self.widgets['AlgoFontColor'].tkWidget().grid(row=row, column=1, sticky=W)
	
	row += 1
	Label(pane, text="Breakpoint Font Color").grid(row=row, column=0, sticky=E)	
	self.widgets['BreakpointFontColor'] = TkColorSelector(pane, 'black')
	self.widgets['BreakpointFontColor'].tkWidget().grid(row=row, column=1, sticky=W)

	row += 1
	Label(pane, text="Interactive Font Color").grid(row=row, column=0, sticky=E)	
	self.widgets['InteractiveFontColor'] = TkColorSelector(pane, 'black')
	self.widgets['InteractiveFontColor'].tkWidget().grid(row=row, column=1, sticky=W)

	row += 1
	Label(pane, text="Background color").grid(row=row, column=0, sticky=E)	
	self.widgets['AlgoWinBackground'] = TkColorSelector(pane, 'black')
	self.widgets['AlgoWinBackground'].tkWidget().grid(row=row, column=1, sticky=W)

	row += 1
	Label(pane, text="Active lines").grid(row=row, column=0, sticky=E)	
	self.widgets['ActiveBackground'] = TkColorSelector(pane, 'black')
	self.widgets['ActiveBackground'].tkWidget().grid(row=row, column=1, sticky=W)


	pane.pack(expand=1, fill=BOTH)

	

if __name__ == '__main__':
    app = TkTestFrame()
    app.mainloop()




