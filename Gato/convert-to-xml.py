import GatoFile
import sys
import os
import os.path

convert_to_xml_help=\
"""
convert-to-xml.py [ [--section[=name] ] [*.alg|*.cat]+ ]+

collects graph and algorithm files to one xml-file, that is writen to stdout
"""

class FileCollector(GatoFile.GatoFile):

    def __init__(self):
        # initialise
        GatoFile.GatoFile.__init__(self)

    def parseArgList(self,args):
        """
        work along arglist
        """
        # a work copy
        myArgs=args[:]
        thisSection=None

        while myArgs:
            # consume argument
            thisArg=myArgs.pop(0)

            # begin new section
            if thisArg[:9]=="--section":
                if thisSection:
                    self.appendGatoElement(thisSection)
                SectionName=None
                if len(thisArg)>9 and thisArg[9]=="=":
                    # got section name argument
                    SectionName=thisArg[10:]
                thisSection=self.createGatoElement(SectionName)
                continue

            if thisArg[-4:]==".alg":
                # append algorithm
                AlgorithmName=os.path.basename(thisArg)[:-4]
                if not os.access(thisArg,os.R_OK):
                    print >>sys.stderr, "could not read file %s, ignoring"%thisArg
                    continue
                if thisSection is None:
                    thisSection=self.createGatoElement()
                newAlgorithm=thisSection.createAlgorithmElement(AlgorithmName)
                newAlgorithm.setAlgorithmFromALGFile(thisArg)
                thisSection.updateAlgorithmByName(newAlgorithm)
                continue

            if thisArg[-4:]==".cat":
                # append graph
                GraphName=os.path.basename(thisArg)[:-4]
                if not os.access(thisArg,os.R_OK):
                    print >>sys.stderr, "could not read file %s, ignoring"%thisArg
                    continue
                if thisSection is None:
                    thisSection=self.createGatoElement()
                newGraph=thisSection.createGraphElement(GraphName)
                newGraph.setGraphFromCATFile(file(thisArg))
                thisSection.updateGraphByName(newGraph)
                continue
        #end while
    
        # append last section
        if thisSection:
            self.appendGatoElement(thisSection)

    def help(self,command):
        """
        print help message
        """
        if command=="convert-to-xml.py":
            print convert_to_xml_help
        
    def run(self, args):
        """
        start with full arg list
        """
        if "--help" in args or "-h" in args:
            self.help(args[0])
            return

        self.parseArgList(args[1:])
        if self.dom.documentElement:
            self.write(sys.stdout)

if __name__=="__main__":
    FileCollector().run(sys.argv)
