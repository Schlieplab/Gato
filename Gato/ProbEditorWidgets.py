#!/usr/bin/env python
################################################################################
#
#       This file is part of Gato (Graph Algorithm Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/~gato
#
#	file:   ProbEditorWidgets.py
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

import math
import Tkinter
import ProbEditorBasics

class scroll_canvas(Tkinter.Canvas):
    """
    should avoid resizing by adding or removing scrollbars in x or y-direction or both
    """

    def __init__(self,master,cnf={},**kw):
                #hidden frame
        self.hidden_frame=Tkinter.Frame(master)
        self.hidden_frame.rowconfigure(0,weight=1)
        self.hidden_frame.columnconfigure(0,weight=1)

        cnf=Tkinter._cnfmerge((cnf,kw))
        if not cnf.has_key('highlightthickness'):
            cnf['highlightthickness']=0
        Tkinter.Canvas.__init__(self,self.hidden_frame,cnf)

        Tkinter.Canvas.grid(self,row=0,column=0,sticky=Tkinter.NSEW)
        self.hidden_frame.bind('<Configure>',self.config_event)
        # prepare scrollbars
        self.sb_y=Tkinter.Scrollbar(self.hidden_frame,
                                    orient=Tkinter.VERTICAL,
                                    command=self.yview)
        self.sb_x=Tkinter.Scrollbar(self.hidden_frame,
                                    orient=Tkinter.HORIZONTAL,
                                    command=self.xview)
        Tkinter.Canvas.configure(self,
                                 yscrollcommand=self.sb_y.set,
                                 xscrollcommand=self.sb_x.set)

    def config_event(self,event):
        # returns empty list, if no scrollregion exists
        scrollr=Tkinter.Canvas.cget(self,'scrollregion')
        if scrollr:
            # print "from config",scrollr
            scrollr=map(int,scrollr.split())
        else:
            # print "from bbox"
            scrollr=self.bbox(Tkinter.ALL)
            self.configure(scrollregion=scrollr)
##        print "event: widht %d, height %d"%(event.width,event.height)
##        print "scrollregion: ",scrollr
##        print "winfo: widht %d, height %d"%(self.c.winfo_width(),
##                                            self.c.winfo_height())
##        print "winfo req: widht %d, height %d"%(self.c.winfo_reqwidth(),
##                                                self.c.winfo_reqheight())
        if event.width>=(scrollr[2]-scrollr[0]):
            # print "x_scrollbar away"
            self.sb_x.grid_remove()
        else:
            # print "x_scrollbar needed"
            self.sb_x.grid(row=1,column=0,sticky=Tkinter.EW)

        if event.height>=(scrollr[3]-scrollr[1]):
            # print "y_scrollbar away"
            self.sb_y.grid_remove()
        else:
            # print "y_scrollbar needed"
            self.sb_y.grid(row=0,column=1,sticky=Tkinter.NS)

        # hidden definitions for geometry methods
        
    def pack_configure(self, cnf={}, **kw):
        cnf=Tkinter._cnfmerge((cnf,kw))
        return self.hidden_frame.pack(cnf)
    pack = pack_configure

    def pack_forget(self):
        return self.hidden_frame.pack_forget()
    forget = pack_forget

    def pack_info(self):
        return self.hidden_frame.pack_info()

    def place_configure(self, cnf={}, **kw):
        cnf=Tkinter._cnfmerge((cnf,kw))
        return self.hidden_frame.place(cnf=cnf)
    place = place_configure

    def place_forget(self):
        return self.hidden_frame.place_forget()
    forget = place_forget

    def place_info(self):
        return self.hidden_frame.place_info()
       
    def grid_configure(self, cnf={}, **kw):
        cnf=Tkinter._cnfmerge((cnf,kw))
        print cnf
        return self.hidden_frame.grid(cnf=cnf)
    grid = grid_configure

    def grid_forget(self):
        return self.hidden_frame.grid_forget()
    forget = grid_forget

    def grid_info(self):
        return self.hidden_frame.grid_info()

    def grid_location(self, x, y):
        return self.hidden_frame.grid_location(x,y)

    location = grid_location

class tab_frame(Tkinter.Frame):
    """
    tabbed widgets
    """
    def tab_selected(self,event):
        """
        event handler for tabs
        """
        selected_item=event.widget.find_withtag(Tkinter.CURRENT)[0]
        selected_tags=event.widget.gettags(selected_item)
        tab_name=filter(lambda t: t[:4]=='tab_',selected_tags)[0][9:]
        key=ProbEditorBasics.tag_to_key(tab_name)
        if key!=self.actual_tab:
            self.change_tab(key)

    def change_tab(self,key):
        """
        process of changing:
        
        - lifts actual tab
        
        - changes color of previous tab to background
        
        - actual tab is marked white

        - releases (forget) previous widget

        - pack actual widget
        """
        # change tabs
        if self.actual_tab!=None:
            poly_list=self.tabs.find_withtag(\
                'tab_poly_'+ProbEditorBasics.key_to_tag(self.actual_tab))
            for item in poly_list:
                self.tabs.itemconfigure(item,fill='')

        tag=ProbEditorBasics.key_to_tag(key)
        poly_list=self.tabs.find_withtag('tab_poly_'+tag)
        for item in poly_list:
            self.tabs.itemconfigure(item,fill='white')
            self.tabs.lift(item)
        text_list=self.tabs.find_withtag('tab_text_'+tag)
        for item in text_list:
            self.tabs.lift(item)
        
        # change body
        if self.actual_tab!=None:
            self.widget_dict[self.actual_tab].pack_forget()
        self.widget_dict[key].pack(side=Tkinter.BOTTOM,
                                   in_=self.container,
                                   expand=1,fill=Tkinter.BOTH)
        self.actual_tab=key

    def __init__(self,master,widget_dict,start=None,**config):
        """
        init frame, containing:

        - tabbs
        
        - frame with fixed width, height for switched widgets

        size from slaves is not propagated
        """
        Tkinter.Frame.__init__(self,master,config)

        self.lower()
        self.tabs=Tkinter.Canvas(self,height=25,highlightthickness=0)
        # why are sizes here?
        self.container=Tkinter.Frame(self,width=400,height=300)
        self.container.pack_propagate(0)

        self.widget_dict=widget_dict
        key_list=widget_dict.keys()
        key_list.sort()
        text_base_y=20
        pos_x=7
        margin_x=3
        margin_y=3
        text_anchor=Tkinter.SW
        for key in key_list:
            # Reiter malen
            # erst den Text
            tab_text=key
            tag=ProbEditorBasics.key_to_tag(key)
            text=self.tabs.create_text((pos_x,text_base_y),
                                       text=key,
                                       anchor=text_anchor,
                                       tags=('tab_text_'+tag))
            text_box=self.tabs.bbox(text)

            #dann den Rand:
            far_right=2000
            far_left=-1
            very_deep=2000
            tab=self.tabs.create_polygon((far_left,text_base_y,
                                          text_box[0]-2-margin_x,text_base_y,
                                          text_box[0]-2,text_box[1]-margin_y,
                                          text_box[2],text_box[1]-margin_y,
                                          text_box[2]+margin_x,text_base_y,
                                          far_right,text_base_y,
                                          far_right,very_deep,
                                          far_left,very_deep),
                                         fill='',
                                         outline='black',
                                         tags=('tab_poly_'+tag)
                                         )
            # Text nach oben
            self.tabs.lift(text)
            pos_x=pos_x+text_box[2]-text_box[0]+2*margin_x

            # Event-Handler
            self.tabs.tag_bind(text,'<Button-1>',self.tab_selected)
            self.tabs.tag_bind(tab,'<Button-1>',self.tab_selected)

        # setze aktuellen Tab
        self.actual_tab=None
        if start!=None:
            self.change_tab(start)
        else:
            self.change_tab(key_list[0])

        self.tabs.pack(side=Tkinter.TOP,fill=Tkinter.X)
        self.container.pack(side=Tkinter.TOP,expand=1,fill=Tkinter.BOTH)

