#!/usr/bin/env python
################################################################################
#
#       This file is part of Gato (Graph Algorithm Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/~gato
#
#	file:   ProbEditorBasics.py
#	author: Achim Gaedke (achim.gaedke@zpr.uni-koeln.de)
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
#       This file is version $Revision$ 
#                       from $Date$
#             last change by $Author$.
#
################################################################################

import string

def key_to_tag(key):
    i=string.find(key,'_')
    while i!=-1:
        key=key[:i]+'/'+key[i:]
        i=string.find(key,'_',i+2)
    i=string.find(key,' ')
    while i!=-1:
        key=key[:i]+'_'+key[i+1:]
        i=string.find(key,' ',i+1)
    return key

def tag_to_key(tag):
    i=string.find(tag,'_')
    while i!=-1:
        if i>0 and tag[i-1]=='/':
            tag=tag[:i-1]+tag[i:]
        else:
            tag=tag[:i]+' '+tag[i+1:]
            i+=1
        i=string.find(tag,'_',i)
    return tag

import UserDict

class ProbDict(UserDict.UserDict):
    """
    Dictionary with a cached sum
    """
    def __init__(self,data=None):
        self.sum=0
        UserDict.UserDict.__init__(self,data)

    def cmp_prob_val(self,a,b):
        if self[a]==self[b]:
            return cmp(a,b)
        else:
            return cmp(self[b],self[a])

    def __setitem__(self,a,b):
        if self.has_key(a):
            self.sum=self.sum-self[a]
        self.sum=self.sum+b
        UserDict.UserDict.__setitem__(self,a,b)

    def __delitem__(self,a):
        self.sum=self.sum-self.data[a]
        UserDict.UserDict.__delitem__(self,a)

    def clear(self):
        self.sum=0
        UserDict.UserDict.clear(self)

    def update(self,dict):
        UserDict.UserDict.update(self,dict)
        self.__calc_sum__()

    def setdefault(self,key,failobj=0):
        if not self.has_key(key):
            self[key] = failobj
        return self[key]

    def get(self, key, failobj=0):
        return self.data.get(key, failobj)

    def __calc_sum__(self):
        self.sum=0
        for v in self.values():
            self.sum=self.sum+v

    def __repr__(self):
        return repr([self.data,self.sum])

    def renorm_to(self,sum):
        "renorm all items to given argument"
        self.__calc_sum__()
        factor=sum/self.sum
        for key in self.data.keys():
            self.data[key]*=factor
        self.__calc_sum__()


#####################################################################################

class emission_change:
    """
    base class for change notices
    """
    def __init__(self,sender,data):
        self.sender=sender
        self.data=data
        self.next_change=None
        self.previous_change=None

    def __repr__(self):
        return '<emission_change>'

class emission_change_color(emission_change):
    """
    only color is changed
    """
    
    def __init__(self,sender,data,color_list):
        emission_change.__init__(self,sender,data)
        self.color_list=color_list

    def __repr__(self):
        return '<emission_change_color '+repr(self.color_list)+'>'


class emission_change_order(emission_change):
    """
    only order is changed
    """
    
    def __init__(self,sender,data,order_list):
        emission_change.__init__(self,sender,data)
        self.order_list=order_list

    def __repr__(self):
        return '<emission_change_order '+repr(self.order_list)+'>'

class emission_change_data(emission_change):
    """
    only data are changed
    """

    def __init__(self,sender,data,dict):
        emission_change.__init__(self,sender,data)
        self.dict=dict

    def __repr__(self):
        return '<emission_change_data '+repr(self.dict)+'>'

#####################################################################################

class emission_data:
    """
    emission data and display data shared by many editors
    contains:

    - probabilities in ProbDict

    - precision

    - constraints to sum (self.fixed_sum<=0: no constraints)

    - color index for each value
    """
    def __init__(self,emissions, color_list=None):
        self.viewer_list=[]
        self.emissions=emissions
        self.precision=1e-7
        self.fixed_sum=0.0
        if color_list is None:
            self.color_list=['red','green','yellow','blue','black',
                             'grey','orange','pink','gold','brown',
                             'tan','purple','magenta','firebrick','deeppink',
                             'lavender','NavajoWhite','seagreen','violet','LightGreen']
        else:
            self.color_list=color_list
        self.order_list=emissions.keys()
        self.order_list.sort(emissions.cmp_prob_val)

    def register_viewer(self,data_viewer):
        self.viewer_list.append(data_viewer)
        return len(self.viewer_list)-1

    def remove_viewer(self,data_viewer):
        i=self.viewer_list.index(data_viewer)
        del self.viewer_list[i]
        return i

    def recieve_change(self,change):

        if self.fixed_sum<=0 or abs(self.fixed_sum-self.emissions.sum)<self.precision:
            # inform all but calling viewer about changes
            for v in self.viewer_list:
                if change.sender!=v:
                    v.recieve_change(change)
        else:
            # renorm the entries
            self.emissions.renorm_to(self.fixed_sum)
            change.dict=self.emissions.data
            # inform all about changes
            for v in self.viewer_list:
                v.recieve_change(change)
                    

#####################################################################################

class emission_editor:
    """
    client of emission_data, recieves update messages and sends updates
    """
    def __init__(self,data):
        self.data=data
        self.data.register_viewer(self)

    def __del__(self):
        self.data.remove_viewer(self)

    def recieve_change(self,change):
        # print 'recieved '+repr(change)
        pass

    def send_change(self,change):
        change.data.recieve_change(change)
