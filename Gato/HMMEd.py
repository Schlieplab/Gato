#!/usr/bin/env python
################################################################################
#
#       This file is part of Gato (Combinatorial Algorithm Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/~gato
#
#	file:   HMMEd.py
#	author: Alexander Schliep (schliep@zpr.uni-koeln.de)
#
#       _COPYRIGHT_
#
#       This file is version $Revision$ 
#                       from $Date$
#             last change by $Author$.
#
################################################################################

from DataStructures import Point2D
from Graph import Graph
from Gred import *
from GraphUtil import GraphInformer, VertexWeight
from GraphDisplay import GraphDisplay
from GatoUtil import stripPath, extension
from GatoGlobals import *
from GraphEditor import EditWeightsDialog
from tkFileDialog import askopenfilename, asksaveasfilename
import tkMessageBox
from tkMessageBox import askokcancel
import tkSimpleDialog 
import whrandom
import string
import types
import copy
import ProbEditorBasics
import ProbEditorDialogs

import HMMXML
import xml.dom.minidom
import EditObjectAttributesDialog
from EditObjectAttributesDialog import EditObjectAttributesDialog, ValidatingString, ValidatingInt, ValidatingFloat, PopupableInt, Probability, DefaultedInt, DefaultedString

from MapEditor import MapEditor

def typed_assign(var, val):
    result = type(var)(val)
    result.__dict__ = var.__dict__
    #result.__dict__ = copy.copy(var.__dict__)
    return result

def listFromCSV(s, type):
    return map(type,string.split(s,','))

def csvFromList(list, perRow = None):
    if perRow == None:
        return string.join(map(str,list), ', ')
    else:
        result = ""
        for start in xrange(0, len(list), perRow):
            result += string.join(map(str,list[start:start+perRow]), ', ') + ',\n'
        return result[0:len(result)-2]

def writeContents(XMLDoc, XMLNode, data):
    contents = XMLDoc.createTextNode("%s" % data)
    XMLNode.appendChild(contents)

def writeData(XMLDoc, XMLNode, dataKey, dataValue):
    data = XMLDoc.createElement("data")
    data.setAttribute('key', "%s" % dataKey)
    contents = XMLDoc.createTextNode("%s" % dataValue)
    data.appendChild(contents)
    XMLNode.appendChild(data)

def writeXMLData(XMLDoc, XMLNode, dataKey, XMLData):
    data = XMLDoc.createElement("data")
    data.setAttribute('key', "%s" % dataKey)
    data.appendChild(XMLData)
    XMLNode.appendChild(data)

class DOM_Map:
    def __init__(self):
        self.initialize()

    def initialize(self):
        self.name = {}
        self.desc = {}
        self.hasDesc = None
        self.name2code = {}
        
    def addCode(self, code, name, desc = None):
        self.name[code] = name
        if desc != None:
            self.desc[code] = desc
            self.hasDesc = 1
        self.name2code[name] = code

    def low(self):
        return min(self.name.keys())

    def high(self):
        return max(self.name.keys())
    
    def fromDOM(self, XMLNode):
        pass

    def symbolsFromDom(self, XMLNode):
        symbols = XMLNode.getElementsByTagName("symbol")
        
        for symbol in symbols:
            symbolCode = ValidatingInt(int(symbol.getAttribute("code")))
            symbolName = ValidatingString(symbol.firstChild.nodeValue)
            symbolDesc = symbol.getAttribute("desc")
            if symbolDesc != None:
                self.addCode(symbolCode, symbolName, ValidatingString(symbolDesc))
            else:
                self.addCode(symbolCode, symbolName)
                
    def toDOM(self, XMLDoc, XMLNode):
        XMLNode.setAttribute('hmm:low', "%s" % self.low())
        XMLNode.setAttribute('hmm:high', "%s" % self.high())
        map = XMLDoc.createElement("map")  
        for key in self.name.keys():
            symbol = XMLDoc.createElement("symbol")
            symbol.setAttribute('code', "%s" % key)
            if self.hasDesc:
                symbol.setAttribute('desc', "%s" % self.desc[key])
            writeContents(XMLDoc, symbol, "%s" % self.name[key])
            map.appendChild(symbol)
        XMLNode.appendChild(map)
   

