#!/usr/bin/env python
################################################################################
#
#       This file is part of Gato (Graph Algorithm Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/~gato
#
#	file:   ProbEditorDialogs.py
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
import tkSimpleDialog
import ProbEditorBasics
import ProbEditorWidgets

class pie_editor(ProbEditorWidgets.scroll_canvas,ProbEditorBasics.emission_editor):

    def report_func(self,what,dict):
        if what=='new value':
            self.data.emissions.update(dict)
            change=ProbEditorBasics.emission_change_data(self,self.data,dict)
            self.send_change(change)

    def __init__(self,master=None,data=None):
        ProbEditorWidgets.scroll_canvas.__init__(self,master,bg='white')
        ProbEditorBasics.emission_editor.__init__(self,data)

        self.pie=ProbEditorWidgets.e_pie_chart(self,self.data.emissions,
                                               self.data.order_list,
                                               self.data.color_list,
                                               self.report_func)
        # self.pie.pack(fill=Tkinter.BOTH,expand=1)
        self.create_window(0,0,window=self.pie,anchor=Tkinter.NW,width=350,height=300)


    def recieve_change(self,change):
        if change.__class__==ProbEditorBasics.emission_change_data:
            self.pie.update_position(self.data.emissions,self.data.order_list)
        elif change.__class__==ProbEditorBasics.emission_change_color:
            self.pie.update_colors(self.data.color_list,self.data.order_list)
        elif change.__class__==ProbEditorBasics.emission_change_order:
            self.pie.update_position(self.data.emissions,self.data.order_list)

class combined_editor(ProbEditorWidgets.scroll_canvas,ProbEditorBasics.emission_editor):
    """
    combines pie chart and bar chart
    """
    def __init__(self,master,emissions):
        ProbEditorBasics.emission_editor.__init__(self,emissions)
        ProbEditorWidgets.scroll_canvas.__init__(self,master,bg='white')
        self.body(self)

    def cmp_prob_val(self,a,b):
        if self.data[a]==self.data[b]:
            return cmp(a,b)
        else:
            return cmp(self.data[b],self.data[a])

    def report_pie(self,what,dict):
        if what!='new value':
            return
        if len(self.key_list2)>0:
            if dict.has_key('other'):
                other_val=dict['other']
                del dict['other']
                sum=0.0
                for key in self.key_list2[1:]:
                    sum=sum+self.data.emissions[key]
                for key in self.key_list2[1:]:
                    dict[key]=self.data.emissions[key]/sum*other_val
            self.bars.update_bars(dict)

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

        # sort for small quantities (i.e. <0.05 of sum)
        self.key_list1=[] # big ones
        self.sum1=0
        self.key_list2=[] # small ones
        self.sum2=0
        for k in self.data.order_list:
            value=self.data.emissions[k]
            if value>0.05*self.data.emissions.sum:
                self.key_list1.append(k)
                self.sum1+=value
            else:
                self.key_list2.append(k)
                self.sum2+=value

        # is Bar-Chart really necessary ?
        if len(self.key_list1)+len(self.key_list2)<5 or len(self.key_list2)<2:
            # put them together again
            self.key_list1=self.data.order_list
            self.key_list2=[]
            
        if len(self.key_list2)>0:
            # draw pie and bars
            bg_canvas=Tkinter.Canvas(self,
                                     bg='white',
                                     highlightthickness=0)
            # display first bar value in pie too
            self.key_list1.append(self.key_list2[0])
            self.pie=ProbEditorWidgets.e_pie_chart(self,
                                                   self.data.emissions,
                                                   self.key_list1,
                                                   self.data.color_list,
                                                   self.report_pie)
            pie_size=self.pie.bbox(Tkinter.ALL)
            pie_window=master.create_window(0,0,
                                            anchor=Tkinter.NW,
                                            window=self.pie,
                                            width=400,
                                            height=300)
            self.color_list2=self.data.color_list[len(self.key_list1)-1:]
            self.bars=ProbEditorWidgets.e_bar_chart_y(self,
                                                      self.data.emissions,
                                                      self.key_list2,
                                                      self.color_list2,
                                                      self.report_bar)
            bars_size=self.bars.bbox(Tkinter.ALL)
            bar_window=master.create_window(0,300,
                                            anchor=Tkinter.NW,
                                            window=self.bars,
                                            width=400,
                                            height=bars_size[3]+30)
        else:
            # only pie
            self.pie=ProbEditorWidgets.e_pie_chart(self,
                                                   self.data.emissions,
                                                   self.data.order_list,
                                                   self.data.color_list,
                                                   self.report_pie)
            pie_window=master.create_window(0,0,
                                            anchor=Tkinter.NW,
                                            window=self.pie,
                                            width=400,
                                            height=300)

    def recieve_change(self,change):
        if change.__class__==ProbEditorBasics.emission_change_data:
            self.pie.update_position(self.data.emissions,self.key_list1)
            if len(self.key_list2)>0:
                self.bars.update_bars(self.data.emissions)
        elif change.__class__==ProbEditorBasics.emission_change_color:
            self.pie.update_colors(self.data.color_list,self.data.order_list)
            if len(self.key_list2)>0:
                self.color_list2=self.data.color_list[len(self.key_list1)-1:]
                self.bars.config_bar_colors(self.data.emissions,
                                               self.data.color_list2,
                                               self.data.key_list2)
        elif change.__class__==ProbEditorBasics.emission_change_order:
            pass

