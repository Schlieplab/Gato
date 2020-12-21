from __future__ import print_function
################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#	file:   GatoFile.py
#	author: Achim Gaedke (achim.gaedke@zpr.uni-koeln.de)
#
#       Copyright (C) 2016-2020 Alexander Schliep and
#	Copyright (C) 1998-2015 Alexander Schliep, Winfried Hochstaettler and 
#       Copyright (C) 1998-2001 ZAIK/ZPR, Universitaet zu Koeln
#                                   
#       Contact: alexander@schlieplab.org             
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
#       This file is version $Revision$ 
#                       from $Date$
#             last change by $Author$.
#
################################################################################
from future import standard_library
standard_library.install_aliases()
from builtins import map
from builtins import range
from builtins import object
import os
import os.path
import shutil
import sys
import string
import re
import tkinter
import tkinter.simpledialog
import tkinter.filedialog
import traceback
import logging
try:
    import winreg
except ImportError:
    # we are not on a windows system
    pass
    
    
gatoMimeType="application/gato"
gatoFileExtension="gato"
gatoDescription="gato graph/algorithm tool"

class ConfigurationException(Exception):
    """
    to report configuration errors
    """
    def __init__(self,message):
        Exception.__init__(self)
        self.message=message
        
    def __repr__(self):
        if hasattr(self,"message"):
            return "%s: %s"%(self.__class__.__name__,self.message)
        else:
            return self.__class__.__name__
            
class configureOS(object):
    """
    system configuration for gato file type support
    """
    
    def __init__(self,DialogMaster=None):
        """
        creates configurator object
        """
        # find script location
        self.myExecutable=os.path.abspath(sys.argv[0])
        self.DialogMaster=DialogMaster
        
    def check(self):
        """
        check, if already configured, returns true, if this executable is installed
        """
        raise ConfigurationException("base class method should not be called")
        
    def askUserInstall(self):
        """
        ask user, if she/he likes configuration
        """
        raise ConfigurationException("base class method should not be called")
        
    def askUserUninstall(self):
        """
        ask user, if she/he likes uninstallation
        """
        raise ConfigurationException("base class method should not be called")
        
    def configureSystem(self):
        """
        do system configuration
        """
        raise ConfigurationException("base class method should not be called")
        
    def unconfigureSystem(self):
        """
        do system unconfiguration
        """
        raise ConfigurationException("base class method should not be called")
        
    def runInstall(self):
        if not self.check() and self.askUserInstall():
            self.configureSystem()
            
    def runUninstall(self):
        if self.check() and self.askUserUninstall():
            self.unconfigureSystem()
            
    def installBinary(self,path):
        """
        installs this binary to another place
        """
        # test, if it is our place...
        if not os.path.exists(path):
            os.makedirs(path)
        newLocation=os.path.join(path,os.path.basename(self.myExecutable))
        if os.path.exists(newLocation):
            os.remove(newLocation)
        shutil.copy2(self.myExecutable,newLocation)
        self.myExecutable=os.path.abspath(newLocation)
        
class configureUnsupported(configureOS):
    """
    some tips and exit
    """
    check=configureSystem=askUserInstall=lambda x:None
    
    def runInstall(self):
        """
        """
        logging.error("unsupported operating system %s" % sys.platform)
        
