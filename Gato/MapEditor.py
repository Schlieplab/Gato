from Tkinter import *
import tkSimpleDialog

class MultiListbox(Frame):
    def __init__(self, master, lists, doubleclickCallback = None):
        Frame.__init__(self, master)
        self.lists = []
        for l,w in lists:
            frame = Frame(self); frame.pack(side=LEFT, expand=YES, fill=BOTH)
            Label(frame, text=l, borderwidth=1, relief=RAISED).pack(fill=X)
            lb = Listbox(frame, width=w, borderwidth=0, selectborderwidth=0,
                         relief=FLAT, exportselection=FALSE)
            lb.pack(expand=YES, fill=BOTH)
            self.lists.append(lb)
            lb.bind('<B1-Motion>', lambda e, s=self: s._select(e.y))
            lb.bind('<Button-1>', lambda e, s=self: s._select(e.y))
            lb.bind('<Double-Button-1>', lambda e, s=self: s._double_select(e.y))
            lb.bind('<Leave>', lambda e: 'break')
            lb.bind('<B2-Motion>', lambda e, s=self: s._b2motion(e.x, e.y))
            lb.bind('<Button-2>', lambda e, s=self: s._button2(e.x, e.y))
        frame = Frame(self); frame.pack(side=LEFT, fill=Y)
        Label(frame, borderwidth=1, relief=RAISED).pack(fill=X)
        sb = Scrollbar(frame, orient=VERTICAL, command=self._scroll)
        sb.pack(expand=YES, fill=Y)
        self.lists[0]['yscrollcommand']=sb.set
        self.doubleclickCallback = doubleclickCallback

    def _double_select(self, y):
        row = self.lists[0].nearest(y)
        self.selection_clear(0, END)
        self.selection_set(row)
        self.doubleclickCallback(self.curselection())
        return 'break'

    def _select(self, y):
        row = self.lists[0].nearest(y)
        self.selection_clear(0, END)
        self.selection_set(row)
        return 'break'

    def _button2(self, x, y):
        for l in self.lists: l.scan_mark(x, y)
        return 'break'

    def _b2motion(self, x, y):
        for l in self.lists: l.scan_dragto(x, y)
        return 'break'

    def _scroll(self, *args):
        for l in self.lists:
            apply(l.yview, args)

    def curselection(self):
        return self.lists[0].curselection()

    def delete(self, first, last=None):
        for l in self.lists:
            l.delete(first, last)

    def get(self, first, last=None):
        result = []
        for l in self.lists:
            result.append(l.get(first,last))
        if last: return apply(map, [None] + result)
        return result
            
    def index(self, index):
        self.lists[0].index(index)

    def insert(self, index, *elements):
        for e in elements:
            i = 0
            for l in self.lists:
                l.insert(index, e[i])
                i = i + 1

    def size(self):
        return self.lists[0].size()

    def see(self, index):
        for l in self.lists:
            l.see(index)

    def selection_anchor(self, index):
        for l in self.lists:
            l.selection_anchor(index)

    def selection_clear(self, first, last=None):
        for l in self.lists:
            l.selection_clear(first, last)

    def selection_includes(self, index):
        return self.lists[0].selection_includes(index)

    def selection_set(self, first, last=None):
        for l in self.lists:
            l.selection_set(first, last)