class bar_editor(ProbEditorWidgets.scroll_canvas,ProbEditorBasics.emission_editor):

    def bar_report(self,what,k,v):
        if what=='new value':
            if abs(v-self.data.emissions[k])>self.data.precision:
                self.data.emissions[k]=v
                dict={k:v}
                change=ProbEditorBasics.emission_change_data(self,self.data,dict)
                self.send_change(change)
        

    def __init__(self,master,emissions):
        ProbEditorWidgets.scroll_canvas.__init__(self,master,bg='white')
        ProbEditorBasics.emission_editor.__init__(self,emissions)

        self.bars=ProbEditorWidgets.e_bar_chart_y(self,self.data.emissions,
                                                  self.data.order_list,
                                                  self.data.color_list,
                                                  self.bar_report)

        region=self.bars.bbox(Tkinter.ALL)
        #self.config(scrollregion=region)
        self.create_window(0,0,
                           anchor=Tkinter.NW,
                           window=self.bars,
                           width=region[2]-region[0]+10,
                           height=region[3]-region[1]+10)

    def recieve_change(self,change):
        if change.__class__==ProbEditorBasics.emission_change_data:
            self.bars.update_bars(change.dict)
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
        self.bars.pack(side=Tkinter.TOP,fill=Tkinter.BOTH,expand=1)

    def recieve_change(self,change):
        if change.__class__==ProbEditorBasics.emission_change_data:
            self.bars.bars.update_bars(change.dict)
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
        self.figures=Tkinter.Canvas(self,bg='white',highlightthickness=0)
        data_widget=self.figures.create_window((0,0),
                                               window=self.data_frame,
                                               anchor=Tkinter.NW)
        self.data_frame.lift(self.figures)
        self.update_idletasks()
        data_box=self.figures.bbox(data_widget)
        self.figures.config(width=data_box[2]-data_box[0]+5,
                            scrollregion=data_box)
        self.figures.pack(side=Tkinter.LEFT,fill=Tkinter.Y)
        self.scrollbar = Tkinter.Scrollbar(self,orient=Tkinter.VERTICAL,
                                           command=self.figures.yview)
        self.figures.config(yscrollcommand=self.scrollbar.set)
        self.bind('<Configure>',self.config_event)

    def config_event(self,event):
        """
        add or remove scrollbar
        """
        scrollr=self.figures.cget('scrollregion')
        scrollr=map(int,scrollr.split())
        # print "from config",scrollr
        if event.height>=(scrollr[3]-scrollr[1]):
            # print "y_scrollbar away"
            self.scrollbar.pack_forget()
        else:
            # print "y_scrollbar needed"
            self.scrollbar.pack(side=Tkinter.LEFT,fill=Tkinter.Y)

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


######################################################################################

