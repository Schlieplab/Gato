#!/usr/bin/env python
################################################################################
#
#       This file is part of Gato (Combinatorial Algorithm Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/~gato
#
#	file:   ProbEditorWidgets.py
#	author: Achim Gaedke (achim.gaedke@zpr.uni-koeln.de)
#
#       _COPYRIGHT_
#
#       This file is version $Revision$ 
#                       from $Date$
#             last change by $Author$.
#
################################################################################

import math
import Tkinter
import ProbEditorBasics

class tab_frame(Tkinter.Frame):
    """
    """
    def tab_selected(self,event):
        selected_item=event.widget.find_withtag(Tkinter.CURRENT)[0]
        selected_tags=event.widget.gettags(selected_item)
        tab_name=filter(lambda t: t[:4]=='tab_',selected_tags)[0][9:]
        if tab_name!=self.actual_tab:
            self.change_tab(tab_name)

    def change_tab(self,key):
        # change tabs
        if self.actual_tab!=None:
            poly_list=self.tabs.find_withtag('tab_poly_'+self.actual_tab)
            for item in poly_list:
                self.tabs.itemconfigure(item,fill='')

        poly_list=self.tabs.find_withtag('tab_poly_'+key)
        for item in poly_list:
            self.tabs.itemconfigure(item,fill='white')
            self.tabs.lift(item)
        text_list=self.tabs.find_withtag('tab_text_'+key)
        for item in text_list:
            self.tabs.lift(item)
        
        # change body
        if self.actual_tab!=None:
            self.widget_dict[self.actual_tab].forget()
        self.widget_dict[key].pack(side=Tkinter.BOTTOM,in_=self,
                                   expand=1,fill=Tkinter.BOTH)
        self.actual_tab=key

    def __init__(self,master,widget_dict,start=None):
        Tkinter.Frame.__init__(self,master)
        self.lower()
        self.tabs=Tkinter.Canvas(self,height=25,highlightthickness=0)
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
            tab_text=key.replace('_',' ')
            text=self.tabs.create_text((pos_x,text_base_y),
                                       text=tab_text,
                                       anchor=text_anchor,
                                       tags=('tab_text_'+key))
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
                                         tags=('tab_poly_'+key),
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

####################################################################################

class bar_chart_x(Tkinter.Canvas):

    def __init__(self,master,prob_dict,keys,colors):
        self.max_value=0
        for k in keys:
            if prob_dict[k]>self.max_value:
                self.max_value=prob_dict[k]
        self.bar_box=(10,10,300,250)
        Tkinter.Canvas.__init__(self,master,
                                bg='white',highlightthickness=0,
                                width=400,height=320)
        self.bar_step=50
        self.bar_width=30
        self.bar_height=(self.bar_box[1]-self.bar_box[3])/self.max_value

        self.create_bars(prob_dict,keys,colors)
        self.config_bar_height(prob_dict)

    def create_bars(self,prob_dict,keys,colors):
        start_x=self.bar_box[0]
        start_y=self.bar_box[3]
        text_x=self.bar_width/2
        text_y=5
        text_anchor=Tkinter.N
        i=0
        for k in keys:
            pos_x=start_x+i*self.bar_step
            pos_y=start_y
            self.create_rectangle(pos_x,
                                  pos_y,
                                  pos_x+self.bar_width,
                                  pos_y,
                                  fill=colors[i],
                                  tags=('bar','tag_'+k))
            self.create_text(pos_x+text_x,pos_y+text_y,
                             anchor=text_anchor,
                             text=k,
                             tags=('text','tag_'+k))
            i=i+1
        
    def config_bar_height(self,prob_dict):

        for key in prob_dict.keys():
            items=self.find_withtag('tag_'+key)
            item=filter(lambda i,s=self:s.type(i)=='rectangle',items)
            coords=self.coords(item)
            self.coords(item,coords[2],coords[3],
                        coords[0],coords[3]+prob_dict[key]*self.bar_height)

    def config_bar_color(self,keys,color_list):
        bar_items=self.find_withtag('bar')

        for item in bar_items:
            key=filter(lambda t:t[:4]=='tag_',self.gettags(item))[0][4:]
            color=color_list[keys.index(key)]
            self.itemconfig(item,fill=color)

    def config_bar_order(self,keys):
        text_x=self.bar_width/2
        start_x=self.bar_box[0]
        start_y=self.bar_box[3]
        i=0
        for k in keys:
            items=self.find_withtag('tag_'+key)
            if len(items)==0:
                continue
            bar_item=filter(lambda i,s=self:s.type(i)=='rectangle',items)
            text_item=filter(lambda i,s=self:s.type(i)=='text',items)
            pos_x=start_x+i*self.bar_step
            pos_y=start_y
            bar_coords=self.coords(bar_item)
            self.coords(bar_item,
                        pos_x,
                        bar_coords[1],
                        pos_x+self.bar_width,
                        bar_coords[3])
            text_coords=self.coords(text_item)
            self.coords(text_item,pos_x+text_x,text_coords[1])
            i=i+1

