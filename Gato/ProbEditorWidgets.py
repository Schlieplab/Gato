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
        key=ProbEditorBasics.tag_to_key(tab_name)
        if key!=self.actual_tab:
            self.change_tab(key)

    def change_tab(self,key):
        # change tabs
        if self.actual_tab!=None:
            poly_list=self.tabs.find_withtag('tab_poly_'+ProbEditorBasics.key_to_tag(self.actual_tab))
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
            self.widget_dict[self.actual_tab].forget()
        self.widget_dict[key].pack(side=Tkinter.BOTTOM,in_=self,
                                   expand=1,fill=Tkinter.BOTH)
        self.actual_tab=key

    def __init__(self,master,widget_dict,start=None):
        Tkinter.Frame.__init__(self,master,width=300,height=300)
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

            # Widget auf Start-Größe
            # widget_dict[key].configure(width=300)
            # widget_dict[key].configure(height=300)
            # nutzt nichts...

        # setze aktuellen Tab
        self.actual_tab=None
        if start!=None:
            self.change_tab(start)
        else:
            self.change_tab(key_list[0])

        self.tabs.pack(side=Tkinter.TOP,fill=Tkinter.X)

#####################################################################################
class flyout_decoration:

    def __init__(self,info_function):
        # prepare bindings
        self.add_bindings(info_function)

    def add_bindings(info_function):
        pass

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
#                                width=self.text_length+self.bar_length+2*self.x_margin,
#                                height=len(keys)*self.bar_step+self.text_length+2*self.y_margin
                                )
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

    def get_max_value(self):
        dict=self.get_bar_values()
        max_value=0
        max_key=''
        for k in dict.keys():
            if dict[k]>self.max_value:
                max_value=dict[k]
                max_key=dict[k]
        return (max_key,max_value)

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

class scale(Tkinter.Canvas):
        
    def __init__(self,master,start_x,factor,max_value=None):
        Tkinter.Canvas.__init__(self,
                                master,
                                height=25,
                                bg='white',
                                highlightthickness=0
                                )
        self.bind('<Configure>',self.configure_event)
        self.draw_arrow(start_x,factor,max_value)

    def configure_event(self,event):
        print 'conf',event.width

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
        x_pos=0.0
        while x_pos<=max_value:
            pixel_x=start_x+x_pos*factor
            self.create_line(pixel_x,15,pixel_x,25,
                                   tags=('tic'))
            self.create_text(pixel_x,15,text=repr(x_pos)[:3],
                             anchor=Tkinter.S,
                             tags=('tic','text'))
            x_pos=x_pos+scale_frac


####################################################################################

class bar_chart_with_scale(Tkinter.Frame):

    def __init__(self,master,prob_dict,keys,colors,report_func):
        Tkinter.Frame.__init__(self,master)
        self.bars=e_bar_chart_y(self,prob_dict,keys,colors,self.bar_report)
        scale_start_x=self.bars.x_margin+self.bars.text_length
        factor=self.bars.bar_factor
        scale_max=self.bars.max_value
        self.scale=scale(self,scale_start_x,factor,scale_max)

        self.report_func=report_func
        scrollbar = Tkinter.Scrollbar(self,orient=Tkinter.VERTICAL,
                                      command=self.bars.yview)
        region=self.bars.bbox(Tkinter.ALL)
        sregion=(0,0,region[2],region[3])
        self.bars.config(height=300,
                         scrollregion=sregion,
                         yscrollcommand=scrollbar.set)


        empty=Tkinter.Frame(self,bg='white')
        self.scale.grid(column=0,row=0,sticky=Tkinter.E+Tkinter.W)
        self.bars.grid(column=0,row=1,sticky=Tkinter.E+Tkinter.W+Tkinter.N+Tkinter.S)
        scrollbar.grid(column=1,row=1,sticky=Tkinter.N+Tkinter.S)
        empty.grid(column=1,row=0,sticky=Tkinter.E+Tkinter.W+Tkinter.N+Tkinter.S)
        Tkinter.Frame.columnconfigure(self,0,weight=1)
        Tkinter.Frame.rowconfigure(self,1,weight=1)
        self.move_count=1

    def bar_report(self,what,key,value):
        if what=='move':
            self.move_count+=1
        if what=='max reached' and self.move_count>0:
            actual_values=self.bars.get_bar_values()
            self.bars.bar_factor/=2
            self.bars.config_bar_height(actual_values)
            self.scale.config_scale(self.bars.x_margin+self.bars.text_length,
                                    self.bars.bar_factor,
                                    self.bars.bar_length/self.bars.bar_factor)
            self.move_count=0
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

class pie_chart(Tkinter.Canvas):

    def __init__(self,master,prob_dict,keys,colors):
        self.ProbDict=prob_dict
        self.arc_box=(100,50,300,250)
        self.key_list=keys
        Tkinter.Canvas.__init__(self,master,bg='white',highlightthickness=0)
        self.draw_arcs(self.arc_box,keys,colors)

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
                # fast voller Kreis
                extent_angle=359.9
            # Volle Kreise zeichnen
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

    def move_start(self,event):
        # find sector belonging to handle
        self.current_item=self.find_withtag(Tkinter.CURRENT)[0]
        self.current_tag=filter(lambda t:t[:4]=='tag_' or t=='other',
                                self.gettags(self.current_item))[0]
        self.current_arc1=filter(lambda i,s=self:s.type(i)=='arc',
                                 self.find_withtag(self.current_tag))
        # find neighbour sector
        angle_pos=float(self.itemcget(self.current_arc1,'start'))
        sectors=self.find_withtag('sector')
        self.current_arc2=[]
        for sector in sectors:
            extent_angle=float(self.itemcget(sector,'extent'))
            start_angle=float(self.itemcget(sector,'start'))
            angle_diff=divmod(start_angle+extent_angle-angle_pos,360.0)[1]
            if angle_diff<0.1 or angle_diff>359.9:
                self.current_arc2.append(sector)

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

    def move_end(self,event):
        # no events!
        self.unbind('<B1-Motion>')
        self.unbind('<ButtonRelease-1>')
        # read new values from graphic
        tags=self.gettags(self.current_arc1)
        key1=filter(lambda tag: tag[:4]=='tag_',tags)
        tags=self.gettags(self.current_arc2)
        key2=filter(lambda tag: tag[:4]=='tag_',tags)
        value1=abs(float(self.itemcget(self.current_arc1,
                                       'extent')))/360.0*self.ProbDict.sum
        value2=abs(float(self.itemcget(self.current_arc2,
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
        self.current_tag=None
        self.current_key=None


    def init_handles(self):
        sectors=self.find_withtag('sector')
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
                                  fill='black',tags=('handle',tag))
            self.tag_bind(oval,'<Button-1>',self.move_start)

    def update_handles(self):
        sectors=self.find_withtag('sector')
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