class sum_editor(Tkinter.Frame,ProbEditorBasics.emission_editor):

    def __init__(self,master,data):
        """
        Widget with text "renorm to " and field for entries
        """

        ProbEditorBasics.emission_editor.__init__(self,data)
        Tkinter.Frame.__init__(self,master,bg='white',highlightthickness=0)
        # create headline
        Tkinter.Label(self,text='sum of probability values',bg='white').grid(row=0,
                                                                             column=0,
                                                                             columnspan=2)

        # create number-widget
        self.entry_width=int(math.ceil(-math.log10(self.data.precision)))
        self.sum=Tkinter.Entry(self,
                               width=self.entry_width,
                               highlightthickness=0,
                               bg='white')
        self.v=Tkinter.IntVar(self)
        if self.data.fixed_sum>0:
            sum_value=self.data.fixed_sum
            if abs(sum_value-100.0)<self.data.precision:
                # to 100 percent
                self.v.set(100)
            elif abs(sum_value-1.0)<self.data.precision:
                # to 1.0
                self.v.set(1)
            else:
                # to a custom value
                self.v.set(-1)
        else:
            self.v.set(0)
            sum_value=self.data.emissions.sum
        self.sum.insert(Tkinter.END,
                        str(round(sum_value,self.entry_width)),
                        )
        self.sum.bind('<Return>',self.renorm_event)

        Tkinter.Radiobutton(self,
                            text='100',
                            variable=self.v,
                            command=self.renorm_event,
                            value=100,
                            bg='white',
                            highlightthickness=0,
                            anchor=Tkinter.W).grid(column=0,row=1,sticky=Tkinter.EW)
        Tkinter.Radiobutton(self,
                            text='1',
                            variable=self.v,
                            command=self.renorm_event,
                            value=1,
                            bg='white',
                            highlightthickness=0,
                            anchor=Tkinter.W).grid(column=0,row=2,sticky=Tkinter.EW)
        Tkinter.Radiobutton(self,
                            text='custom',
                            variable=self.v,
                            command=self.renorm_event,
                            value=-1,
                            bg='white',
                            highlightthickness=0,
                            anchor=Tkinter.W).grid(column=0,row=3,sticky=Tkinter.EW)
        self.sum.grid(column=1,row=3,sticky=Tkinter.EW)
        Tkinter.Radiobutton(self,
                            text='free',
                            variable=self.v,
                            command=self.renorm_event,
                            value=0,
                            bg='white',
                            highlightthickness=0,
                            anchor=Tkinter.W).grid(column=0,row=4,sticky=Tkinter.EW)
        self.columnconfigure(3,weight=1)
        self.rowconfigure(5,weight=1)

    def get_sum_value(self):
        """
        get valid value from Entry Widget or set to actual sum
        """
        text=self.sum.get()
        try:
            new_sum=eval('float('+text+')')
            if new_sum<=0:
                new_sum=self.data.emmissions.sum
        except Exception, e:
            # nothing happens
            print e
            new_sum=self.data.emmissions.sum

        self.sum.delete(0,Tkinter.END)
        self.sum.insert(Tkinter.END,
                        str(round(new_sum,self.entry_width)),
                        )
        return new_sum

    def renorm_event(self,event=None):
        """
        do renorming of data
        """
        rb_sum=self.v.get()
        new_sum=0.0
        if rb_sum>=0:
            new_sum=float(rb_sum)
        else:
            # read from textfield
            new_sum=self.get_sum_value()
        # if necessary, force change-report to all
        self.data.fixed_sum=new_sum
        if new_sum>0 and \
           abs(self.data.emissions.sum-new_sum)>self.data.precision:
            self.data.emissions.renorm_to(new_sum)
            change=ProbEditorBasics.emission_change_data(self,
                                                         self.data,
                                                         self.data.emissions)
            self.send_change(change)

    def recieve_change(self,change):
        """
        if the sum changes and the custom constraint is not active,
        display the actual sum
        """
        if self.data.fixed_sum==0:
            sum_value=self.data.emissions.sum
            self.sum.delete(0,Tkinter.END)
            self.sum.insert(Tkinter.END,
                            str(round(sum_value,self.entry_width)),
                            )


###################################################################################

class emission_dialog(Tkinter.Toplevel,ProbEditorBasics.emission_editor):

    def __init__(self,parent,emissions,title):
        """
        the entire dialog
        """
        Tkinter.Toplevel.__init__(self,parent)
        ProbEditorBasics.emission_editor.__init__(self,emissions)
        self.status=''
        self.withdraw()
        self.title(title)
        self.emissions=emissions

        #buttons 
        w1 = Tkinter.Button(self, text="ok", width=10, command=self.ok,
                            default=Tkinter.ACTIVE)
        w2 = Tkinter.Button(self, text="cancel", width=10, command=self.cancel,
                            default=Tkinter.ACTIVE)

        self.bind("<Escape>", self.cancel)

        f=Tkinter.Frame(self)
        figures=figure_editor(f,self.emissions)

        tab_dict={}
        tab_dict['combined']=combined_editor(self,self.emissions)
        tab_dict['pie']=pie_editor(self,self.emissions)
        # tab_dict['bars']=bar_editor(self,self.emissions)
        tab_dict['bars']=scaled_bar_editor(self,self.emissions)
        tab_dict['sum']=sum_editor(self,self.emissions)
        tabs=ProbEditorWidgets.tab_frame(f,tab_dict)
        figures.pack(side=Tkinter.LEFT,fill=Tkinter.Y)
        tabs.pack(side=Tkinter.LEFT,expand=1,fill=Tkinter.BOTH)
        
        f.pack(side=Tkinter.TOP,expand=1,fill=Tkinter.BOTH)
        w2.pack(side=Tkinter.LEFT, expand=1, padx=5, pady=5)
        w1.pack(side=Tkinter.RIGHT, expand=1,padx=5, pady=5)
        self.initial_focus=w1

        self.update_idletasks()
        self.deiconify()
        self.wait_window(self)

    def ok(self,event=None):
        self.destroy()
        self.status='ok'
        
    def cancel(self,event=None):
        # to do: hier fehlt noch die Zurücksetzung auf alte Werte
        self.destroy()
        self.status='cancel'

    def success(self):
        return self.status

    def recieve_change(self,change):
        pass