class e_bar_chart_x(bar_chart_x):

    def __init__(self,master,prob_dict,keys,colors,report_func):
        bar_chart_x.__init__(self,master,prob_dict,keys,colors)
        # report value changes to this function
        self.report_func=report_func

        for item in self.find_withtag('bar'):
            self.tag_bind(item,'<Button-1>',self.handle_mouse_move_start)

    def handle_mouse_move_start(self,event):
        self.current_item=self.find_withtag(Tkinter.CURRENT)[0]
        coords=self.coords(self.current_item)
        if event.y>coords[1]+2:
            return
        self.bind('<ButtonRelease-1>',self.handle_mouse_move_end)
        self.bind('<B1-Motion>',self.handle_mouse_move)

    def handle_mouse_move(self,event):
        coords=self.coords(self.current_item)
        if event.y>coords[3] or event.y<self.bar_box[1]:
            return
        coords[1]=event.y
        self.coords(self.current_item,tuple(coords))

    def handle_mouse_move_end(self,event):
        self.unbind('<ButtonRelease-1>')
        self.unbind('<B1-Motion>')
        tags=self.gettags(self.current_item)
        tag=filter(lambda tag: tag[:4]=='tag_',tags)[0]
        coords=self.coords(self.current_item)
        new_value=float(coords[1]-coords[3])/self.bar_height
        self.report_func(tag[4:],new_value)

#####################################################################################

class bar_chart_y(Tkinter.Canvas):

    def __init__(self,master,prob_dict,keys,colors):
        self.max_value=0.0
        for k in keys:
            if prob_dict[k]>self.max_value:
                self.max_value=prob_dict[k]
        self.bar_step=30
        self.bar_width=20
        self.text_length=30
        self.x_margin=10
        self.y_margin=10
        self.bar_length=350
        self.bar_factor=self.bar_length/self.max_value
        Tkinter.Canvas.__init__(self,
                                master,
                                bg='white',
                                highlightthickness=0,
                                width=self.text_length+self.bar_length+2*self.x_margin,
                                height=len(keys)*self.bar_step+self.text_length+2*self.y_margin)
        self.create_bars(prob_dict,keys,colors)
        self.config_bar_height(prob_dict)
        self.create_bar_flyouts(prob_dict)

    def create_bars(self,prob_dict,keys,colors):
        start_x=self.x_margin+self.text_length
        start_y=self.y_margin
        text_anchor=Tkinter.W
        i=0
        for k in keys:
            pos_x=start_x
            pos_y=start_y+i*self.bar_step
            self.create_rectangle(pos_x,
                                  pos_y,
                                  pos_x,
                                  pos_y+self.bar_width,
                                  fill=colors[i],
                                  tags=('bar','tag_'+k))
            self.create_text(self.x_margin,pos_y+self.bar_width/2,
                             anchor=text_anchor,
                             text=k,
                             tags=('text','tag_'+k))
            i=i+1

    def create_bar_flyouts(self,prob_dict):
        self.flyout_stat=0
        self.after_id=0
        for key in prob_dict.keys():
            items=self.find_withtag('tag_'+key)
            if len(items)==0: continue
            item=filter(lambda i,s=self:s.type(i)=='rectangle',items)
            self.tag_bind(item,'<Enter>',self.flyout_enter)
            self.tag_bind(item,'<Motion>',self.flyout_delay_start)
            self.tag_bind(item,'<Leave>',self.flyout_leave)

    def flyout_enter(self,event):
        # stat:
        # 0 no timer set, no flyout, after motion =>1
        # 1 timer set, no flyout, after motion =>1, no motion =>2
        # 2 flyout, no timer, after motion =>1
        if self.flyout_stat!=0:
            return
        self.flyout_stat=0
        self.after_id=0

    def flyout_leave(self,event):
        if self.flyout_stat==1:
            self.after_cancel(self.after_id)
        if self.flyout_stat==2:
            self.flyout_hide()
        self.flyout_stat=0

    def flyout_delay_start(self,event):
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
        self.flyout_stat==2
        self.flyout_show(item,x,y)

    def flyout_show(self,item,x,y):
        self.flyout_stat=2
        key=filter(lambda t:t[:4]=='tag_',self.gettags(item))[0][4:]
        coords=self.coords(item)
        value=float(coords[2]-coords[0])/self.bar_factor
        flyout_text=('%s: %f')%(key,value)
        text_x=self.canvasx(x)+15
        text_y=self.canvasy(y)+15
        text_item=self.create_text((text_x,text_y),text=flyout_text,tags=('flyout'),
                                   anchor=Tkinter.NW)
        self.create_rectangle(self.bbox(text_item),fill='khaki',tags=('flyout'))
        self.lift(text_item)
        
    def flyout_hide(self):
        self.flyout_stat=0
        flyout_elements=self.find_withtag('flyout')
        for element in flyout_elements:
            self.delete(element)

    def get_bar_values(self,key_list=None):
        dict={}
        if not key_list:
            # return all keys
            bar_items=self.find_withtag('bar')
            for bar_item in bar_items:
                tags=self.gettags(bar_item)
                key=filter(lambda t:'tag_'==t[:4],tags)[0][4:]
                coords=self.coords(bar_item)
                value=float(coords[2]-coords[0])/self.bar_factor
                dict.update({key:value})
        else:
            # retur only keys in list
            for key in key_list:
                items=self.find_withtag('tag_'+key)
                if len(items)==0: continue
                bar_item=filter(lambda i,s=self:'bar' in s.gettags(i),items)
                coords=self.coords(bar_item)
                value=float(coords[2]-coords[0])/self.bar_factor
                dict.update({key:value})
        return dict
            
    def config_bar_height(self,prob_dict):
        for key in prob_dict.keys():
            items=self.find_withtag('tag_'+key)
            if len(items)==0: continue
            bar_item=filter(lambda i,s=self:'bar' in s.gettags(i),items)
            coords=self.coords(bar_item)
            self.coords(bar_item,coords[0],coords[1],
                        coords[0]+prob_dict[key]*self.bar_factor,coords[3])

    def config_bar_color(self,keys,color_list):
        bar_items=self.find_withtag('bar')
        for item in bar_items:
            key=filter(lambda t:t[:4]=='tag_',self.gettags(item))[0][4:]
            color=color_list[keys.index(key)]
            self.itemconfig(item,fill=color)

    def config_bar_order(self,keys):
        text_x=self.bar_width/2
        start_y=self.y_margin
        i=0
        for k in keys:
            items=self.find_withtag('tag_'+key)
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