#####################################################################################

class flyout_decoration:
    """
    works only with canvas derivatives
    """
    def __init__(self,info_function):
        """
        prepare bindings and store info-function
        """
        self.info_function=info_function
        # prepare bindings
        self.add_bindings(info_function)

    def add_bindings(self,info_function):
        """
        add bindings to canvas-items with 'flyout_info' tag
        """
        items=self.find_withtag(Tkinter.ALL)
        # init status
        self.flyout_stat=0
        # init id of after-timer
        self.after_id=0
        for item in items:
            key_tag=filter(lambda t:t=='flyout_info',self.gettags(item))
            if len(key_tag)==0: continue
            self.tag_bind(item,'<Enter>',self.flyout_enter,'+')
            self.tag_bind(item,'<Motion>',self.flyout_delay_start,'+')
            self.tag_bind(item,'<Leave>',self.flyout_leave,'+')

    def flyout_enter(self,event):
        """
        a item is entered, initialise status
        """
        # stat:
        # 0 no timer set, no flyout, after motion =>1
        # 1 timer set, no flyout, after motion =>1, no motion =>2
        # 2 flyout, no timer, after motion =>1
        if self.flyout_stat!=0:
            return
        self.flyout_stat=0
        self.after_id=0

    def flyout_leave(self,event):
        """
        the item is left:
        
        - cancel timer
        
        - hide flyout
        
        - reset status
        """
        if self.flyout_stat==1:
            self.after_cancel(self.after_id)
        if self.flyout_stat==2:
            self.flyout_hide()
        self.flyout_stat=0

    def flyout_delay_start(self,event):
        """
        mouse move over item:

        - store item

        - evtl. hide flyout and cancel previous timer
        
        - start new timer for move-timeout

        """
        item=self.find_withtag(Tkinter.CURRENT)[0]
        if self.flyout_stat==1:
            # moved again, no flyout set
            self.after_cancel(self.after_id)
        elif self.flyout_stat==2:
            # flyout set
            self.flyout_hide()
        # moved
        self.flyout_stat=1
        self.after_id=self.after(1000,self.flyout_delay_end,item,event.x,event.y)

    def flyout_delay_end(self,item,x,y):
        """
        after-event handler:
        
        no move occured, we can create a flyout
        """
        self.flyout_stat==2
        self.flyout_show(item,x,y)

    def flyout_show(self,item,x,y):
        """
        create the flyout, get info text from 'info_function'
        """
        self.flyout_stat=2
        text_x=self.canvasx(x)+15
        text_y=self.canvasy(y)+15
        flyout_text=self.info_function(item)
        text_item=self.create_text((text_x,text_y),text=flyout_text,tags=('flyout'),
                                   anchor=Tkinter.NW)
        self.create_rectangle(self.bbox(text_item),fill='khaki',tags=('flyout'))
        self.lift(text_item)

    def flyout_hide(self):
        """
        destroy flyout, reset state
        """
        self.flyout_stat=0
        flyout_elements=self.find_withtag('flyout')
        for element in flyout_elements:
            self.delete(element)

######################################################################################