class DiscreteHMMAlphabet(DOM_Map):
    def __init__(self):
        DOM_Map.__init__(self)
        self.hmm_type = 'discrete'

    def fromDOM(self, XMLNode):
        """Take dom subtree representing a <hmm:alphabet</hmm:alphabet> element"""
        self.initialize()
        # Not reading: hmm:low hmm:high
        if XMLNode.getAttribute("hmm:type") == self.hmm_type:
            self.symbolsFromDom(XMLNode)
        else:
            print "DiscreteHMMAlphabet wrong type %s" % XMLNode.getAttribute("hmm:type") 

    def toDOM(self, XMLDoc, XMLNode):
        hmmalphabet = XMLDoc.createElement("hmm:alphabet")
        hmmalphabet.setAttribute('hmm:type', 'discrete')
        DOM_Map.toDOM(self, XMLDoc, hmmalphabet)
        XMLNode.appendChild(hmmalphabet)

    def size(self):
        return len(self.name.keys())

    
class HMMClass(DOM_Map):
    def __init__(self):
        DOM_Map.__init__(self)

    def fromDOM(self, XMLNode):
        """Take dom subtree representing a <hmm:class></hmm:class> element"""
        self.initialize()
        self.symbolsFromDom(XMLNode)

    def toDOM(self, XMLDoc, XMLNode):
        hmmclass = XMLDoc.createElement("hmm:class")   
        DOM_Map.toDOM(self, XMLDoc, hmmclass)
        XMLNode.appendChild(hmmclass)

    def edit(self, master):        
        mapedit = MapEditor(master, [self.name, self.desc], ['code','name','desc'], [3,5,35])
        print mapedit.result
        if mapedit.result != None:
            
            new_keys = []
            for (code_str, name, desc) in mapedit.result:
                code = int(code_str)
                self.name[code] = name
                self.desc[code] = desc
                self.name2code[name] = code
                new_keys.append(code)
            
            for key in self.name.keys():
                if key not in new_keys:
                    del self.name2code[self.name[key]]
                    del self.name[key] 
                    del self.desc[key]
                else:
                    self.name2code[self.name[key]] = key
            
            