class MapEditor(tkSimpleDialog.Dialog):

    def __init__(self, master, maps, map_titles, field_widths):
        self.maps = maps
        self.map_titles = map_titles
        self.field_widths = field_widths
        self.entryWidget = []
        self.lastSelection = None
	tkSimpleDialog.Dialog.__init__(self, master, "MapEditor")

    def body(self, master):
        outer_frame = Frame(master, relief=SUNKEN, bd=2)

        args = ()
        for i in xrange(len(self.map_titles)):
            args += ((self.map_titles[i], self.field_widths[i]),)
        self.mlb = MultiListbox(outer_frame, args, self.editSelection)
        self.mlb.pack(expand=YES,fill=BOTH)

        frame = Frame(outer_frame, relief=RAISED, bd=2)
        yanf = Frame(frame)
        for i in xrange(len(self.map_titles)):
            self.entryWidget.append(Entry(yanf,width=self.field_widths[i], exportselection=FALSE))
            self.entryWidget[i].pack(padx=4, pady=3, side=LEFT)
        yanf.pack(expand=YES,fill=Y, side=TOP)
        yanf = Frame(frame)
        addButton = Button(yanf, text='Delete', foreground='red', command=self.deleteSelection)
        addButton.pack(padx=4, pady=3, side=RIGHT)
        addButton = Button(yanf, text='Update', foreground='red', command=self.updateMapItem)
        addButton.pack(padx=4, pady=3, side=RIGHT)
        addButton = Button(yanf, text='Add', foreground='red', command=self.addMapItem)
        addButton.pack(padx=6, pady=3, side=RIGHT)
        yanf.pack(expand=YES,fill=Y)
        frame.pack(expand=YES,fill=Y)
        outer_frame.pack(expand=YES,fill=BOTH)

        for k in self.maps[0].keys():
            mapItem = (k,)
            for i in xrange(len(self.maps)):
                mapItem += (self.maps[i][k],)
            self.mlb.insert(END, mapItem)
            
    def addMapItem(self):
        mapItem = ()
        for i in xrange(len(self.map_titles)):
            mapItem += (self.entryWidget[i].get(),)
            self.entryWidget[i].delete(0,END)

        self.mlb.insert(END, mapItem)

    def updateMapItem(self):
        mapItem = ()
        for i in xrange(len(self.map_titles)):
            mapItem += (self.entryWidget[i].get(),)
            self.entryWidget[i].delete(0,END)

        if self.mlb.curselection() == self.lastSelection:
            self.mlb.delete(self.lastSelection)           
            self.mlb.insert(self.lastSelection, mapItem)

    def deleteSelection(self):
        self.mlb.delete(self.mlb.curselection())

    def editSelection(self, selection):
        self.lastSelection = selection
        values = self.mlb.get(selection)
        for i in xrange(len(values)):
            self.entryWidget[i].delete(0,END)
            self.entryWidget[i].insert(0,"%s" % values[i])

    def ok(self, event=None):
        self.result = []
        for i in range(self.mlb.size()):
            self.result.append(self.mlb.get(i))
        tkSimpleDialog.Dialog.ok(self, event)

    
class NamedCollectionEditor(tkSimpleDialog.Dialog):
    """ Provide a simple editor to
        - add items
        - remove items
        - edit items
        in a NamedCollection (e.g. a dictionary). The NamedCollection is responsible
        for supplying:
        - add(name)
        - delete(name)
        - edit(name)
        - names() the name initially listed
        methods, which should being up UI for add/edit if necessary. """ 
        
    def __init__(self, master, collection):
        self.collection = collection
	tkSimpleDialog.Dialog.__init__(self, master, "CollectionEditor")

    def body(self, master):
        outer_frame = Frame(master, relief=SUNKEN, bd=2)

        scrollbar = Scrollbar(outer_frame, orient=VERTICAL)
        self.lb = Listbox(outer_frame, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.lb.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.lb.pack(expand=YES, fill=BOTH)

        for name in self.collection.names():
            self.lb.insert(END, name)

        yanf = outer_frame

        addButton = Button(yanf, text='Delete', foreground='red', command=self.deleteItem)
        addButton.pack(padx=4, pady=3, side=RIGHT)
        addButton = Button(yanf, text='Edit', foreground='red', command=self.editItem)
        addButton.pack(padx=4, pady=3, side=RIGHT)
        addButton = Button(yanf, text='New', foreground='red', command=self.newItem)
        addButton.pack(padx=4, pady=3, side=RIGHT)
        self.nameEntry = Entry(yanf,width=20, exportselection=FALSE)
        self.nameEntry.pack(padx=6, pady=3, side=RIGHT)
        yanf.pack(expand=YES,fill=Y)
        outer_frame.pack(expand=YES,fill=BOTH)
            
    def newItem(self):
        name = self.nameEntry.get()
        self.collection.add(name)
        self.lb.insert(END, name)
        
    def editItem(self):
        name = self.lb.get(self.lb.curselection())
        if name is not "":
            self.collection.edit(self, name)
        
    def deleteItem(self):
        name = self.lb.get(self.lb.curselection())
        self.collection.delete(name)
        self.lb.delete(self.lb.curselection())

    def ok(self, event=None):
        tkSimpleDialog.Dialog.ok(self, event)
    


if __name__ == '__main__':
    tk = Tk()

    map = {"josef":1, "maria":2}
    sexMap = {"josef":'m', "maria":'w'}
    mapedit = MapEditor(tk,[map, sexMap],['Name','Age','Sex'],[32,5,5])
    tk.mainloop()