class bar_chart_y(Tkinter.Canvas,flyout_decoration):
    """
    
    """
    def __init__(self,master,prob_dict,keys,colors,report_func=None):
        """
        
        """
        self.max_value=0
        self.max_key=None
        for k in keys:
            if prob_dict[k]>self.max_value:
                self.max_value=prob_dict[k]
                self.max_key=k

        self.bar_step=30
        self.bar_width=20
        self.text_length=30
        self.x_margin=10
        self.y_margin=10
        self.bar_length=350
        if self.max_value!=0:
            self.bar_factor=self.bar_length/self.max_value
        else:
            self.bar_factor=1.0
        Tkinter.Canvas.__init__(self,
                                master,
                                bg='white',
                                highlightthickness=0,
                                )
        self.create_description(prob_dict,keys)
        self.create_bars(prob_dict,keys,colors)
        self.report_func=None
        if report_func!=None:
            self.report_func=report_func
        self.config_bar_parameters(prob_dict)
        self.config_bar_height(prob_dict)
        flyout_decoration.__init__(self,self.info_func)
        self.bind('<Configure>',self.bars_configure)

    def info_func(self,item):
        tag=filter(lambda t:t[:4]=='tag_',self.gettags(item))[0]
        key=ProbEditorBasics.tag_to_key(tag[4:])
        bar=filter(lambda i,s=self:'bar' in s.gettags(i),self.find_withtag(tag))[0]
        coords=self.coords(bar)
        value=float(coords[2]-coords[0])/self.bar_factor
        if value>0:
            precision=-math.floor(math.log10(value))+3
        else:
            precision=1
        flyout_text=('%s: %s')%(key,str(round(value,precision)))
        return flyout_text

    def create_description(self,prob_dict,keys):
        text_anchor=Tkinter.W
        i=0
        self.text_length=0.0
        for k in keys:
            tag='tag_'+ProbEditorBasics.key_to_tag(k)
            pos_y=self.y_margin+i*self.bar_step
            text=self.create_text(self.x_margin,pos_y+self.bar_width/2,
                                  anchor=text_anchor,
                                  text=k,
                                  tags=('text',tag))
            text_box=self.bbox(text)
            this_length=abs(text_box[0]-text_box[2])
            if this_length>self.text_length:
                self.text_length=this_length
            i=i+1

    def create_bars(self,prob_dict,keys,colors):
        start_x=self.x_margin+self.text_length
        start_y=self.y_margin
        text_anchor=Tkinter.W
        i=0
        for k in keys:
            tag='tag_'+ProbEditorBasics.key_to_tag(k)
            pos_x=start_x
            pos_y=start_y+i*self.bar_step
            self.create_rectangle(pos_x,
                                  pos_y,
                                  pos_x,
                                  pos_y+self.bar_width,
                                  fill=colors[i],
                                  tags=('bar','flyout_info',tag))
            i=i+1

    def get_max_value(self):
        dict=self.get_bar_values()
        max_value=0.0
        max_key=''
        for k in dict.keys():
            if dict[k]>self.max_value:
                max_value=dict[k]
                max_key=k
        return (max_key,max_value)

    def get_bar_values(self,key_list=None):
        dict={}
        if not key_list:
            # return all keys
            bar_items=self.find_withtag('bar')
            for bar_item in bar_items:
                tags=self.gettags(bar_item)
                tag=filter(lambda t:'tag_'==t[:4],tags)[0][4:]
                key=ProbEditorBasics.tag_to_key(tag)
                coords=self.coords(bar_item)
                value=float(coords[2]-coords[0])/self.bar_factor
                dict.update({key:value})
        else:
            # return only keys in list
            for key in key_list:
                tag='tag_'+ProbEditorBasics.key_to_tag(key)
                items=self.find_withtag(tag)
                if len(items)==0: continue
                bar_item=filter(lambda i,s=self:'bar' in s.gettags(i),items)
                coords=self.coords(bar_item)
                value=float(coords[2]-coords[0])/self.bar_factor
                dict.update({key:value})
        return dict

    def bars_configure(self,event):
        actual_values=self.config_bar_parameters(width=event.width)
        self.update_bars(actual_values)

    def config_bar_parameters(self,prob_dict=None,width=None):
        # merge new values (if exist)
        actual_values=self.get_bar_values()
        if prob_dict!=None:
            for key in prob_dict.keys():
                if actual_values.has_key(key):
                    actual_values[key]=prob_dict[key]
        old_max=self.max_value
        # find new max value
        self.max_value=0.0
        self.max_key=''
        for key in actual_values.keys():
            if actual_values[key]>self.max_value:
                self.max_value=actual_values[key]
                self.max_key=key
        # expand bars (if necessary, fix to 100)
        if width!=None:
            self.bar_length=width-self.text_length-2*self.x_margin
        if self.bar_length<100:
            self.bar_length=100
        # decide to change scale
        if self.max_value*self.bar_factor>self.bar_length or \
           self.max_value*self.bar_factor<self.bar_length/2.0:
            # scale change, if it is rational
            if self.max_value!=0:
                self.bar_factor=self.bar_length/self.max_value
                if self.report_func!=None:
                    self.report_func('scale change',None,None)
        else:
            # no scale change
            actual_values=prob_dict
        return actual_values

    def config_bar_height(self,prob_dict):
        # do real work
        if prob_dict==None: return
        for key in prob_dict.keys():
            tag='tag_'+ProbEditorBasics.key_to_tag(key)
            items=self.find_withtag(tag)
            if len(items)==0: continue
            bar_item=filter(lambda i,s=self:'bar' in s.gettags(i),items)
            coords=self.coords(bar_item)
            self.coords(bar_item,coords[0],coords[1],
                        coords[0]+prob_dict[key]*self.bar_factor,coords[3])

    def config_bar_color(self,keys,color_list):
        bar_items=self.find_withtag('bar')
        for item in bar_items:
            tag=filter(lambda t:t[:4]=='tag_',self.gettags(item))[0][4:]
            key=ProbEditorBasics.tag_to_key(tag[4:])
            color=color_list[keys.index(key)]
            self.itemconfig(item,fill=color)

    def config_bar_order(self,keys):
        text_x=self.bar_width/2
        start_y=self.y_margin
        i=0
        for k in keys:
            tag='tag_'+ProbEditorBasics.key_to_tag(key)
            items=self.find_withtag(tag)
            if len(items)!=1:
                continue
            bar_item=filter(lambda i,s=self:s.type(i)=='rectangle',items)
            text_item=filter(lambda i,s=self:s.type(i)=='text',items)
            pos_y=start_y+i*self.bar_step
            bar_coords=self.coords(bar_item)
            self.coords(bar_item,
                        bar_coords[0],
                        pos_y,
                        bar_coords[2],
                        pos_y+self.bar_width)
            text_coords=self.coords(text_item)
            self.coords(text_item,text_coords[0],pos_y+text_y)
            i=i+1

#######################################################################################