class e_bar_chart_y(bar_chart_y):

    def __init__(self,master,prob_dict,keys,colors,report_func):
        bar_chart_y.__init__(self,master,prob_dict,keys,colors)
        # report value changes to this function
        self.report_func=report_func

        self.normal_cursor=self.cget('cursor')
        self.current_item=None
        for item in self.find_withtag('bar'):
            coords=self.coords(item)
            tags=self.gettags(item)
            tag=filter(lambda tag: tag[:4]=='tag_',tags)[0]
            handle=self.create_rectangle((coords[2],coords[1],coords[2],coords[3]),
                                         fill='black',
                                         tags=('bar_top',tag))
            self.tag_bind(handle,'<Button-1>',self.handle_mouse_move_start)
            self.tag_bind(handle,'<Enter>',self.change_cursor)
            self.tag_bind(handle,'<Leave>',self.restore_cursor)
        self.config_handle_pos(prob_dict)

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
        self.current_item=self.find_withtag(Tkinter.CURRENT)[0]
        tags=self.gettags(self.current_item)
        self.current_key=filter(lambda tag: tag[:4]=='tag_',tags)[0][4:]
        self.bind('<ButtonRelease-1>',self.handle_mouse_move_end)
        self.bind('<B1-Motion>',self.handle_mouse_move)
        coords=self.coords(self.current_item)
        old_value=self.value_from_handle_coords(coords)
        self.report_func('old value',self.current_key,old_value)

    def handle_mouse_move(self,event):
        x=self.canvasx(event.x)
        what='move'
        if x<self.x_margin+self.text_length:
            x=self.x_margin+self.text_length
        elif x>self.x_margin+self.text_length+self.bar_length:
            x=self.x_margin+self.text_length+self.bar_length
            what='max reached'
        new_value=float(x-self.x_margin-self.text_length)/self.bar_factor
        self.config_handle_pos({self.current_key:new_value})
        self.report_func(what,self.current_key,new_value)

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
        for key in prob_dict.keys():
            items=self.find_withtag('tag_'+key)
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

