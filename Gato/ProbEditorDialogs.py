#!/usr/bin/env python
################################################################################
#
#       This file is part of Gato (Combinatorial Algorithm Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/~gato
#
#	file:   ProbEditorDialogs.py
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
import tkSimpleDialog
import ProbEditorBasics
import ProbEditorWidgets

class pie_editor(Tkinter.Frame,ProbEditorBasics.emission_editor):

    def report_func(self,what,dict):
        if what=='new value':
            self.data.emissions.update(dict)
            change=ProbEditorBasics.emission_change_data(self,self.data,dict)
            self.send_change(change)

    def __init__(self,master=None,data=None):
        Tkinter.Frame.__init__(self,master)
        ProbEditorBasics.emission_editor.__init__(self,data)

        self.pie=ProbEditorWidgets.e_pie_chart(self,self.data.emissions,
                                               self.data.order_list,
                                               self.data.color_list,
                                               self.report_func)
        self.pie.pack()

    def recieve_change(self,change):
        if change.__class__==ProbEditorBasics.emission_change_data:
            self.pie.update_position(self.data.emissions,self.data.order_list)
        elif change.__class__==ProbEditorBasics.emission_change_color:
            self.pie.update_colors(self.data.color_list,self.data.order_list)
        elif change.__class__==ProbEditorBasics.emission_change_order:
            self.pie.update_position(self.data.emissions,self.data.order_list)

class combined_editor(Tkinter.Frame,ProbEditorBasics.emission_editor):

    def __init__(self,master,emissions):
        ProbEditorBasics.emission_editor.__init__(self,emissions)
        Tkinter.Frame.__init__(self,master)
        self.body(self)

    def cmp_prob_val(self,a,b):
        if self.data[a]==self.data[b]:
            return cmp(a,b)
        else:
            return cmp(self.data[b],self.data[a])

    def report_pie(self,dict):
        if len(self.key_list2)>0:
            if dict.has_key('other'):
                other_val=dict['other']
                del dict['other']
                sum=0.0
                for key in self.key_list2[1:]:
                    sum=sum+self.data.emissions[key]
                for key in self.key_list2[1:]:
                    dict[key]=self.data.emissions[key]/sum*other_val
            self.bars.config_bar_height(dict)

        self.data.emissions.update(dict)
        change=ProbEditorBasics.emission_change_data(self,self.data,dict)
        self.send_change(change)

    def report_bar(self,what,k,v):
        if what=='new value':
            if abs(v-self.data.emissions[k])>self.data.precision:
                self.data.emissions[k]=v
                self.pie.update_position(self.data.emissions,self.key_list1)
                dict={k:v}
                change=ProbEditorBasics.emission_change_data(self,self.data,dict)
                self.send_change(change)

    def body(self,master):

        self.key_list1=[]
        self.key_list2=[]
        for k in self.data.order_list:
            value=self.data.emissions[k]
            if value>0.05:
                self.key_list1.append(k)
            else:
                self.key_list2.append(k)

        # Ist ein Bar-Chart auch nötig?
        if len(self.key_list1)+len(self.key_list2)<5 or len(self.key_list2)<2:
            # trennen in große und kleine Wkten hat keinen Sinn
            self.key_list1=self.data.order_list
            self.key_list2=[]
            
        if len(self.key_list2)>0:
            # draw pie and bars
            bg_canvas=Tkinter.Canvas(self,width=400,height=300,bg='white',
                                     highlightthickness=0,
                                     scrollregion=(0,0,400,1000))
            # display first bar value in pie too
            self.key_list1.append(self.key_list2[0])
            self.pie=ProbEditorWidgets.e_pie_chart(self,
                                                   self.data.emissions,
                                                   self.key_list1,
                                                   self.data.color_list,
                                                   self.report_pie)
            pie_window=bg_canvas.create_window(0,0,anchor=Tkinter.NW,window=self.pie)
            self.color_list2=self.data.color_list[len(self.key_list1)-1:]
            self.bars=ProbEditorWidgets.e_bar_chart_y(self,
                                                      self.data.emissions,
                                                      self.key_list2,
                                                      self.color_list2,
                                                      self.report_bar)
            bar_window=bg_canvas.create_window(0,400,anchor=Tkinter.NW,window=self.bars)
            region=bg_canvas.bbox(Tkinter.ALL)
            bg_canvas.pack(side=Tkinter.LEFT,expand=1,fill=Tkinter.BOTH)
            scrollbar = Tkinter.Scrollbar(self,orient=Tkinter.VERTICAL,
                                          command=bg_canvas.yview)
            bg_canvas.config(yscrollcommand=scrollbar.set,
                             scrollregion=region)
            scrollbar.pack(fill=Tkinter.Y,expand=1)
        else:
            # only pie
            self.pie=ProbEditorWidgets.pie_chart(self,
                                                 self.data.emissions,
                                                 self.data.order_list,
                                                 self.data.color_list)
            self.pie.pack(expand=1,fill=Tkinter.BOTH)


    def recieve_change(self,change):
        if change.__class__==ProbEditorBasics.emission_change_data:
            self.pie.update_position(self.data.emissions,self.key_list1)
            if len(self.key_list2)>0:
                self.bars.config_bar_height(self.data.emissions)
        elif change.__class__==ProbEditorBasics.emission_change_color:
            self.pie.update_colors(self.data.color_list,self.data.order_list)
            if len(self.key_list2)>0:
                self.color_list2=self.data.color_list[len(self.key_list1)-1:]
                self.bars.config_bar_colors(self.data.emissions,
                                               self.data.color_list2,
                                               self.data.key_list2)
        elif change.__class__==ProbEditorBasics.emission_change_order:
            pass