class e_bar_chart_y(bar_chart_y):

    def __init__(self,master,prob_dict,keys,colors,report_func):
        bar_chart_y.__init__(self,master,prob_dict,keys,colors)
        # report value changes to this function
        self.report_func=report_func
        self.normal_cursor=self.cget('cursor')
        self.current_item=None
        self.create_handles()
        flyout_decoration.add_bindings(self,self.info_func)
        self.config_handle_pos(prob_dict)

    def create_handles(self):
        for item in self.find_withtag('bar'):
            coords=self.coords(item)
            tags=self.gettags(item)
            tag=filter(lambda tag: tag[:4]=='tag_',tags)[0]
            handle=self.create_rectangle((coords[2],coords[1],coords[2],coords[3]),
                                         fill='black',
                                         tags=('bar_top','flyout_info',tag))
            self.tag_bind(handle,'<Button-1>',self.handle_mouse_move_start)
            self.tag_bind(handle,'<Enter>',self.change_cursor)
            self.tag_bind(handle,'<Leave>',self.restore_cursor)

    def info_func(self,item):
        tags=self.gettags(item)
        if 'bar_top' in tags:
            tag=filter(lambda t:t[:4]=='tag_',tags)[0]
            key=ProbEditorBasics.tag_to_key(tag[4:])
            coords=self.coords(item)
            value=self.value_from_handle_coords(coords)
            if value>0:
                precision=-math.floor(math.log10(value))+3
            else:
                precision=1
            flyout_text=('%s: %s')%(key,str(round(value,precision)))
        else:
            flyout_text=bar_chart_y.info_func(self,item)
        return flyout_text

    def change_cursor(self,event):
        self.on_handle=1
        event.widget.configure(cursor='sb_h_double_arrow')

    def restore_cursor(self,event):
        self.on_handle=0
        if self.current_item==None:
            event.widget.configure(cursor=self.normal_cursor)

    def value_from_handle_coords(self,coords):
        return float((coords[2]+coords[0])/2.0-self.x_margin-self.text_length)/self.bar_factor

    def handle_mouse_move_start(self,event):
        #count moves since region of maximum value
        self.move_above=1
        #count moves since maximum position
        self.move_beneath=1
        #cache information
        self.current_item=self.find_withtag(Tkinter.CURRENT)[0]
        tags=self.gettags(self.current_item)
        self.current_tag=filter(lambda tag: tag[:4]=='tag_',tags)[0]
        self.current_key=ProbEditorBasics.tag_to_key(self.current_tag[4:])

        values=self.get_bar_values()
        # for undo function
        self.report_func('old value',self.current_key,values[self.current_key])

        #find maximum value, except own value
        keys=values.keys()
        keys.remove(self.current_key)
        self.other_max=0.0
        for key in keys:
            if values[key]>self.other_max:
                self.other_max=values[key]
        
        #bind necessary motion-functions
        self.bind('<ButtonRelease-1>',self.handle_mouse_move_end)
        self.bind('<B1-Motion>',self.handle_mouse_move)

    def handle_mouse_move(self,event):
        x=self.canvasx(event.x)
        new_value=float(x-self.x_margin-self.text_length)/self.bar_factor
        upper_value=float(self.bar_length)/self.bar_factor
        if new_value<upper_value:
            self.move_beneath+=1
        if new_value>self.other_max:
            self.move_above+=1

        if new_value<=0:
            new_value=0
        elif new_value>upper_value:
            new_value=upper_value
            if self.move_beneath>0:
                actual_values=self.get_bar_values()
                self.bar_factor/=1.4142135623730951
                self.config_bar_height(actual_values)
                self.report_func('scale change',None,None) 
            self.move_beneath=0
        elif new_value<self.other_max*0.9 and \
             self.bar_factor!=self.bar_length/self.other_max:
            if self.move_above>0:
                actual_values=self.get_bar_values()
                self.bar_factor*=1.4142135623730951
                if self.bar_factor>self.bar_length/self.other_max:
                    self.bar_factor=self.bar_length/self.other_max
                self.config_bar_height(actual_values)
                self.report_func('scale change',None,None) 
            self.move_above=0
        self.config_handle_pos({self.current_key:new_value})
        self.report_func('move',self.current_key,new_value)

    def handle_mouse_move_end(self,event):
        self.unbind('<ButtonRelease-1>')
        self.unbind('<B1-Motion>')
        coords=self.coords(self.current_item)
        new_value=self.value_from_handle_coords(coords)
        self.config_bar_height({self.current_key:new_value})
        self.report_func('new value',self.current_key,new_value)
        self.current_item=None
        if self.on_handle==0:
            event.widget.configure(cursor=self.normal_cursor)

    def config_handle_pos(self,prob_dict):
        if prob_dict==None: return
        for key in prob_dict.keys():
            tag='tag_'+ProbEditorBasics.key_to_tag(key)
            items=self.find_withtag(tag)
            bar_item=filter(lambda i,s=self:'bar_top' in s.gettags(i),items)
            if len(bar_item)==0: continue
            coords=self.coords(bar_item)
            pos_x=self.x_margin+self.text_length+prob_dict[key]*self.bar_factor
            self.coords(bar_item,
                        pos_x-1,
                        coords[1],
                        pos_x+1,
                        coords[3])

    def config_bar_height(self,prob_dict):
        bar_chart_y.config_bar_height(self,prob_dict)
        self.config_handle_pos(prob_dict)

    def update_bars(self,prob_dict):
        actual_values=self.config_bar_parameters(prob_dict)
        self.config_bar_height(actual_values)

####################################################################################