class HMMState:
    def __init__(self, nodeIndex, itsHMM):

        self.itsHMM = itsHMM

        self.index = nodeIndex # The node index in the underlying graph
        
        self.id = ValidatingString("%s" % nodeIndex)
        self.state_class = PopupableInt()        
        self.state_class.setPopup(itsHMM.hmmClass.name, itsHMM.hmmClass.name2code, 10)

        self.label = ValidatingString("<none>")

        self.order = DefaultedInt()
        self.order.setDefault(1, 0)

        self.emissions = []

        self.initial = Probability("0.0")
        self.tiedto = DefaultedString()
        self.tiedto.setDefault(1, '')
        self.desc = self.id


    editableAttr = ['id', 'state_class', 'label', 'order', 'initial', 'tiedto']
    xmlAttr = editableAttr + ['ngeom', 'emissions']


    def fromDOM(self, XMLNode):

        self.id = ValidatingString(XMLNode.attributes['id'].nodeValue.encode('ascii', 'replace'))
        
        self.index = self.itsHMM.G.AddVertex()
        
        datas = XMLNode.getElementsByTagName("data")
        for data in datas:
            dataKey = data.attributes['key'].nodeValue
            dataValue = data.firstChild.nodeValue

            if dataKey == 'class':
                self.state_class = typed_assign(self.state_class, int(dataValue))
            elif  dataKey == 'label':
                self.label = type(self.label)(dataValue.encode('ascii', 'replace'))

            elif  dataKey == 'order':
                if dataValue == None: # Use default value
                    self.order = typed_assign(self.order, self.order.defaultValue)
                    self.order.useDefault = 1
                else:
                    self.order = typed_assign(self.order, int(dataValue))
                    self.order.useDefault = 0

            elif  dataKey == 'initial':
                self.initial = typed_assign(self.initial, float(dataValue))

            elif  dataKey == 'tiedto':
                
                if dataValue == None: # Use default value
                    self.tiedto = typed_assign(self.tiedto, self.tiedto.defaultValue)
                    self.tiedto.useDefault = 1
                else:
                    self.tiedto = typed_assign(self.tiedto, dataValue.encode('ascii', 'replace'))
                    self.tiedto.useDefault = 0
                    
            elif  dataKey == 'ngeom':
                # We only use pos
                pos = XMLNode.getElementsByTagName('pos')[0] # Just one pos ...                
                self.pos = Point2D(float(pos.attributes['x'].nodeValue),
                                   float(pos.attributes['y'].nodeValue))
                
            elif  dataKey == 'emissions':
                # collect all strings from childnodes
                dataValue = ""
                for child in data.childNodes:
                    dataValue += child.nodeValue
                self.emissions = listFromCSV(dataValue, types.FloatType)
                #print self.emissions
                    
            else:
                print "HMMState.fromDOM: unknown key %s of value %s" % (dataKey, dataValue)
        

    def toDOM(self, XMLDoc, XMLNode, initial_sum):
        node = XMLDoc.createElement("node")
        node.setAttribute('id', "%s" % self.id)

        # Mandatory elems
        writeData(XMLDoc, node, 'label', self.label)
        writeData(XMLDoc, node, 'class', self.state_class)
        writeData(XMLDoc, node, 'initial', self.initial / initial_sum)
        pos = self.itsHMM.G.embedding[self.index]
        pos_elem = XMLDoc.createElement("pos")
        pos_elem.setAttribute('x', "%s" % pos.x)
        pos_elem.setAttribute('y', "%s" % pos.y)
        writeXMLData(XMLDoc, node, 'ngeom', pos_elem)

        if not self.order.useDefault:
            writeData(XMLDoc, node, 'order', self.order)

        if not self.tiedto == '':
            writeData(XMLDoc, node, 'tiedto', self.tiedto)
        else:
            if self.order.useDefault:
                order = 0
            else:
                order = self.order

            # XXX Produce uniform emission probs, if we dont have the correct number of
            # parameters
            size = self.itsHMM.hmmAlphabet.size()**(order+1)
            if len(self.emissions) != size:
                self.emissions = [1.0/size] * size
                
            if order > 0:
                writeData(XMLDoc, node, 'emissions', csvFromList(self.emissions,
                                                                 self.itsHMM.hmmAlphabet.size()))
            else:
                writeData(XMLDoc, node, 'emissions', csvFromList(self.emissions))
            
        XMLNode.appendChild(node)