class bar_editor(Tkinter.Frame,ProbEditorBasics.emission_editor):

    def bar_report(self,what,k,v):
        if what=='new value':
            if abs(v-self.data.emissions[k])>self.data.precision:
                self.data.emissions[k]=v
                dict={k:v}
                change=ProbEditorBasics.emission_change_data(self,self.data,dict)
                self.send_change(change)
        

    def __init__(self,master,emissions):
        Tkinter.Frame.__init__(self,master)
        ProbEditorBasics.emission_editor.__init__(self,emissions)

        self.bars=ProbEditorWidgets.e_bar_chart_y(self,self.data.emissions,
                                                  self.data.order_list,
                                                  self.data.color_list,
                                                  self.bar_report)

        scrollbar = Tkinter.Scrollbar(self,orient=Tkinter.VERTICAL,
                                      command=self.bars.yview)
        region=self.bars.bbox(Tkinter.ALL)
        self.bars.config(height=300,
                         scrollregion=region,
                         yscrollcommand=scrollbar.set)

        self.bars.pack(side=Tkinter.LEFT)
        scrollbar.pack(fill=Tkinter.Y,expand=1)

    def recieve_change(self,change):
        if change.__class__==ProbEditorBasics.emission_change_data:
            self.bars.config_bar_height(change.dict)
        elif change.__class__==ProbEditorBasics.emission_change_color:
            self.bars.config_bar_color(change.data.color,
                                            change.data.order_list)
        elif change.__class__==ProbEditorBasics.emission_change_order:
            self.bars.config_bar_order(change.data.order_list)

class scaled_bar_editor(Tkinter.Frame,ProbEditorBasics.emission_editor):

    def bar_report(self,what,k,v):
        if what=='new value':
            if abs(v-self.data.emissions[k])>self.data.precision:
                self.data.emissions[k]=v
                dict={k:v}
                change=ProbEditorBasics.emission_change_data(self,self.data,dict)
                self.send_change(change)
        

    def __init__(self,master,emissions):
        Tkinter.Frame.__init__(self,master)
        ProbEditorBasics.emission_editor.__init__(self,emissions)

        self.bars=ProbEditorWidgets.bar_chart_with_scale(self,self.data.emissions,
                                                         self.data.order_list,
                                                         self.data.color_list,
                                                         self.bar_report)
        self.bars.pack()

    def recieve_change(self,change):
        if change.__class__==ProbEditorBasics.emission_change_data:
            self.bars.bars.config_bar_height(change.dict)
        elif change.__class__==ProbEditorBasics.emission_change_color:
            self.bars.bars.config_bar_color(change.data.color,
                                       change.data.order_list)
        elif change.__class__==ProbEditorBasics.emission_change_order:
            self.bars.bars.config_bar_order(change.data.order_list)