class scale(Tkinter.Canvas):
        
    def __init__(self,master,start_x,factor,max_value=None):
        Tkinter.Canvas.__init__(self,
                                master,
                                height=25,
                                bg='white',
                                highlightthickness=0
                                )
        self.draw_arrow(start_x,factor,max_value)

    def draw_arrow(self,start_x,factor,max_value=None):
        self.create_line(start_x,
                         20,
                         start_x+factor*max_value+10,
                         20,
                         arrow=Tkinter.LAST,
                         tags=('arrow'))
        if max_value!=None:
            self.config_scale(start_x,factor,max_value)

    def config_scale(self,start_x,factor,max_value):
        tic_tags=self.find_withtag('tic')
        for tag in tic_tags:
            self.delete(tag)
        arrow=self.find_withtag('arrow')
        self.coords(arrow,
                    start_x,
                    20,
                    start_x+factor*max_value+10,
                    20)
        scale_frac=10.0**(math.floor(math.log10(max_value)))
        if scale_frac*factor>100:
            scale_frac/=2
        if scale_frac*factor<50:
            scale_frac*=2
        # an der Teilung muß noch gefeilt werden
        round_pos=-math.floor(math.log10(scale_frac))
        x_pos=0.0
        while x_pos<=max_value:
            pixel_x=start_x+x_pos*factor
            self.create_line(pixel_x,15,pixel_x,25,
                                   tags=('tic'))
            self.create_text(pixel_x,15,text=str(round(x_pos,round_pos)),
                             anchor=Tkinter.S,
                             tags=('tic','text'))
            x_pos=x_pos+scale_frac


####################################################################################

class bar_chart_with_scale(Tkinter.Frame):

    def __init__(self,master,prob_dict,keys,colors,report_func):
        """
        glue scale and barchart together
        """
        Tkinter.Frame.__init__(self,master)
        self.bars=e_bar_chart_y(self,prob_dict,keys,colors,self.bar_report)
        scale_start_x=self.bars.x_margin+self.bars.text_length
        factor=self.bars.bar_factor
        scale_max=self.bars.max_value
        self.scale=scale(self,scale_start_x,factor,scale_max)

        self.report_func=report_func
        self.scrollbar = Tkinter.Scrollbar(self,orient=Tkinter.VERTICAL,
                                           command=self.bars.yview)
        region=self.bars.bbox(Tkinter.ALL)
        sregion=(0,0,region[2],region[3])
        self.bars.config(scrollregion=sregion,
                         yscrollcommand=self.scrollbar.set)

        empty=Tkinter.Frame(self,bg='white')
        self.scale.grid(column=0,row=0,sticky=Tkinter.E+Tkinter.W)
        self.bars.grid(column=0,row=1,sticky=Tkinter.E+Tkinter.W+Tkinter.N+Tkinter.S)
        empty.grid(column=1,row=0,sticky=Tkinter.E+Tkinter.W+Tkinter.N+Tkinter.S)
        Tkinter.Frame.columnconfigure(self,0,weight=1)
        Tkinter.Frame.rowconfigure(self,1,weight=1)
        self.bind('<Configure>',self.config_event)

    def config_event(self,event):
        """
        add or remove scrollbar
        """
        scrollr=self.bars.cget('scrollregion')
        scrollr=map(int,scrollr.split())
        # print "from config",scrollr
        #hier muesste noch ein config_scale rein
        # self.scale.config_scale()
        if event.height>=(scrollr[3]-scrollr[1]):
            # print "y_scrollbar away"
            self.scrollbar.grid_remove()
        else:
            # print "y_scrollbar needed"
            self.scrollbar.grid(column=1,row=1,sticky=Tkinter.NS)

    def bar_report(self,what,key,value):
        if what=='move':
            return
        if what=='scale change':
            self.scale.config_scale(self.bars.x_margin+self.bars.text_length,
                                    self.bars.bar_factor,
                                    self.bars.bar_length/self.bars.bar_factor)
            return

        self.report_func(what,key,value)


####################################################################################

class rod_chart(Tkinter.Canvas):
    def __init__(self,master,prob_dict,keys,colors):
        self.ProbDict=prob_dict
        self.rod_box=(10,10,300,60)
        Tkinter.Canvas.__init__(self,master,
                                bg='white',highlightthickness=0,
                                width=200,height=320
                                )
        self.draw_rods(keys,colors)

    def draw_rods(self,keys,colors):
        start_pos=self.rod_box[0]
        factor=(self.rod_box[2]-self.rod_box[0])/self.ProbDict.sum
        i=0
        for key in keys:
            end_pos=start_pos+factor*self.ProbDict[key]
            self.create_rectangle(start_pos,
                                  self.rod_box[1],
                                  end_pos,
                                  self.rod_box[3],
                                  fill=colors[i],
                                  tags=('rod','tag_'+key))
            i=i+1

        for key in keys:
            rod_item=self.find_withtag('tag_'+key)[0]
            coords=self.coords(rod_item)
            text_line_x=(coords[0]+coords[2])/2
            h1=0.7
            h2=1.2
            h3=1.5
            text_line_y1=(coords[1]*(1-h1)+coords[3]*h1)
            text_line_y2=(coords[1]*(1-h2)+coords[3]*h2)
            text_y=(coords[1]*(1-h3)+coords[3]*h3)
            self.create_line(text_line_x,text_line_y1,
                             text_line_x,text_line_y2,
                             tags=('tag_'+key,'line'))
            self.create_text(text_line_x,text_y,
                             text=key,
                             anchor=Tkinter.N)

class e_rod_chart(rod_chart):
    def __init__(self,master,prob_dict,keys,colors):
        rod_chart.__init__(self,master,prob_dict,keys,colors)

        self.text_item=self.create_text(20,190,text='Los gehts',tag='info')

        for item in self.find_withtag('bar'):
            self.tag_bind(item,'<Button-1>',self.handle_mouse_move_start)

    def handle_mouse_move_start(self,event):
        self.current_item=self.find_withtag(Tkinter.CURRENT)[0]
        coords=self.coords(self.current_item)
        if self.canvasy(event.y)>coords[1]+2:
            return
        self.bind('<ButtonRelease-1>',self.handle_mouse_move_end)
        self.bind('<B1-Motion>',self.handle_mouse_move)
        self.itemconfigure(self.text_item, text='Enter')

    def handle_mouse_move(self,event):
        coords=self.coords(self.current_item)
        y=self.eventy(event.y)
        if y>coords[3] or y<self.bar_box[1]:
            return
        coords[1]=y
        self.coords(self.current_item,tuple(coords))
        self.itemconfigure(self.text_item, text='Move')

    def handle_mouse_move_end(self,event):
        self.unbind('<ButtonRelease-1>')
        self.unbind('<B1-Motion>')
        self.itemconfigure(self.text_item, text='Leave')
        tags=self.gettags(self.current_item)
        tag=filter(lambda tag: tag[:4]=='tag_',tags)[0]
        coords=self.coords(self.current_item)
        new_value=float(coords[1]-coords[3])/self.bar_height
        self.change_value(tag[4:],new_value)

    def change_value(self,key,value):
        self.ProbDict[key]=value
        self.ProbDict.changed()