class HMM:    
    def __init__(self, XMLFileName = None):

 	self.G = Graph()
	self.G.directed = 1
	self.G.euclidian = 0
	self.Pi = {}
        self.id2index = {}

        self.hmmAlphabet = DiscreteHMMAlphabet()
        self.hmmClass = HMMClass()
        
        self.editableAttr = {}
        self.editableAttr['HMM'] = ['desc']
        self.desc = ValidatingString()       

        self.state = {}

        if XMLFileName != None:
            self.OpenXML(XMLFileName)


    def AddState(self, v):
        state = HMMState(v, self)
        self.state[v] = state
        
    def DeleteState(self, v):
        del self.id2index[self.state[v].id]
        del self.state[v]        

    def fromDOM(self, XMLNode):
        
        self.hmmClass.fromDOM(XMLNode.getElementsByTagName("hmm:class")[0]) # One class!
        self.hmmAlphabet.fromDOM(XMLNode.getElementsByTagName("hmm:alphabet")[0]) # One alphabet!

        nodes = XMLNode.getElementsByTagName("node")
        for n in nodes:
            state = HMMState(-1, self)
            state.fromDOM(n)
            i = state.index
            self.state[i] = state
            self.id2index[state.id] = i

            self.G.embedding[i] = state.pos
            self.G.labeling[i] = "%s\n%s" % (state.id, state.label) # XXX Hack Aaaargh!

        edges = XMLNode.getElementsByTagName("edge")
        for edge in edges:
            i = self.id2index[edge.attributes['source'].nodeValue]
            j = self.id2index[edge.attributes['target'].nodeValue]

            datas = edge.getElementsByTagName("data")
            for data in datas:
                dataKey = data.attributes['key'].nodeValue
                dataValue = data.firstChild.nodeValue

            if dataKey == 'prob':
                p = float(dataValue)
                               
            self.G.AddEdge(i, j)
            self.G.edgeWeights[0][(i,j)] = p

    def toDOM(self, XMLDoc, XMLNode):
        graphml = XMLDoc.createElement("graphml")
        XMLNode.appendChild(graphml)

        self.hmmClass.toDOM(XMLDoc, graphml)
        self.hmmAlphabet.toDOM(XMLDoc, graphml) 

        graph = XMLDoc.createElement("graph")

        # Compute sums of initial probabilities for renormalization 
        initial_sum = 0.0
        for s in self.state:
            initial_sum = initial_sum + self.state[s].initial
        
        for s in self.state:
            self.state[s].toDOM(XMLDoc, graph, initial_sum)
        
        # Compute sums of outgoing probabilities for renormalization of transition probabilities
        out_sum = [0.0] * (self.G.Order() + 1)
        for e in self.G.Edges():
            out_sum[e[0]] = out_sum[e[0]] + self.G.edgeWeights[0][e]

        for e in self.G.Edges():
            edge_elem = XMLDoc.createElement("edge")
            edge_elem.setAttribute('source', "%s" % self.state[e[0]].id)
            edge_elem.setAttribute('target', "%s" % self.state[e[1]].id)
            writeData(XMLDoc, edge_elem, 'prob', self.G.edgeWeights[0][e] / out_sum[e[0]])
            graph.appendChild(edge_elem)
            
        graphml.appendChild(graph)

    def OpenXML(self, fileName):
        dom = xml.dom.minidom.parse(fileName)
        assert dom.documentElement.tagName == "graphml"   
        self.fromDOM(dom)
        dom.unlink()

    def WriteXML(self, fileName):
        doc = xml.dom.minidom.Document()
        self.toDOM(doc, doc)
        file = open(fileName, 'w')
        file.write(doc.toprettyxml())
        file.close()
        doc.unlink()

    def SaveAs(self, fileName):
        self.WriteXML(fileName)