class configureUNIX(configureOS):
    """
    linux configuration
    expands mailcap file
    """
    
    def __init__(self,DialogMaster=None):
        """
        find script location, configuration file location...
        """
        configureOS.__init__(self,DialogMaster)
        
        # find mailcap file
        if "HOME" not in os.environ:
            raise ConfigurationException("could not determine home directory")
        self.mailcapFile=os.path.join(os.environ["HOME"],".mailcap")
        self.mime_typesFile=os.path.join(os.environ["HOME"],".mime.types")
        
    def check(self):
        """
        """
        self.cache_check_mailcap=self.check_mailcap()
        self.cache_check_mime_types=self.check_mime_types()
        return self.cache_check_mailcap and self.cache_check_mime_types
        
    def check_mailcap(self):
        """        
        """
        if not os.access(self.mailcapFile,os.R_OK):
            return 0
            
        mailcap=file(self.mailcapFile,"r")
        while 1:
            line=mailcap.readline()
            # line end
            if not line:
                break
                
                # skip comments
            if line[0]=="#":
                continue
               
            line=line.strip()
            # skip whitespace
            if len(line) == 0:
                continue                                      
            while line[-1]=="\\":
                line=line[:-1]+mailcap.readline().rstrip()
            entries=line.split(";")
            (mimeType,viewCommand)=list(map(string.strip,entries[:2]))
            
            if (mimeType==gatoMimeType and
                os.path.exists(viewCommand.split(" ")[0]) and
                os.path.samefile(viewCommand.split(" ")[0],self.myExecutable)):
                return 1
                
        return 0
        
    def check_mime_types(self):
        """
        """
        if not os.access(self.mime_typesFile,os.R_OK):
            return 0
            
        mime_types=file(self.mime_typesFile,"r")
        while 1:
            line=mime_types.readline()
            # line end
            if not line:
                break
                
                # skip comments
            if line[0]=="#":
                continue
                
                #catenate lines
            line=line.strip()
            while line[-1]=="\\":
                newLine=mime_types.readline()
                if newLine=="":
                    break
                line=line[:-1]+newLine.rstrip()
                
            mime_dict={}
            # format: key=value or key="value"
            kv_pair=re.compile("(\w+)=((?:\"[^\"]*\")|(?:[^\"\s]*))")
            kv_pairs=kv_pair.findall(line)
            for kv in kv_pairs:
                (key,value)=kv
                if value[0]=="\"":
                    value=value[1:-1]
                mime_dict[key]=value
            if mime_dict.get("type")=="application/gato" and mime_dict.get("exts")=="gato":
                return 1
                
        return 0
        
    class askUserInstallDialog(tkinter.simpledialog.Dialog):
        """
        dialog for system file manipulation of linux systems
        """
        
        def __init__(self,master,title=None):
            if not title:
                title="System Configuration"
            tkinter.simpledialog.Dialog.__init__(self,master,title)
            
        def body(self, master):
            """
            """
            row=0
            # install prefix question
            tkinter.Label(master, text="Install Gato to another place?").grid(row=row,column=0)
            self.installQ = tkinter.IntVar()
            self.installQ.set(1)
            tkinter.Radiobutton(master, text="Yes", variable=self.installQ, value=1,
                                command=self.enablePathEntry).grid(row=row,column=1)
            tkinter.Radiobutton(master, text="No",  variable=self.installQ, value=2,
                                command=self.disablePathEntry).grid(row=row,column=2)
            
            # install location
            row+=1
            self.installP=tkinter.Entry(master)
            self.installP.insert(0,os.path.expanduser("~/bin"))
            self.installP.rowLocation=row
            self.installP.colLocation=0
            self.installP.grid(row=row,column=0,sticky=tkinter.EW)
            self.searchP=tkinter.Button(master,text="search...",
                                        command=self.askInstallPrefix,
                                        pady=0)
            self.searchP.grid(row=row,column=1,columnspan=2)
            
            # mime type reg?
            row+=1
            tkinter.Label(master, text="add gato mime type").grid(row=row,column=0)
            self.mimeQ = tkinter.IntVar()
            self.mimeQ.set(1)
            tkinter.Radiobutton(master, text="Yes", variable=self.mimeQ,
                                value=1).grid(row=row,column=1)
            tkinter.Radiobutton(master, text="No",  variable=self.mimeQ,
                                value=2).grid(row=row,column=2)
            
            # mime type reg?
            row+=1
            tkinter.Label(master, text="add gato to .mailcap").grid(row=row,column=0)
            self.mailcapQ = tkinter.IntVar()
            self.mailcapQ.set(1)
            tkinter.Radiobutton(master, text="Yes", variable=self.mailcapQ,
                                value=1).grid(row=row,column=1)
            tkinter.Radiobutton(master, text="No",  variable=self.mailcapQ,
                                value=2).grid(row=row,column=2)
            
        def enablePathEntry(self):
            self.installP.grid(row=self.installP.rowLocation,column=self.installP.colLocation,sticky=tkinter.EW)
            self.searchP["state"]=tkinter.NORMAL
            
        def disablePathEntry(self):
            self.installP.grid_forget()
            self.searchP["state"]=tkinter.DISABLED
            
        def askInstallPrefix(self):
            """
            command for search button
            """
            initDir=self.installP.get()
            newPrefix=""
            if os.path.exists(initDir):
                newPrefix=tkinter.filedialog.askdirectory(parent=self,initialdir=initDir,mustexist=1)
            else:
                newPrefix=tkinter.filedialog.askdirectory(parent=self,mustexist=1)                
            if newPrefix:
                self.installP.delete(0, tkinter.END)
                self.installP.insert(0, newPrefix)
                
        def apply(self):
            """
            return result as dictionary
            """
            self.result={}
            if (hasattr(self,"installP") and 
                hasattr(self,"installQ") and
                (self.installQ.get()==1)):
                self.result["installTo"]=self.installP.get()
            else:
                self.result["installTo"]=None
            if hasattr(self,"mimeQ"):
                self.result["mimeQ"]=self.mimeQ.get()==1
            if hasattr(self,"mailcapQ"):
                self.result["mailcapQ"]=self.mailcapQ.get()==1
                
    def askUserInstall(self):
        """
        """
        self.askedUser=self.askUserInstallDialog(self.DialogMaster).result
        return self.askedUser
        
    class askUserUninstallDialog(tkinter.simpledialog.Dialog):
        """
        dialog for system file manipulation of linux systems
        """
        def __init__(self,master,title=None):
            if not title:
                title="System Configuration"
            tkinter.simpledialog.Dialog.__init__(self,master,title)
            
        def body(self, master):
            """
            Are you sure...? Dialog...
            """
            row=0
            # install prefix question
            tkinter.Label(master,
                          text="Install Gato from\n%s ?"%self.myExecutable
                          ).grid(row=row,column=0)
            
        def apply(self):
            """
            return result as dictionary
            """
            self.result={}
            
    def askUserUninstall(self):
        self.askedUser=self.askUserUnnstallDialog(self.DialogMaster).result
        return self.askedUser
        
    def configureSystem(self):
        """
        """
        if self.askedUser.get("installTo",0):
            self.installBinary(self.askedUser["installTo"])
        if not self.cache_check_mailcap and self.askedUser.get("mailcapQ",0):
            self.configure_mailcap()
        if not self.cache_check_mime_types and self.askedUser.get("mimeQ",0):
            self.configure_mime_types()
            
    def configure_mailcap(self):
        """
        append my mime type to .mailcap
        """
        savedLines=""
        # if this file exists
        if os.access(self.mailcapFile,os.R_OK):
            mailcap=file(self.mailcapFile,"r")
            
            while 1:
                line=mailcap.readline()
                savedLine=line[:]
                # line end
                if not line:
                    break
                    
                    # skip comments
                if line[0]=="#":
                    savedLines+=line
                    continue
                    
                line=line.strip()
                continuedLines=[]
                while line[-1]=="\\":
                    continuedLines.append(savedLine)
                    savedLine=mailcap.readline()
                    line=line[:-1]+savedLine.rstrip()
                entries=line.split(";")
                (mimeType,viewCommand)=list(map(string.strip,entries[:2]))
                
                # skip my old entry
                if mimeType==gatoMimeType:
                    continue
                    
                savedLines+= "".join(continuedLines)+savedLine
            mailcap.close()
            # open for write access
        mailcap=file(self.mailcapFile,"w")
        mailcap.write(savedLines)
        mailcap.write("%s;%s \"%%s\"\n"%(gatoMimeType,self.myExecutable))
        mailcap.close()
        
    def configure_mime_types(self):
        """
        append my information to .mime.types
        """
        savedLines=""
        # if this file exists
        if os.access(self.mime_typesFile,os.R_OK):
            mime_types=file(self.mime_typesFile,"r")
            
            while 1:
                line=mime_types.readline()
                savedLine=line[:]
                # line end
                if not line:
                    break
                    
                    # skip comments
                if line[0]=="#":
                    savedLines+=line
                    continue
                    
                line=line.strip()
                continuedLines=[]
                while line[-1]=="\\":
                    continuedLines.append(savedLine)
                    savedLine=mime_types.readline()
                    line=line[:-1]+savedLine.rstrip()
                entries=line.split(";")
                
                mime_dict={}
                # format: key=value or key="value"
                kv_pair=re.compile("(\w+)=((?:\"[^\"]*\")|(?:[^\"\s]*))")
                kv_pairs=kv_pair.findall(line)
                for kv in kv_pairs:
                    (key,value)=kv
                    if value[0]=="\"":
                        value=value[1:-1]
                    mime_dict[key]=value
                if (mime_dict.get("type")==gatoMimeType and
                    mime_dict.get("exts")==gatoFileExtension):
                    continue
                    
                savedLines+="".join(continuedLines)+savedLine
            mime_types.close()
        else:
            # fake Netscape MIME file
            savedLines+="#--Netscape Communications Corporation MIME Information\n"
            # open for write access
        mime_types=file(self.mime_typesFile,"w")
        mime_types.write(savedLines)
        mime_types.write("# inserted by gato SystemConfiguration Module\n")
        mime_types.write("type=%s  \\\ndesc=\"%s\"  \\\nexts=\"%s\"\n"%
                         (gatoMimeType,gatoDescription,gatoFileExtension))
        mime_types.close()
        
        