class figure_editor(Tkinter.Frame,ProbEditorBasics.emission_editor):

    def val_entry(self,widget,key):
        text=widget.get()
        try:
            new_value=eval('float('+text+')')
        except Exception, e:
            self.update_values({key:self.data.emissions[key]})
        else:
            if abs(new_value-self.data.emissions[key])>self.data.precision:
                if new_value>=0:
                    self.data.emissions[key]=new_value
                    dict={key:new_value}
                    self.update_values(dict)
                    change=ProbEditorBasics.emission_change_data(self,self.data,dict)
                    self.send_change(change)
                else:
                    self.update_values({key:self.data.emissions[key]})
        return 1

    def return_pressed(self,widget,key):
        self.val_entry(widget,key)
        widget.tk_focusNext().focus_set()

    def __init__(self,master,emissions):
        Tkinter.Frame.__init__(self,master)
        ProbEditorBasics.emission_editor.__init__(self,emissions)

        self.entry_dict={}
        self.data_frame=Tkinter.Frame(self,bg='white')
        row=0
        self.entry_width=int(math.ceil(-math.log10(self.data.precision)))

        for key in self.data.order_list:
            text=Tkinter.Label(self.data_frame,text=key,bg='white')
            edit_value=Tkinter.Entry(self.data_frame,
                                     width=self.entry_width+3,
                                     bg='white')
            val_func=lambda s=self,w=edit_value,k=key:s.val_entry(w,k)
            edit_value.configure(validate='focusout',vcmd=val_func)
            event_func=lambda e,s=self,w=edit_value,k=key:s.return_pressed(w,k)
            edit_value.bind('<Return>',event_func)
            text.grid(row=row,column=0)
            edit_value.grid(row=row,column=1)
            self.entry_dict[key]=edit_value
            row=row+1

        self.update_values(emissions.emissions)
        figures=Tkinter.Canvas(self,bg='white',highlightthickness=0)
        data_widget=figures.create_window((0,0),
                                          window=self.data_frame,
                                          anchor=Tkinter.NW)
        self.data_frame.lift(figures)
        self.update_idletasks()
        data_box=figures.bbox(data_widget)
        figures.config(width=data_box[2]-data_box[0]+5,
                       scrollregion=data_box)
        figures.pack(side=Tkinter.LEFT,fill=Tkinter.Y)
        scrollbar = Tkinter.Scrollbar(self,orient=Tkinter.VERTICAL,
                                      command=figures.yview)
        figures.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=Tkinter.LEFT,fill=Tkinter.Y)

    def update_values(self,dict):
        for key in dict.keys():
            widget=self.entry_dict[key]
            widget.delete(0,Tkinter.END)
            value_text=str(round(dict[key],self.entry_width))
            widget.insert(Tkinter.END,value_text)

    def update_position(self,change):
        pass
##        for key in change.data.order_list:
##            self.data_frame.forget(entry_dict[key])
            

    def recieve_change(self,change):
        if change.__class__==ProbEditorBasics.emission_change_data:
            self.update_values(change.dict)
        elif change.__class__==ProbEditorBasics.emission_change_color:
            pass
        elif change.__class__==ProbEditorBasics.emission_change_order:
            self.update_position(change)

###################################################################################

class emission_dialog(Tkinter.Toplevel,ProbEditorBasics.emission_editor):

    def __init__(self,parent,emissions,title):
        Tkinter.Toplevel.__init__(self,parent)
        ProbEditorBasics.emission_editor.__init__(self,emissions)
        self.withdraw()
        self.title(title)
        self.emissions=emissions

        w = Tkinter.Button(self, text="Quit", width=10, command=self.ok,
                           default=Tkinter.ACTIVE)
        self.bind("<Escape>", self.cancel)
        self.initial_focus=w

        figures=figure_editor(self,self.emissions)

        tab_dict={}
        tab_dict['combined']=combined_editor(self,self.emissions)
        tab_dict['pie']=pie_editor(self,self.emissions)
        tab_dict['bars']=bar_editor(self,self.emissions)
        tab_dict['scaled_bars']=scaled_bar_editor(self,self.emissions)
        tabs=ProbEditorWidgets.tab_frame(self,tab_dict)
        empty=Tkinter.Frame(self)

        w.pack(side=Tkinter.BOTTOM, padx=5, pady=5)
        figures.pack(side=Tkinter.LEFT,fill=Tkinter.Y,expand=1)
        tabs.pack(side=Tkinter.LEFT,expand=1,fill=Tkinter.BOTH)        
        empty.pack(fill=Tkinter.BOTH)

        self.update_idletasks()
        self.deiconify()
        self.wait_window(self)

    def ok(self,event=None):
        self.destroy()
        
    def cancel(self,event=None):
        self.destroy()

    def recieve_change(self,change):
        pass