class HMMEditor(SAGraphEditor):

    def __init__(self, master=None):
	SAGraphEditor.__init__(self, master)	
	self.HMM = None

    def CreateWidgets(self):

        toolbar = Frame(self, cursor='hand2', relief=FLAT)
        toolbar.pack(side=LEFT, fill=Y) # Allows horizontal growth

        extra = Frame(toolbar, cursor='hand2', relief=SUNKEN, borderwidth=2)
        extra.pack(side=TOP) # Allows horizontal growth
        extra.rowconfigure(5,weight=1)
        extra.bind("<Enter>", lambda e, gd=self:gd.DefaultInfo())

        px = 0 
        py = 3 

        self.toolVar = StringVar()

        import GatoIcons
        # Load Icons
        self.vertexIcon = PhotoImage(data=GatoIcons.vertex)
        self.edgeIcon   = PhotoImage(data=GatoIcons.edge)
        self.deleteIcon = PhotoImage(data=GatoIcons.delete)
        self.swapIcon   = PhotoImage(data=GatoIcons.swap)
        self.editIcon   = PhotoImage(data=GatoIcons.edit)
        self.propIcon   = PhotoImage(data=GatoIcons.edit)
        
        b = Radiobutton(extra, width=32, padx=px, pady=py, 
                        text='Add or move vertex',  
                        command=self.ChangeTool,
                        var = self.toolVar, value='AddOrMoveVertex', 
                        indicator=0, image=self.vertexIcon)
        b.grid(row=0, column=0, padx=2, pady=2)
        b.bind("<Enter>", lambda e, gd=self:gd.UpdateInfo('Add or move vertex'))
        self.defaultButton = b # default doesnt work as config option


        b = Radiobutton(extra, width=32, padx=px, pady=py, 
                        text='Add edge', 
                        command=self.ChangeTool,
                        var = self.toolVar, value='AddEdge', indicator=0,
                        image=self.edgeIcon)
        b.grid(row=1, column=0, padx=2, pady=2)
        b.bind("<Enter>", lambda e, gd=self:gd.UpdateInfo('Add edge'))


        b = Radiobutton(extra, width=32, padx=px, pady=py, 
                        text='Delete edge or vertex', 
                        command=self.ChangeTool,
                        var = self.toolVar, value='DeleteEdgeOrVertex', indicator=0,
                        image=self.deleteIcon)
        b.grid(row=2, column=0, padx=2, pady=2)
        b.bind("<Enter>", lambda e, gd=self:gd.UpdateInfo('Delete edge or vertex'))


        b = Radiobutton(extra, width=32, padx=px, pady=py, 
                        text='Swap orientation', 
                        command=self.ChangeTool,
                        var = self.toolVar, value='SwapOrientation', indicator=0,
                        image=self.swapIcon)
        b.grid(row=3, column=0, padx=2, pady=2)
        b.bind("<Enter>", lambda e, gd=self:gd.UpdateInfo('Swap orientation'))


        b = Radiobutton(extra, width=32, padx=px, pady=py, 
                        text='Edit Weight', 
                        command=self.ChangeTool,
                        var = self.toolVar, value='EditWeight', indicator=0,
                        image=self.editIcon)
        b.grid(row=4, column=0, padx=2, pady=2)
        b.bind("<Enter>", lambda e, gd=self:gd.UpdateInfo('Edit Weight'))

        b = Radiobutton(extra, width=32, padx=px, pady=py, 
                        text='Edit Properties', 
                        command=self.ChangeTool,
                        var = self.toolVar, value='EditProperties', indicator=0,
                        image=self.editIcon)
        b.grid(row=5, column=0, padx=2, pady=2)
        b.bind("<Enter>", lambda e, gd=self:gd.UpdateInfo('Edit Properties'))
        
        GraphEditor.CreateWidgets(self)


    #----- Tools Menu callbacks
    def ChangeTool(self):
        self.SetEditMode(self.toolVar.get())

    def MouseUp(self,event):
	if self.mode == 'AddOrMoveVertex':
	    self.AddOrMoveVertexUp(event)
	elif self.mode == 'AddEdge':
	    self.AddEdgeUp(event)
	elif self.mode == 'DeleteEdgeOrVertex':
	    self.DeleteEdgeOrVertexUp(event)
	elif self.mode == 'SwapOrientation':
	    self.SwapOrientationUp(event)
	elif self.mode == 'EditWeight':
	    self.EditWeightUp(event)
	elif self.mode == 'EditProperties':
	    self.EditPropertiesUp(event)



    def makeMenuBar(self):
	self.menubar = Menu(self,tearoff=0)

	# Add file menu
	self.fileMenu = Menu(self.menubar, tearoff=0)
	self.fileMenu.add_command(label='New',            command=self.NewGraph)
	self.fileMenu.add_command(label='Open ...',       command=self.OpenGraph)
	self.fileMenu.add_command(label='Save',	     command=self.SaveGraph)
	self.fileMenu.add_command(label='Save as ...',    command=self.SaveAsGraph)
	self.fileMenu.add_separator()
	self.fileMenu.add_command(label='Export EPSF...', command=self.ExportEPSF)
	self.fileMenu.add_separator()
	self.fileMenu.add_command(label='Quit',	     command=self.Quit)
	self.menubar.add_cascade(label="File", menu=self.fileMenu, 
				 underline=0)
	
	self.graphMenu = Menu(self.menubar, tearoff=0)
	self.graphMenu.add_command(label='Edit HMM', command=self.EditHMM)
	self.graphMenu.add_command(label='Edit Class label', command=self.EditClassLabel)
	#self.graphMenu.add_command(label='Edit Emissions', command=self.EditEmissions)
	self.graphMenu.add_command(label='Edit Prior', command=self.EditPrior)
	self.graphMenu.add_separator()
	self.graphMenu.add_checkbutton(label='Grid', 
						  command=self.ToggleGridding)	
	self.menubar.add_cascade(label="HMM", menu=self.graphMenu, 
				 underline=0)

	self.master.configure(menu=self.menubar)

    def SetGraphMenuOptions(self):
	if not self.gridding:
	    self.graphMenu.invoke(self.graphMenu.index('Grid'))	
	

    ############################################################
    #
    # Menu Commands
    #
    # The menu commands are passed as call back parameters to 
    # the menu items.
    #
    def NewGraph(self, nrOfSymbols=0):
	self.HMM = HMM()

	self.HMM.G.euclidian = 0
	self.HMM.G.directed = 1
	self.HMM.G.simple = 0
	self.graphName = "New"
	self.ShowGraph(self.HMM.G,self.graphName)
	self.RegisterGraphInformer(HMMInformer(self.HMM))
	self.fileName = None
	self.SetTitle("HMMEd _VERSION_ - New Graph")
	self.SetGraphMenuOptions()
	if nrOfSymbols == 0:
	    nrOfSymbols  = tkSimpleDialog.askinteger("New HMM",
						     "Enter the number of output symbols")
	for i in xrange(nrOfSymbols):
	    self.HMM.G.vertexWeights[i] = VertexWeight(0.0)

    def OpenGraph(self):	
	file = askopenfilename(title="Open HMM",
			       defaultextension=".xml",
			       filetypes = (("XML", ".xml"),
                                            )
			       )
	if file is "": 
	    print "cancelled"
	else:
	    self.fileName = file
	    self.graphName = stripPath(file)
	    e = extension(file)
            
	    if e == 'xml':
		self.HMM.OpenXML(file)
	    else:
		print "Unknown extension"
		return

	    self.ShowGraph(self.HMM.G, self.graphName)
	    self.RegisterGraphInformer(HMMInformer(self.HMM))
	    self.SetTitle("HMMEd _VERSION_ - " + self.graphName)

	    if not self.gridding:
		self.graphMenu.invoke(self.graphMenu.index('Grid'))	


    def SaveGraph(self):
	if self.fileName != None:
	    self.HMM.SaveAs(self.fileName)
	else:
	    self.SaveAsGraph()
	

    def SaveAsGraph(self):
	file = asksaveasfilename(title="Save HMM",
				 defaultextension=".xml",
				 filetypes = ( ("XML", ".xml"),
					       )
				 )
	if file is "": 
	    print "cancelled"
	else:
	    print file
	    self.fileName = file
	    self.HMM.SaveAs(file)
	    self.graphName = stripPath(file)
	    self.SetTitle("HMMEd _VERSION_ - " + self.graphName)


    def EditWeightUp(self,event):
	if event.widget.find_withtag(CURRENT):
	    widget = event.widget.find_withtag(CURRENT)[0]
	    tags = self.canvas.gettags(widget)
	    if "edges" in tags:
 		(tail,head) = self.edge[widget]

                transition_probabilities=ProbEditorBasics.ProbDict({})
		for head in self.HMM.G.OutNeighbors(tail):
		    weight=self.HMM.G.edgeWeights[0][(tail,head)]
		    label = "-> %d" % head
                    transition_probabilities.update({label:weight})

                if transition_probabilities.sum==0:
                    key_list=transition_probabilities.keys()
                    for key in key_list:
                        transition_probabilities[key]=1.0/len(key_list)
                e=ProbEditorBasics.emission_data(transition_probabilities)
                d = ProbEditorDialogs.emission_dialog(self,
                                                      e,
                                                      "transition probs from state %d" % tail)
                if d.success():
                    # write back normalized probabilities
                    for key in transition_probabilities.keys():
                        head = int(key[3:])
                        self.HMM.G.edgeWeights[0][(tail,head)]=transition_probabilities[key]/transition_probabilities.sum

	    else: # We have a vertex
		v = self.FindVertex(event)
		if v != None:
                    state = self.HMM.state[v]
                    if state.order > 0:
                        print "Ooops. Cant edit higher order states"
                        return
                    
                    if state.tiedto != '':
                        msg = "The emission parameters of state %s you attempted to edit are tied to those of state %s." %  (state.id, state.tiedto)
                        #print "Note:", msg
                        if not askokcancel("Edit Tied State", msg + "Edit those of state %s instead?" % state.tiedto):
                            return
                        else:
                            state = self.HMM.state[self.HMM.id2index[state.tiedto]]

                    if state.emissions == []:
                        state.emissions = [1.0 / self.HMM.hmmAlphabet.size()] * self.HMM.hmmAlphabet.size()
                    emission_probabilities = ProbEditorBasics.ProbDict({})

                    for code in self.HMM.hmmAlphabet.name.keys():
                        label = self.HMM.hmmAlphabet.name[code]
                        weight = state.emissions[code]
                        emission_probabilities.update({label:weight})
                        
                    # Normalize ... should be member function
                    if emission_probabilities.sum != 1.0:
                        key_list = emission_probabilities.keys()
                        for key in key_list:
                            emission_probabilities[key] = 1.0 / len(key_list)

                            
                    e = ProbEditorBasics.emission_data(emission_probabilities)
                    d = ProbEditorDialogs.emission_dialog(self, e,
                                                          "emission probs of state %s" % state.id)
                    if d.success():
                        # write back normalized probabilities
                        for key in emission_probabilities.keys():
                            code = self.HMM.hmmAlphabet.name2code[key]
                            state.emissions[code] = emission_probabilities[key] / emission_probabilities.sum	

    def EditPropertiesUp(self,event):
	if event.widget.find_withtag(CURRENT):
	    widget = event.widget.find_withtag(CURRENT)[0]
	    tags = self.canvas.gettags(widget)
	    if not "edges" in tags:
		v = self.FindVertex(event)
                d = EditObjectAttributesDialog(self, self.HMM.state[v], HMMState.editableAttr)

                # We only show the label out of the editable items
                self.HMM.G.labeling[v] = "%s\n%s" % (self.HMM.state[v].id, self.HMM.state[v].label) # XXX Hack Aaaargh!
                self.UpdateVertexLabel(v, 0)
                self.HMM.id2index[self.HMM.state[v].id] = v

                

    def EditHMM(self):
        d = EditObjectAttributesDialog(self, self.HMM, self.HMM.editableAttr['HMM'])

    def EditClassLabel(self):
        self.HMM.hmmClass.edit(self)
        
    def EditPrior(self):
	if self.HMM.G.Order() == 0:
	    return
        
        emission_probabilities = ProbEditorBasics.ProbDict({})
        for state in self.HMM.state.values():
            label = state.id
            weight = state.initial
            emission_probabilities.update({label:weight})

        e = ProbEditorBasics.emission_data(emission_probabilities)
        d = ProbEditorDialogs.emission_dialog(self, e, "initial probabilities")
        u = 1.0 / len(emission_probabilities.keys())
        
        if d.success():
            # write back normalized probabilities
            for key in emission_probabilities.keys():
                state = self.HMM.state[self.HMM.id2index[key]]
                if emission_probabilities.sum == 0.0:
                    state.initial = typed_assign(state.initial, u)
                else:
                    state.initial = typed_assign(state.initial,
                                                 emission_probabilities[key] / emission_probabilities.sum)
                
    def AddVertexCanvas(self,x,y):
	v = GraphDisplay.AddVertexCanvas(self, x, y)
        print "AddVertex at ",x,y
        self.HMM.AddState(v)

    def AddEdge(self,tail,head):
        GraphDisplay.AddEdge(self,tail,head)
        self.HMM.G.edgeWeights[0][(tail, head)] = 1.0
	
    def DeleteVertex(self,v):
        self.HMM.DeleteState(v)
        SAGraphEditor.DeleteVertex(self,v)

    def ShowCoords(self,event):
        pass

    
class HMMInformer(GraphInformer):
    def __init__(self, itsHMM):
        GraphInformer.__init__(self, itsHMM.G)
        self.itsHMM = itsHMM

    def VertexInfo(self,v):
        state = self.itsHMM.state[v]
        msg = "State '%s' class=%s (%s:%s) order=%d" % (state.id, state.state_class,
                                                        self.itsHMM.hmmClass.name[state.state_class],
                                                        self.itsHMM.hmmClass.desc[state.state_class],
                                                        state.order)
        if state.order == 0 and state.emissions != []:
            msg += " [A:%0.3f C:%0.3f G:%0.3f T:%0.3f N:%0.3f]" % tuple(state.emissions)
        return msg

    def EdgeInfo(self,tail,head):
        tail_state = self.itsHMM.state[tail]
        head_state = self.itsHMM.state[head]
        p = self.itsHMM.G.edgeWeights[0][(tail, head)]
        msg = "Transition: '%s' -> '%s' prob=%0.2f" % (tail_state.id, head_state.id, p)
        return msg
       
        

################################################################################
if __name__ == '__main__':
    graphEditor = HMMEditor(Tk())
    graphEditor.NewGraph(2)
    graphEditor.mainloop()