class configureLinux(configureUNIX):
    """
    """
    def __init__(self, DialogMaster=None):
        if sys.platform[:5]!='linux':
            raise ConfigurationException("tried to instantiate %s on %s"%
                                         (self.__class__.__name__,sys.platform))
        configureUNIX.__init__(self,DialogMaster)
        
class configureSUNOS(configureUNIX):
    """
    """
    def __init__(self, DialogMaster=None):
        if sys.platform[:5]!='sunos':
            raise ConfigurationException("tried to instantiate %s on %s"%
                                         (self.__class__.__name__,sys.platform))
        configureUNIX.__init__(self,DialogMaster)
        
class configureWindows(configureOS):
    """
    Configuration module for windows
    contaminates the windows registry with our
    extension, program and mime type
    """
    
    def __init__(self,DialogMaster=None):
        """
        find script location...
        """
        configureOS.__init__(self,DialogMaster)
        
    def check(self):
        """
        """
        self.ClassesSection=self.findWritableClassesSection()
        return 0
        
    class askUserInstallDialog(tkinter.simpledialog.Dialog):
        """
        """
        def __init__(self,master,title=None):
            if not title:
                title="System Configuration"
            tkinter.simpledialog.Dialog.__init__(self,master,title)
            
        def body(self, master):
            """
            dialog body
            """
            row=0
            # install question
            tkinter.Label(master, text="Install Gato.exe to another place?").grid(row=row,column=0)
            self.installQ = tkinter.IntVar()
            self.installQ.set(1)
            tkinter.Radiobutton(master, text="Yes", variable=self.installQ, value=1, command=self.enablePathEntry).grid(row=row,column=1)
            tkinter.Radiobutton(master, text="No",  variable=self.installQ, value=2, command=self.disablePathEntry).grid(row=row,column=2)
            # install location
            row+=1
            self.installP=tkinter.Entry(master)
            self.installP.insert(0,"C:\\Gato\\")
            self.installP.rowLocation=row
            self.installP.colLocation=0
            self.installP.grid(row=row,column=0,sticky=tkinter.EW)
            self.searchP=tkinter.Button(master,text="search...",command=self.askInstallPrefix, pady=0)
            self.searchP.grid(row=row,column=1,columnspan=2)
            # extension question
            row+=1
            self.extensionQ = tkinter.IntVar()
            self.extensionQ.set(1)
            tkinter.Label(master, text="Create bindings to .%s file extensions:"%gatoFileExtension).grid(row=row)
            tkinter.Radiobutton(master, text="Yes", variable=self.extensionQ, value=1).grid(row=row,column=1)
            tkinter.Radiobutton(master, text="No",  variable=self.extensionQ, value=2).grid(row=row,column=2)
            # MIME type question
            row+=1
            self.mimeQ = tkinter.IntVar()
            self.mimeQ.set(1)
            tkinter.Label(master, text="Register MIME type %s:"%gatoMimeType).grid(row=row)
            tkinter.Radiobutton(master, text="Yes", variable=self.mimeQ, value=1).grid(row=row,column=1)
            tkinter.Radiobutton(master, text="No",  variable=self.mimeQ, value=2).grid(row=row,column=2)
            
        def apply(self):
            """
            return result as dictionary
            """
            self.result={}
            if (hasattr(self,"installP") and 
                hasattr(self,"installQ") and
                (self.installQ.get()==1)):
                self.result["installTo"]=self.installP.get()
            else:
                self.result["installTo"]=None
            if hasattr(self,"mimeQ"):
                self.result["mimeQ"]=self.mimeQ.get()==1
            if hasattr(self,"extensionsQ"):
                self.result["extensionsQ"]=self.extensionsQ.get()==1
                
        def enablePathEntry(self):
            self.installP.grid(row=self.installP.rowLocation,column=self.installP.colLocation,sticky=tkinter.EW)
            self.searchP["state"]=tkinter.NORMAL
            
        def disablePathEntry(self):
            self.installP.grid_forget()
            self.searchP["state"]=tkinter.DISABLED
            
        def askInstallPrefix(self):
            """
            command for search button
            """
            initDir=self.installP.get()
            newPrefix=""
            if os.path.exists(initDir):
                newPrefix=tkinter.filedialog.askdirectory(parent=self,initialdir=initDir,mustexist=1)
            else:
                newPrefix=tkinter.filedialog.askdirectory(parent=self,mustexist=1)                
            if newPrefix:
                self.installP.delete(0, tkinter.END)
                self.installP.insert(0, newPrefix)
                
    def askUserInstall(self):
        """
        """
        self.askedUser=self.askUserInstallDialog(self.DialogMaster).result
        return self.askedUser
        
    def configureSystem(self):
        """
        do the system configuration
        """
        if self.askedUser.get("installTo",0):
            self.installBinary(self.askedUser["installTo"])
        if self.askedUser.get("extensionQ",0) or self.askedUser.get("mimeQ",0):
            self.insertGatoEntries(self.ClassesSection)
            
    def printGatoEntries(self):
        """
        start reading...
        """
        reader=winreg.ConnectRegistry(None,winreg.HKEY_CLASSES_ROOT)
        # get Gato.File section
        GatoFileHandle=None
        try:
            GatoFileHandle=winreg.OpenKey(reader,"Gato.File")
        except WindowsError:
            logging.error("Could not find Gato.File section")
        else:
            print(logging.info("found Gato.File section:"))
            self.printSubRegistry(GatoFileHandle)
            
            # get Gato FileExtension Section
        GatoExtensionHandle=None
        try:
            GatoExtensionHandle=winreg.OpenKey(reader,"."+gatoFileExtension)
        except WindowsError:
            logging.error("could not find the file extension .%s" % gatoFileExtension)
        else:
            logging.info("found gato's extension")
            self.printSubRegistry(GatoExtensionHandle)
            
            # get Gato mime Type section
        GatoMimeHandleGatoExt=None
        try:
            GatoMimeHandle=winreg.OpenKey(reader,"MIME")
            GatoMimeHandleDatabase=winreg.OpenKey(GatoMimeHandle,
                                                    "Database")
            GatoMimeHandleContentType=winreg.OpenKey(GatoMimeHandleDatabase,
                                                      "Content Type")
            GatoMimeHandleGatoExt=winreg.OpenKey(GatoMimeHandleContentType,
                                                  gatoMimeType)
        except WindowsError:
            logging.error("could not find mime type: %s" % gatoMimeType)
        else:
            logging.info("found %s mime type"%gatoMimeType)
            self.printSubRegistry(GatoMimeHandleGatoExt)
            
    def printSubRegistry(self,key,indent=""):
        """
        print all information of a subkey
        """
        subkeyNo,valueNo,lastMod=winreg.QueryInfoKey(key)
        for i in range(valueNo):
            logging.debug("%s %s" % (indent, winreg.EnumValue(key, i)))
        for i in range(subkeyNo):
            subkeyName=winreg.EnumKey(key,i)
            subkey=winreg.OpenKey(key,subkeyName)
            logging.debug("%s %s" % (indent, winreg.EnumValue(key, i)))
            self.printSubRegistry(subkey,indent+"  ")
            
    def findWritableClassesSection(self):
        # first try in HKEY_CLASSES_ROOT
        try:
            writer=winreg.ConnectRegistry(None,winreg.HKEY_CLASSES_ROOT)
            GatoFileTestHandle=winreg.CreateKey(writer,"Gato.File.Test")
            winreg.DeleteKey(writer,"Gato.File.Test")
            return writer
        except WindowsError:
            # print "could not access HKEY_CLASSES_ROOT/Gato.File"
            # self.traceback.print_exc()
            pass
            # next try...
        try:
            writer=winreg.ConnectRegistry(None,winreg.HKEY_CURRENT_USER)
            SoftwareSection=winreg.OpenKey(writer,"Software")
            ClassesSection=winreg.OpenKey(SoftwareSection,"Classes",0,winreg.KEY_SET_VALUE)
            GatoFileTestHandle=winreg.CreateKey(ClassesSection,"Gato.File.Test")
            winreg.DeleteKey(ClassesSection,"Gato.File.Test")
            return ClassesSection
        except WindowsError:
            # print "could not access HKEY_CURRENT_USER/Software/Classes Section"
            # self.traceback.print_exc()
            return None
            
    def insertGatoEntries(self,ClassesSection):
        """
        updates registry database
        """
        # update Gato.File section
        try:
            GatoFileHandle=winreg.CreateKey(ClassesSection,"Gato.File")
            winreg.SetValueEx(GatoFileHandle,"",0,winreg.REG_SZ,"Gato.File")
        except WindowsError:
            logging.error("Could not create/update the Gato.File section")
            self.traceback.print_exc()
            
            # update Gato.File's subsections
        try:
            GatoShellHandle=winreg.CreateKey(GatoFileHandle,"shell")
            GatoOpenHandle=winreg.CreateKey(GatoShellHandle,"open")
            GatoOpenCommandHandle=winreg.CreateKey(GatoOpenHandle,"command")
            winreg.SetValueEx(GatoOpenCommandHandle,"",0,winreg.REG_SZ,self.myExecutable+' "%1"')
        except WindowsError:
            logging.error("could not install open command for gato")
            self.traceback.print_exc()
            
            # update .gato section    
        try:
            GatoExtensionHandle=winreg.CreateKey(ClassesSection,"."+gatoFileExtension)
            winreg.SetValueEx(GatoExtensionHandle,"",0,winreg.REG_SZ,"Gato.File")
            winreg.SetValueEx(GatoExtensionHandle,"Content Type",0,winreg.REG_SZ,gatoMimeType)
        except WindowsError:
            logging.error("could not create/update FileExtension section")
            self.traceback.print_exc()
            
            # access MIME Database section
        MimeContentTypeSection=None
        try:
            MimeSection=winreg.CreateKey(ClassesSection,"MIME")
            MimeDatabaseSection=winreg.CreateKey(MimeSection,"Database")
            MimeContentTypeSection=winreg.CreateKey(MimeDatabaseSection,"Content Type")
        except WindowsError:
            logging.error("could not access MIME Content Type database")
            self.traceback.print_exc()
            return
            # update gato's mime type
        try:
            GatoMimeContentTypeHandle=winreg.CreateKey(MimeContentTypeSection,gatoMimeType)
            winreg.SetValueEx(GatoMimeContentTypeHandle,"Extension",0,
                                    winreg.REG_SZ,"."+gatoFileExtension)
        except WindowsError:
            logging.error("could not update the gato MIME section")
            self.traceback.print_exc()
            