####################################################################################

class pie_chart(Tkinter.Canvas,flyout_decoration):

    def __init__(self,master,prob_dict,keys,colors):
        self.ProbDict=prob_dict
        self.arc_box=(100,50,300,250)
        self.key_list=keys
        Tkinter.Canvas.__init__(self,master,bg='white',highlightthickness=0)
        self.draw_arcs(self.arc_box,keys,colors)
        flyout_decoration.__init__(self,self.info_function)

    def info_function(self,item):
        tag=filter(lambda t:t=='other' or t[:4]=='tag_',self.gettags(item))[0]
        sector=filter(lambda i,s=self:'sector' in s.gettags(i),self.find_withtag(tag))
        if tag!='other':
            key=ProbEditorBasics.tag_to_key(tag[4:])
        else:
            key='other'
        value=abs(float(self.itemcget(sector,'extent')))/360.0*self.ProbDict.sum
        l10_value=-math.floor(math.log10(value))
        info='%s: %s'%(key,str(round(value,l10_value+3)))
        return info

    def anchor(self,angle,angle_base):
        """
        returns anchor-position for text
        angle is counted anti-clockwise from 3o'clock
        """
        #Winkel auf jeden Fall positiv zählen
        if angle<0:
            my_angle=angle_base/2-angle
        my_angle=(angle/angle_base-math.floor(angle/angle_base))*8.0
        if my_angle<1 or my_angle>=7:
            return Tkinter.W
        if my_angle<2:
            return Tkinter.SW
        if my_angle<3:
            return Tkinter.SE
        if my_angle<5:
            return Tkinter.E
        if my_angle<6:
            return Tkinter.NE
        return Tkinter.NW

    def draw_arcs(self,circle_box,key_list,colors):
        """
        """
        this_sum=0.0
        #Start bei 6 Uhr
        start_angle=270.0
        # im Uhrzeigersinn laufen
        full_angle=-360.0
        i=0
        while i<=len(key_list):
            key=''
            tag=''
            this_angle=0
            extent_angle=0
            if i<len(key_list):
                key=key_list[i]
                tag='tag_'+ProbEditorBasics.key_to_tag(key)
                this_angle=start_angle+this_sum*full_angle/self.ProbDict.sum
                extent_angle=self.ProbDict[key]*full_angle/self.ProbDict.sum
                this_sum=this_sum+self.ProbDict[key]
                color=colors[i]
            else:
                key='other'
                tag='other'
                if 1.0-this_sum/self.ProbDict.sum<=1e-5:
                    break
                this_angle=start_angle+this_sum*full_angle/self.ProbDict.sum
                extent_angle=start_angle+full_angle-this_angle
                color=self.cget('bg')
            line_angle=0.0
            if abs(extent_angle)>=360:
                # fast voller Kreis
                extent_angle=359.9
            # Volle Kreise zeichnen
            sector=self.create_arc(circle_box,
                                   start=this_angle,
                                   extent=extent_angle,
                                   tags=('sector','flyout_info',tag),
                                   fill=color)
            i=i+1

        for item in self.find_withtag('sector'):
            coords=self.coords(item)
            start_angle=float(self.itemcget(item,'start'))
            extent_angle=float(self.itemcget(item,'extent'))
            line_angle=start_angle+extent_angle/2
            tags=filter(lambda t: t[:4]=='tag_',self.gettags(item))
            text=''
            if len(tags)==0:
                text='other'
                tags=('other',)
            else:
                text=ProbEditorBasics.tag_to_key(tags[0][4:])
            m_x=math.cos(line_angle/180.0*math.pi)
            m_y=-math.sin(line_angle/180.0*math.pi)
            circle_middle_x=(coords[0]+coords[2])/2
            circle_middle_y=(coords[1]+coords[3])/2
            circle_diam_x=(coords[2]-coords[0])/2
            circle_diam_y=(coords[3]-coords[1])/2
            self.create_line(circle_middle_x+m_x*circle_diam_x*0.8,
                             circle_middle_y+m_y*circle_diam_y*0.8,
                             circle_middle_x+m_x*circle_diam_x*1.1,
                             circle_middle_y+m_y*circle_diam_y*1.1,
                             tags=('line',tags))
            # hier ist der Text!
            self.create_text(circle_middle_x+m_x*circle_diam_x*1.1,
                             circle_middle_y+m_y*circle_diam_y*1.1,
                             anchor=self.anchor(line_angle,360.0),
                             text=text,
                             tags=('text',tags))

    def configure_description(self,item):
        coords=self.coords(item)
        if len(coords)==0: return
        start_angle=float(self.itemcget(item,'start'))
        extent_angle=float(self.itemcget(item,'extent'))
        line_angle=start_angle+extent_angle/2
        m_x=math.cos(line_angle/180.0*math.pi)
        m_y=-math.sin(line_angle/180.0*math.pi)
        circle_middle_x=(coords[0]+coords[2])/2
        circle_middle_y=(coords[1]+coords[3])/2
        circle_diam_x=(coords[2]-coords[0])/2
        circle_diam_y=(coords[3]-coords[1])/2
        tags=filter(lambda t: t[:4]=='tag_',self.gettags(item))
        if len(tags)==0:
            tags=('other',)
        
        tag_items=self.find_withtag(tags[0])
        line_item=text_item=0
        for tag_item in tag_items:
            item_type=self.type(tag_item)
            if item_type=="line":
                line_item=tag_item
            elif item_type=="text":
                text_item=tag_item
                
        self.coords(line_item,
                    circle_middle_x+m_x*circle_diam_x*0.8,
                    circle_middle_y+m_y*circle_diam_y*0.8,
                    circle_middle_x+m_x*circle_diam_x*1.1,
                    circle_middle_y+m_y*circle_diam_y*1.1)
        # hier ist der Text!
        self.coords(text_item,
                    circle_middle_x+m_x*circle_diam_x*1.1,
                    circle_middle_y+m_y*circle_diam_y*1.1)
        self.itemconfig(text_item,
                        anchor=self.anchor(line_angle,360.0))

    def update_colors(self,order_list,color_list):
        sectors=self.find_withtag('sector')
        for sector in sectors:
            tag=filter(lambda t:t[:4]=='tag_',self.gettags(sector))[0]
            key=ProbEditorBasics.tag_to_key(tag[4:])
            if len(keytag)!=1: continue
            color=color_list[order_list.index(key)]
            self.itemconfig(sector,color=color)

    def update_position(self,dict,order_list):
        this_sum=0.0
        #Start bei 6 Uhr
        start_angle=270.0
        # im Uhrzeigersinn laufen
        full_angle=-360.0
        i=0
        while i<=len(order_list):
            key=''
            tag=''
            this_angle=0
            extent_angle=0
            if i<len(order_list):
                key=order_list[i]
                tag='tag_'+ProbEditorBasics.key_to_tag(key)
                this_angle=start_angle+this_sum*full_angle/dict.sum
                extent_angle=dict[key]*full_angle/dict.sum
                this_sum=this_sum+dict[key]
            else:
                key='other'
                tag='other'
                if 1.0-this_sum/dict.sum<=1e-5:
                    break
                this_angle=start_angle+this_sum*full_angle/dict.sum
                extent_angle=start_angle+full_angle-this_angle
            line_angle=0.0
            sector=filter(lambda item,s=self:'sector' in s.gettags(item),
                          self.find_withtag(tag))
            
            if abs(extent_angle)>=360:
                extent_angle=359.9
            self.itemconfig(sector,
                            start=this_angle,
                            extent=extent_angle)
            self.configure_description(sector)
            i=i+1

    def angle(self,x,y):
        if y==0:
            if x<0: return 180.0
            else: return 0.0
        elif x==0:
            if y<0: return 90.0
            else: return 270.0
        elif y<0:
            return math.atan(x/y)/math.pi*180.0+90.0
        else:
            return math.atan(x/y)/math.pi*180.0+270.0