####################################################################################

class bar_chart_with_scale(Tkinter.Frame):

    def bar_report(self,what,key,value):
        if what=='move':
            self.move_count+=1
        if what=='max reached' and self.move_count>1:
            actual_values=self.bars.get_bar_values()
            self.bars.bar_factor/=2
            self.bars.config_bar_height(actual_values)
            self.config_scale()
            self.move_count=0
        self.report_func(what,key,value)

    def __init__(self,master,prob_dict,keys,colors,report_func):
        Tkinter.Frame.__init__(self,master)
        self.bars=e_bar_chart_y(self,prob_dict,keys,colors,self.bar_report)
        self.scale=Tkinter.Canvas(self,
                                  width=self.bars.cget('width'),
                                  height=25,
                                  bg='white',
                                  highlightthickness=0
                                  )
        self.draw_scale()
        self.scale.grid(row=0,column=0)
        self.bars.grid(row=1,column=0)
        self.report_func=report_func
        scrollbar = Tkinter.Scrollbar(self,orient=Tkinter.VERTICAL,
                                      command=self.bars.yview)
        region=self.bars.bbox(Tkinter.ALL)
        sregion=(0,0,region[2],region[3])
        self.bars.config(height=300,
                         scrollregion=sregion,
                         yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1,column=1,sticky=Tkinter.N+Tkinter.S)
        self.move_count=0

    def draw_scale(self):
        scale_start_x=self.bars.x_margin+self.bars.text_length
        self.scale.create_line(scale_start_x,
                               20,
                               scale_start_x+self.bars.bar_length+10,
                               20,
                               arrow=Tkinter.LAST,
                               tags=('arrow'))
        self.config_scale()

    def config_scale(self):
        tic_tags=self.scale.find_withtag('tic')
        for tag in tic_tags:
            self.scale.delete(tag)
        arrow=self.scale.find_withtag('arrow')
        scale_start_x=self.bars.x_margin+self.bars.text_length
        self.scale.coords(scale_start_x,
                          20,
                          scale_start_x+self.bars.bar_length+10,
                          20)
        scale_max=self.bars.bar_length/self.bars.bar_factor
        scale_frac=10.0**(math.floor(math.log10(scale_max)))/2
        scale_pixels=scale_frac*self.bars.bar_factor
        # an der Teilung muﬂ noch gefeilt werden
        x_pos=0
        while x_pos<=scale_max:
            pixel_x=scale_start_x+x_pos*self.bars.bar_factor
            self.scale.create_line(pixel_x,15,pixel_x,25,
                                   tags=('tic'))
            self.scale.create_text(pixel_x,15,text=repr(x_pos),
                                   anchor=Tkinter.S,
                                   tags=('tic','text'))
            x_pos=x_pos+scale_frac

####################################################################################

class rod_chart(Tkinter.Canvas):
    def __init__(self,master,prob_dict,keys,colors):
        self.ProbDict=prob_dict
        self.rod_box=(10,10,300,60)
        Tkinter.Canvas.__init__(self,master,
                                bg='white',highlightthickness=0,
                                width=200,height=320)
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

class pie_chart(Tkinter.Canvas):

    def __init__(self,master,prob_dict,keys,colors):
        self.ProbDict=prob_dict
        self.arc_box=(100,50,300,250)
        self.key_list=keys
        Tkinter.Canvas.__init__(self,master,bg='white',highlightthickness=0,
                                width=400,height=300)
        self.draw_arcs(self.arc_box,keys,colors)

    def anchor(self,angle,angle_base):
        """
        returns anchor-position for text
        angle is counted anti-clockwise from 3o'clock
        """
        #Winkel auf jeden Fall positiv z‰hlen
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
                tag='tag_'+key
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
                color=''
            line_angle=0.0
            if abs(extent_angle)>=360:
                extent_angle=359.9
##                # Volle Kreise zeichnen
##                sector=self.create_oval(circle_box,
##                                        tags=('sector',tag),
##                                        fill=color)
##            else:
            sector=self.create_arc(circle_box,
                                   start=this_angle,
                                   extent=extent_angle,
                                   tags=('sector',tag),
                                   fill=color)

            # self.tag_bind(sector,'<Enter>',self.create_info_line)
            # self.tag_bind(sector,'<Leave>',self.clear_info_line)
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
                text=tags[0][4:]
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
            key=filter(lambda t:t[:4]=='tag_',self.gettags(sector))[0][4:]
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
                tag='tag_'+key
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