class GatoInstaller(object):
    """
    A instance of this class reflects the installation capabilities and status.
    It should be instantiated only once.
    """
    instanceCounter=0
    
    def __init__(self,disabled=0,menu=None,index=tkinter.END):
        """
        gets system configurator and checks state
        """
        # assure singleton
        if GatoInstaller.instanceCounter!=0:
            raise ConfigurationException("class GatoInstaller should be instantiated once.")
        GatoInstaller.instanceCounter+=1
        self.disabled=disabled
        self.menu=menu
        self.index=index
        # set if no menu item should appear
        if self.disabled:
            return
        self.SysConfig=self.getConfigurator()
        self.state=self.SysConfig.check()
        
    def __del__(self):
        """
        clean up and decrement
        """
        GatoInstaller.instanceCounter-=1
        
    def enable(self):
        self.disabled=0
        self.SysConfig=getConfigurator()
        self.state=self.SysConfig.check()
        if self.menu != None:
            self.insertMenuEntry()
            
    def disable(self):
        self.disabled=1
        self.removeMenuEntry()
        
    def addMenuEntry(self,menu,index=tkinter.END):
        self.menu=menu
        self.index=menu.index(index) # make absolute position
        if self.disabled:
            return
        self.insertMenuEntry()
        
    def insertMenuEntry(self):
        if self.menu is None:
            return
        self.menu.insert_command(self.index)
        self.configureMenuEntry()
        
    def removeMenuEntry(self):
        if self.menu is None:
            return
        self.menu.delete(self.index)
        
    def configureMenuEntry(self):
        if self.menu is None:
            return
        if self.state:
            self.menu.entryconfig(self.index,
                                  command=self.uninstallCommand,
                                  label='Uninstall Gato'
                                  )
        else:
            self.menu.entryconfig(self.index,
                                  command=self.installCommand,
                                  label='Install Gato...')
            
    def installCommand(self):
        self.SysConfig.runInstall()
        self.state=self.SysConfig.check()
        self.configureMenuEntry()
        
    def uninstallCommand(self):
        logging.info("uninstall")
        self.state=self.SysConfig.check()
        self.configureMenuEntry()
        
    def getConfigurator(self):
        if sys.platform[:5]=="linux":
            return configureLinux()
        elif sys.platform=="win32":
            return configureWindows()
        elif sys.platform[:5]=="sunos":
            return configureSUNOS()
        else:
            return configureUnsupported()
            
if __name__=="__main__":
    i=GatoInstaller()
    
    
    
    