######################################################################################

class e_pie_chart(pie_chart):

    def __init__(self,master,prob_dict,keys,colors,report_func):
        pie_chart.__init__(self,master,prob_dict,keys,colors)
        self.report_func=report_func
        self.oval_diam_x=self.oval_diam_y=4
        self.init_handles()
        flyout_decoration.add_bindings(self,self.info_function)

    def info_function(self,item):
        tags=self.gettags(item)
        if 'handle' in tags:
            tag=filter(lambda t:t[:4]=='tag_' or t=='other',tags)[0]
            if tag!='other':
                key=ProbEditorBasics.tag_to_key(tag[4:])
            else:
                key='other'
            arc=filter(lambda i,s=self:s.type(i)=='arc',
                        self.find_withtag(tag))
            neighbours=self.find_neighbours(arc)
            neighbours.append(arc)
            flyout_text=''
            for item in neighbours:
                flyout_text+=', '+pie_chart.info_function(self,item)
            flyout_text=flyout_text[2:]
        else:
            flyout_text=pie_chart.info_function(self,item)
        return flyout_text


    def find_neighbours(self,sector_item):
        # find neighbour sector
        angle_pos=float(self.itemcget(sector_item,'start'))
        sectors=self.find_withtag('sector')
        neighbours=[]
        for sector in sectors:
            extent_angle=float(self.itemcget(sector,'extent'))
            start_angle=float(self.itemcget(sector,'start'))
            angle_diff=divmod(start_angle+extent_angle-angle_pos,360.0)[1]
            if angle_diff<0.1 or angle_diff>359.9:
                neighbours.append(sector)
        return neighbours

    def move_start(self,event):
        # find sector belonging to handle
        self.current_item=self.find_withtag(Tkinter.CURRENT)[0]
        self.current_tag=filter(lambda t:t[:4]=='tag_' or t=='other',
                                self.gettags(self.current_item))[0]
        self.current_arc1=filter(lambda i,s=self:s.type(i)=='arc',
                                 self.find_withtag(self.current_tag))
        # find neighbour sector
        self.current_arc2=self.find_neighbours(self.current_arc1)

        # really found one?
        if len(self.current_arc2)==0:
            print 'no neighbour found'
            return
        if len(self.current_arc2)>1:
            print 'too much neighbours found'
            return

        self.current_arc2=self.current_arc2[0]
        # cache coordinates
        coords=self.coords(self.current_arc1)
        self.current_center_x=(coords[0]+coords[2])/2.0 #center of arc
        self.current_center_y=(coords[1]+coords[3])/2.0 #center of arc
        self.current_diam_x=abs(coords[1]-coords[3])/2.0
        self.current_diam_y=abs(coords[0]-coords[2])/2.0
        # save angle sum
        self.angle_start=float(self.itemcget(self.current_arc2,'start'))
        self.angle_extent=float(self.itemcget(self.current_arc1,'extent'))+float(self.itemcget(self.current_arc2,'extent'))

        self.bind('<B1-Motion>',self.move)
        self.bind('<ButtonRelease-1>',self.move_end)

    def move(self,event):
        # compute new angle
        canvas_x=self.canvasx(event.x)
        canvas_y=self.canvasy(event.y)
        angle=self.angle(canvas_x-self.current_center_x,canvas_y-self.current_center_y)
        # is this angle valid?
        # and calcualte new start,extent angles
        new_extent2=float(self.itemcget(self.current_arc2,'extent'))
        new_start1=float(self.itemcget(self.current_arc1,'start'))
        if self.angle_extent>0:
            #anti-clockwise orientation
            if self.angle_start>angle:
                if self.angle_start+self.angle_extent<=angle+360:
                    # valid
                    new_start1=angle
                    new_extent2=angle+360-self.angle_start
                else:
                    #invalid
                    pass
            else:
                if self.angle_start+self.angle_extent<=angle:
                    # valid
                    new_start1=angle
                    new_extent2=angle-self.angle_start
                else:
                    # invalid
                    pass
        else:
            #clockwise orientation
            if self.angle_start<angle:
                if self.angle_start+self.angle_extent<=angle-360:
                    # valid
                    new_start1=angle
                    new_extent2=angle-360-self.angle_start
                else:
                    # invalid
                    pass
            else:
                if self.angle_start+self.angle_extent<=angle:
                    # valid
                    new_start1=angle
                    new_extent2=angle-self.angle_start
                else:
                    # invalid
                    pass

        # set new arc angles
        new_start2=self.angle_start
        new_extent1=self.angle_extent-new_extent2
        # pitfall! extent>=360°
        if new_extent1>359.9:
            new_extent1=359.9
        elif new_extent1<-359.9:
            new_extent1=-359.9
        if new_extent2>359.9:
            new_extent2=359.9
        elif new_extent2<-359.9:
            new_extent2=-359.9
        self.itemconfig(self.current_arc1,start=new_start1)
        self.itemconfig(self.current_arc2,start=new_start2)
        self.itemconfig(self.current_arc1,extent=new_extent1)
        self.itemconfig(self.current_arc2,extent=new_extent2)
        # set handle
        oval_x=math.cos(new_start1/180.0*math.pi)*self.current_diam_x+self.current_center_x
        oval_y=-math.sin(new_start1/180.0*math.pi)*self.current_diam_y+self.current_center_y
        oval=self.coords(self.current_item,
                         oval_x-self.oval_diam_x,oval_y-self.oval_diam_y,
                         oval_x+self.oval_diam_x,oval_y+self.oval_diam_y)

        # set description
        self.configure_description(self.current_arc1)
        self.configure_description(self.current_arc2)

        # report move
        tags=self.gettags(self.current_arc1)
        tag1=filter(lambda tag: tag[:4]=='tag_' or tag=='other',tags)[0]
        if tag1!='other':
            key1=ProbEditorBasics.tag_to_key(tag1[4:])
        else:
            key1='other'
        tags=self.gettags(self.current_arc2)
        tag2=filter(lambda tag: tag[:4]=='tag_' or tag=='other',tags)[0]
        if tag2!='other':
            key2=ProbEditorBasics.tag_to_key(tag2[4:])
        else:
            key2='other'
        value1=abs(float(self.itemcget(self.current_arc1,
                                       'extent')))/360.0*self.ProbDict.sum
        value2=abs(float(self.itemcget(self.current_arc2,
                                       'extent')))/360.0*self.ProbDict.sum
        report_dict={}
        report_dict[key1]=value1
        report_dict[key2]=value2
        self.report_func('move value',report_dict)


    def move_end(self,event):
        # no events!
        self.unbind('<B1-Motion>')
        self.unbind('<ButtonRelease-1>')
        # read new values from graphic
        tags=self.gettags(self.current_arc1)
        tag1=filter(lambda tag: tag[:4]=='tag_' or tag=='other',tags)[0]
        if tag1!='other':
            key1=ProbEditorBasics.tag_to_key(tag1[4:])
        else:
            key1='other'
        tags=self.gettags(self.current_arc2)
        tag2=filter(lambda tag: tag[:4]=='tag_' or tag=='other',tags)[0]
        if tag2!='other':
            key2=ProbEditorBasics.tag_to_key(tag2[4:])
        else:
            key2='other'
        value1=abs(float(self.itemcget(self.current_arc1,
                                       'extent')))/360.0*self.ProbDict.sum
        value2=abs(float(self.itemcget(self.current_arc2,
                                       'extent')))/360.0*self.ProbDict.sum
        report_dict={}
        report_dict[key1]=value1
        report_dict[key2]=value2
        self.report_func('new value',report_dict)
        self.current_tag=None
        self.current_key=None


    def init_handles(self):
        sectors=list(self.find_withtag('sector'))
        sectors.reverse()
        for sector in sectors:
            coords=self.coords(sector)
            tag=filter(lambda t:t[:4]=='tag_' or t=='other',self.gettags(sector))
            angle=float(self.itemcget(sector,'start'))
            center_x=(coords[0]+coords[2])/2.0 #center of arc
            center_y=(coords[1]+coords[3])/2.0 #center of arc
            diam_x=abs(coords[1]-coords[3])/2.0
            diam_y=abs(coords[0]-coords[2])/2.0
            oval_x=math.cos(angle/180.0*math.pi)*diam_x+center_x
            oval_y=-math.sin(angle/180.0*math.pi)*diam_y+center_y
            oval=self.create_oval(oval_x-self.oval_diam_x,oval_y-self.oval_diam_y,
                                  oval_x+self.oval_diam_x,oval_y+self.oval_diam_y,
                                  fill='black',tags=('handle','flyout_info',tag))
            self.tag_bind(oval,'<Button-1>',self.move_start)

    def update_handles(self):
        sectors=list(self.find_withtag('sector'))
        sectors.reverse()
        for sector in sectors:
            coords=self.coords(sector)
            tag=filter(lambda t:t[:4]=='tag_' or t=='other',self.gettags(sector))
            angle=float(self.itemcget(sector,'start'))
            center_x=(coords[0]+coords[2])/2.0 #center of arc
            center_y=(coords[1]+coords[3])/2.0 #center of arc
            diam_x=abs(coords[1]-coords[3])/2.0
            diam_y=abs(coords[0]-coords[2])/2.0
            oval_x=math.cos(angle/180.0*math.pi)*diam_x+center_x
            oval_y=-math.sin(angle/180.0*math.pi)*diam_y+center_y
            oval=filter(lambda i,s=self:s.type(i)=='oval',
                        self.find_withtag(tag))

            self.coords(oval,oval_x-self.oval_diam_x,oval_y-self.oval_diam_y,
                        oval_x+self.oval_diam_x,oval_y+self.oval_diam_y)

    def update_position(self,dict,order_list):
        pie_chart.update_position(self,dict,order_list)
        self.update_handles()