class e_pie_chart(pie_chart):

    def __init__(self,master,prob_dict,keys,colors,report_func):
        pie_chart.__init__(self,master,prob_dict,keys,colors)
        self.report_func=report_func
        for item in self.find_withtag('sector'):
            self.tag_bind(item,'<Button-1>',self.handle_mouse_move_start)

    def handle_mouse_move_start(self,event):
        self.current_item=self.find_withtag(Tkinter.CURRENT)[0]
        coords=self.coords(self.current_item)
        center_x=(coords[0]+coords[2])/2.0 #center of oval
        center_y=(coords[1]+coords[3])/2.0 #center of oval
        diam_x=abs(coords[1]-coords[3])/2.0
        diam_y=abs(coords[0]-coords[2])/2.0
        rel_x=self.canvasx(event.x)-center_x
        rel_y=self.canvasy(event.y)-center_y
        dist2=(rel_x/diam_x)**2+(rel_y/diam_y)**2 # square of center distance
        if dist2>1.0 or dist2<0.25:
            return
        # find arcs
        items=[]
        angle=self.angle(rel_x,rel_y)
        for item in self.find_withtag('sector'):
            start=float(self.itemcget(item,'start'))
            extent=float(self.itemcget(item,'extent'))
            end=divmod(start+extent,360.0)[1]
            if divmod(abs(start-angle),360.0)[1]<1:
                items.append(item)
                self.itemconfigure(item,extent=-extent,start=end)
            if divmod(abs(end-angle),360.0)[1]<1:
                items.append(item)
            
        # no border
        if len(items)==0:
            return

        if len(items)>2:
            print "can not decide which arc to change"
            return

        if len(items)==1:
            print "no second border"
            return

        # compare extent-values
        extent_1=float(self.itemcget(items[0],'extent'))
        extent_2=float(self.itemcget(items[1],'extent'))
        self.pos_extent_item=self.neg_extent_item=0
        if extent_1>0:
            self.pos_extent_item=items[0]
            self.neg_extent_item=items[1]
        else:
            self.pos_extent_item=items[1]
            self.neg_extent_item=items[0]
        
        self.bind('<ButtonRelease-1>',self.handle_mouse_move_end)
        self.bind('<B1-Motion>',self.handle_mouse_move)

    def handle_mouse_move(self,event):
        coords=self.coords(self.current_item)
        rel_x=self.canvasx(event.x)-(coords[0]+coords[2])/2.0 #center of oval
        rel_y=self.canvasy(event.y)-(coords[1]+coords[3])/2.0 #center of oval
        angle=self.angle(rel_x,rel_y)
        start1=float(self.itemcget(self.pos_extent_item,'start'))
        start2=float(self.itemcget(self.neg_extent_item,'start'))

        # is that angle allowed?
        if (start1<start2):
            if angle>start1 and angle<start2:
                self.itemconfigure(self.pos_extent_item, extent=angle-start1)
                self.itemconfigure(self.neg_extent_item, extent=angle-start2)
                self.configure_description(self.pos_extent_item)
                self.configure_description(self.neg_extent_item)
            return

        if (start1>start2):
            if not (angle<start1 and angle>start2):
                if angle<start2:
                    self.itemconfigure(self.pos_extent_item, extent=angle+360.0-start1)
                    self.itemconfigure(self.neg_extent_item, extent=angle-start2)
                else:
                    self.itemconfigure(self.pos_extent_item, extent=angle-start1)
                    self.itemconfigure(self.neg_extent_item, extent=angle-360-start2)
                self.configure_description(self.pos_extent_item)
                self.configure_description(self.neg_extent_item)
            return

        
    def handle_mouse_move_end(self,event):
        self.unbind('<ButtonRelease-1>')
        self.unbind('<B1-Motion>')
        tags=self.gettags(self.pos_extent_item)
        key1=filter(lambda tag: tag[:4]=='tag_',tags)
        tags=self.gettags(self.neg_extent_item)
        key2=filter(lambda tag: tag[:4]=='tag_',tags)
        value1=abs(float(self.itemcget(self.pos_extent_item,
                                       'extent')))/360.0*self.ProbDict.sum
        value2=abs(float(self.itemcget(self.neg_extent_item,
                                       'extent')))/360.0*self.ProbDict.sum
        report_dict={}
        if len(key1)!=0:
            report_dict[key1[0][4:]]=value1
        else:
            # handle other
            report_dict['other']=value1
        if len(key2)!=0:
            report_dict[key2[0][4:]]=value2
        else:
            # handle other
            report_dict['other']=value2
        self.report_func('new value',report_dict)

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
