#!/usr/bin/env python2.0

import math
import Tkinter
import ProbEditorBasics
import ProbEditorWidgets

class plot_object:
    """
    object that can be plotted
    """

    def __init__(self,color=None):
        """
        init color
        """
        self.color=color

    def resolution(self,x_1,x_2):
        """
        needed resolution for this object in the given interval
        """
        return 10

    def sample_values(self,x_1,x_2):
        """
        values needed for a good plots
        """
        sample=[]
        res=self.resolution(x1,x2)
        if res<2:
            res=2
        step_diff=(x2-x1)/(res-1)
        for step in range(0,res):
            x=step*step_diff+x1
            sample.append(x)
        return sample

    def get_values(self, list_x):
        """
        calculate values from a list
        """
        list_y=[]
        for x in list_x:
            list_y.append((x,self.get_value(x)))
        return list_y

    def get_value(self,x):
        """
        get one value
        """
        return None

    def get_points(self,x1,x2):
        """
        calculates sufficient pairs for a spline approximation
        """
        return self.get_values(self.get_sample_values(x1,x2))

    def get_color(self):
        """
        get saved color
        """
        return self.color

    def set_color(self,color=None):
        """
        save color
        """
        self.color=color
        return color

    def __repr__(self):
        return "plot_object"

class sum_function(plot_object):
    """
    weighted sum of plot objects,
    not very smart straight-forward-implementation
    """

    def __init__(self,sum_list=[],weight_list=None,color=None):
        """
        init list
        """
        plot_object.__init__(self,color)
        self.sum_list=sum_list[:]
        if weight_list==None:
            self.weight_list=[1.0]*len(self.sum_list)
        else:
            self.weight_list=weight_list[:len(obj_list)-1]
            self.weight_list[len(weight_list):len(obj_list)-1]=0.0
            
    def get_value(self,x):
        """
        get one value
        """
        sum=0.0
        for i in range(0,len(self.sum_list)):
            if self.weight_list[i]!=0:
                sum+=self.sum_list[i].get_value(x)*self.weight_list[i]
        return sum

    def get_sample_values(self,x1,x2):
        x_list=[]
        for i in range(0,len(self.sum_list)):
            if self.weight_list[i]!=0:
                x_list+=self.sum_list[i].get_sample_values(x1,x2)

        x_list.sort()
        # delete double values (epsilon<(x1-x2)/400)
        epsilon=abs(x1-x2)/400.0

        i=1
        while i<len(x_list):
            if abs(x_list[i]-x_list[i-1])<epsilon:
                del x_list[i]
            else:
                i+=1

        return x_list

class line_function(plot_object):

    def __init__(self,a=0,b=0,color=None):
        "init parameters"
        plot_object.__init__(self,color)
        self.a=float(a)
        self.b=float(b)

    def get_value(self,x):
        "simple evaluation: linear function"
        return self.a*x+self.b

    def resolution(self,x1,x2):
        "only 2 points needed"
        return 2

    def __repr__(self):
        return "line_function: x->%f*x+%f"%(self.a,self.b)

class gauss_function(plot_object):
    """
    gauss function
    """

    def __init__(self,mu=0,sigma=1,a=1,color=None):
        "init parameters"
        plot_object.__init__(self,color)
        self.mu=float(mu)
        self.sigma=float(sigma)
        self.a=float(a)

    def get_sample_values(self,x1,x2):
        """
        make different resolutions
        """
        if x1>x2:
            x_max=x1
            x_min=x2
        else:
            x_max=x2
            x_min=x1

        # epiric values
        res_map={5: 3, 4: 3, 3: 3,2: 5,1: 5, 0: 7}
        res_map_start=5.0
        # renormed distances
        n_min=(x_min-self.mu)/self.sigma
        n_max=(x_max-self.mu)/self.sigma
        n_step=(n_max-n_min)/10.0

        n_list=[]
        n=n_min

        # boring range <5
        while n<n_max and n<-res_map_start:
            n_list.append(n)
            n+=n_step

        # interesting range
        n=max(-res_map_start,n_min)
        while n<n_max and n<res_map_start:
            n_list.append(n)
            n+=1.0/float(res_map[abs(int(n))])

        # boring range >5
        while n<n_max:
            n_list.append(n)
            n+=n_step

        n_list.append(n_max)

        # convert n_list to x_list
        i=0
        l=len(n_list)
        while i<l:
            n_list[i]=n_list[i]*self.sigma+self.mu
            i+=1

        return n_list

    def get_value(self,x):
        "gauss function"
        n=(float(x)-self.mu)/self.sigma
        factor=self.a/self.sigma/math.sqrt(2.0*math.pi)
        return math.exp(n*n/-2.0)*factor

    def __repr__(self):
        return "gauss_function: x->%f/(%f*sqrt(2*pi))*exp(-(x-%f)**2/2*%f**2)"%(self.a,self.sigma,self.mu,self.sigma)

class plot_canvas(Tkinter.Canvas):

    def __init__(self,master,**cnf):
        Tkinter.Canvas.__init__(self,master,**cnf)
        self.configured=0

        # defined elsewhere
        self.scale_x=1.0
        self.scale_y=1.0
        self.orig_x=0.0
        self.orig_y=0.0

        # init list of pairs : (plotted objects,item_number)
        self.plot_objects=[]

        # get sizes
        self.bind('<Configure>',self.configure_event)

    def configure_event(self,event):
        """
        configuration of canvas, scales and plots
        """
        self.plot_box=(30,10,event.width-10,event.height-30)
        self.scale_offset_x=self.plot_box[0]
        self.scale_offset_y=self.plot_box[3]
        self.scale_end_x=self.plot_box[2]
        self.scale_end_y=self.plot_box[1]
        (self.end_x,self.end_y)=self.canvasxy_to_xy((self.scale_end_x,self.scale_end_y))
        if self.configured==0:
            self.create_scale()
        else:
            self.configure_scale()

        if self.plot_objects:
            self.replot()

    def xy_to_canvasxy(self,xy):
        """
        converts xy Pairs to pixle coordinates on the plot canvas
        """
        return ((xy[0]-self.orig_x)*self.scale_x+self.scale_offset_x,
                (xy[1]-self.orig_y)*-self.scale_y+self.scale_offset_y)

    def canvasxy_to_xy(self,canvasxy):
        """
        converts canvas pixle coords to xy Pairs
        """
        return ((canvasxy[0]-self.scale_offset_x)/self.scale_x+self.orig_x,
                (canvasxy[1]-self.scale_offset_y)/-self.scale_y+self.orig_y)

    def create_scale(self):
        """
        creates and configures scale-arrows and provides tics
        """
        self.scale_item_x=self.create_line(self.scale_offset_x,self.scale_offset_y,
                                           self.scale_end_x,self.scale_offset_y,
                                           arrow=Tkinter.LAST,
                                           tags=('x_arrow'))
        self.scale_item_y=self.create_line(self.scale_offset_x,self.scale_offset_y,
                                           self.scale_offset_x,self.scale_end_y,
                                           arrow=Tkinter.LAST,
                                           tags=('y_arrow'))
        self.new_tics()
        self.configured=1

    def configure_scale(self):
        """
        when all coordinates are set, the graphic items were configured
        """
        #configure arrows
        self.coords(self.scale_item_x,self.scale_offset_x,self.scale_offset_y,
                    self.scale_end_x,self.scale_offset_y)
        self.coords(self.scale_item_y,self.scale_offset_x,self.scale_offset_y,
                    self.scale_offset_x,self.scale_end_y)
        self.del_tics()
        self.new_tics()


    def calculate_tic_distance(self,scale,length):
        """
        calculates distance between tics by:

        - scaling factor (pixel per unit)

        - length (pixel)
        """

        interval=length/scale
        sign=interval/abs(interval)
        interval=abs(interval)

        dist=10**math.floor(math.log10(interval)-1)
        if dist*scale>20:
            return dist*sign

        if dist*scale*2>20:
            return dist*2*sign

        if dist*scale*5>20:
            return dist*5*sign

        return dist*10*sign

    def del_tics(self):
        """
        delete tics
        """
        for item in self.tic_list:
            self.delete(item)
        self.tic_list=[]
        
    def new_tics(self):    
        """
        new tics
        """
        self.tic_list=[]
        # x tics
        dist=self.calculate_tic_distance(self.scale_x,
                                         self.scale_end_x-self.scale_offset_x)
        prec=1-math.floor(math.log10(dist))
        pos_x=math.floor(self.orig_x/dist)*dist
        while pos_x<=self.end_x:
            pixel_x=pos_x*self.scale_x+self.scale_offset_x
            tic=self.create_line(pixel_x,
                                 self.scale_offset_y-2,
                                 pixel_x,
                                 self.scale_offset_y+2)
            text=self.create_text(pixel_x,self.scale_offset_y+2,
                                  anchor=Tkinter.N,
                                  text=str(round(pos_x,prec)))
            self.tic_list.append(tic)
            self.tic_list.append(text)
            pos_x+=dist


        # y tics
        dist=self.calculate_tic_distance(self.scale_y,
                                         self.scale_end_y-self.scale_offset_y)
        pos_y=math.floor(self.orig_y/dist)*dist
        while pos_y<=self.end_y:
            pixel_y=-pos_y*self.scale_y+self.scale_offset_y
            tic=self.create_line(self.scale_offset_x-2,
                                 pixel_y,
                                 self.scale_offset_x+2,
                                 pixel_y)
            text=self.create_text(self.scale_offset_x-2,pixel_y,
                                  anchor=Tkinter.E,
                                  text=str(round(pos_y,prec)))
            self.tic_list.append(tic)
            self.tic_list.append(text)
            pos_y-=dist

    def replot(self):
        """
        redraws all plot-objects
        """
        for object in self.plot_objects:
            self.configure_plot_item(object[1],object[0])


    def replot_object(self,object):
        """
        replot a single object
        """
        o=self.find_plot_object(object)
        if o==None:
            return
        self.configure_plot_item(self.plot_objects[o][1],self.plot_objects[o][0])
        
    def create_plot_item(self,plot_object):
        return self.create_line(self.get_coords(plot_object),
                                smooth=0,
                                fill=plot_object.get_color())

    def configure_plot_item(self,item,plot_object):
        self.coords(item,tuple(self.get_coords(plot_object)))
        self.itemconfigure(item,fill=plot_object.get_color())

    def get_coords(self,plot_object):
        if self.configured==0:
            # nothing to do
            return [0,0,0,0]
        coord_list=[]
        points=plot_object.get_points(self.orig_x,self.end_x)
        for point in points:
            coord_list.append((point[0]-self.orig_x)*self.scale_x+self.scale_offset_x)
            coord_list.append((point[1]-self.orig_y)*-self.scale_y+self.scale_offset_y)
        return coord_list
        
    def find_plot_object(self,object):
        """
        finds the position of the plot object in the list,
        returns None, if it doesn't exist
        """
        i=0
        length=len(self.plot_objects)
        while i<length and self.plot_objects[i][0]!=object:
            i+=1
        if i>=length:
            i=None
        return i

    def add_plot_object(self,plot_object):
        """
        adds a plot object, if it does not allready exist 
        """
        if self.find_plot_object(plot_object)!=None:
            # exists!
            return
        item=self.create_plot_item(plot_object)
        self.plot_objects.append((plot_object,item))
            
    def remove_plot_object(self,plot_object):
        """
        removes a plot_object, if it existst in the list
        and erases the line from canvas
        """
        object_index=self.find_plot_object(plot_object)
        if object_index==None:
            #doesn't exist
            return
        self.delete(self.plot_objects[object_index])
        del self.plot_objects[object_index]

class gauss_editor(Tkinter.Frame):

    def __init__(self,master,**cnf):
        """
        first demonstration of continous prob editor
        """
        Tkinter.Frame.__init__(self,master,cnf)
        self.plot_area=plot_canvas(self,bg='white')
        self.edit_area=Tkinter.Canvas(self,bg='white')
        self.edit_area.bind('<Configure>',self.configure_handles)

        self.plot_list=[]
        self.mu_handle_list=[]
        self.sigma_handle_list=[]
        
        #some nonsence data
        self.plot_area.scale_y=100.0
        self.plot_area.scale_x=50.0        

        d={}
        for i in range(1,5):
            o=gauss_function(mu=i*2.0,sigma=1.0,a=i/2.0,color='blue')
            self.plot_list.append(o)
            self.plot_area.add_plot_object(o)
            d[str(i)]=i/2.0
        self.dict=ProbEditorBasics.ProbDict(d)

        self.plot_sum=sum_function(sum_list=self.plot_list,color='red')
        self.plot_area.add_plot_object(self.plot_sum)
        self.create_handles()

        self.pie=ProbEditorWidgets.e_pie_chart(self,
                                               self.dict,
                                               self.dict.keys(),
                                               ['red','green','blue','yellow'],
                                               self.pie_report)
        self.pie.configure(width=400,height=400)
        self.plot_area.configure(width=550)

        self.edit_area.grid(row=1,column=0,sticky=Tkinter.NSEW)
        self.plot_area.grid(row=0,column=0,sticky=Tkinter.NSEW)
        self.pie.grid(row=0,rowspan=2,column=1,sticky=Tkinter.NSEW)
        self.rowconfigure(0,minsize=50,weight=1)
        self.columnconfigure(0,minsize=50,weight=1)

    def pie_report(self,what,dict):
        """
        """
        if what=='new value' or what=='move value':
            for k in dict.keys():
                i=int(k)-1
                self.plot_list[i].a=dict[k]
                self.plot_area.replot_object(self.plot_list[i])
            self.plot_area.replot_object(self.plot_sum)

    def create_handles(self):
        """
        creates handles for objects in list
        """
        pos=0
        self.edit_area.configure(height=10*len(self.plot_list))
        for o in self.plot_list:
            if o.__class__.__name__=='gauss_function':
                if self.plot_area.configured!=0:
                    x=self.plot_area.xy_to_canvasxy((o.mu,0))[0]
                    mu_coords=(x-1,pos,x+1,pos+10)
                    x1=self.plot_area.xy_to_canvasxy((o.mu-o.sigma,0))[0]
                    x2=self.plot_area.xy_to_canvasxy((o.mu+o.sigma,0))[0]
                    sigma_coords=(x1,pos+3,x1,pos+8,x1,pos+5,
                                  x2,pos+5,x2,pos+8,x2,pos+3)
                else:
                    mu_coords=(pos,0,pos+10,0)
                    sigma_coords=(0,pos+3,0,pos+8)
                mu_handle=self.edit_area.create_rectangle(mu_coords,
                                                          fill='grey',
                                                          outline='grey')
                sigma_handle=self.edit_area.create_line(sigma_coords,fill='black')
                self.edit_area.tag_bind(mu_handle,
                                        '<Button-1>',
                                        self.handle_move_start)
                self.edit_area.tag_bind(sigma_handle,
                                        '<Button-1>',
                                        self.handle_move_start)
                self.mu_handle_list.append(mu_handle)
                self.sigma_handle_list.append(sigma_handle)
            else:
                print "no handle for %s"%(o.__class__.__name__)
            pos+=10

    def configure_handle(self,index):
        """
        configure a single handle
        """
        object=self.plot_list[index]
        pos=index*10
        if object.__class__.__name__=='gauss_function':
            x=self.plot_area.xy_to_canvasxy((object.mu,0))[0]
            x1=self.plot_area.xy_to_canvasxy((object.mu-object.sigma,0))[0]
            x2=self.plot_area.xy_to_canvasxy((object.mu+object.sigma,0))[0]
            mu_coords=(x-1,pos,x+1,pos+10)
            sigma_coords=(x1,pos+3,x1,pos+8,x1,pos+5,
                          x2,pos+5,x2,pos+8,x2,pos+3)
            self.edit_area.coords(self.mu_handle_list[index],mu_coords)
            self.edit_area.coords(self.sigma_handle_list[index],sigma_coords)
        else:
            print "no handle for %s"%(o.__class__.__name__)


    def configure_handles(self,event):
        """
        configure handles for gauss functions
        """
        if self.plot_area.configured==0:
            return
        i=0
        self.edit_area.configure(height=10*len(self.plot_list))
        while i<len(self.plot_list):
            self.configure_handle(i)
            i+=1

    def handle_move_start(self,event):
        """
        start moving one handle
        """
        self.this_item=self.edit_area.find_withtag(Tkinter.CURRENT)[0]
        if self.this_item in self.mu_handle_list:
            self.this_index=self.mu_handle_list.index(self.this_item)
            self.this_handle_type='mu'
            self.this_object=self.plot_list[self.this_index]
        elif self.this_item in self.sigma_handle_list:
            self.this_index=self.sigma_handle_list.index(self.this_item)
            self.this_handle_type='sigma'
            self.this_object=self.plot_list[self.this_index]
            cx=self.edit_area.canvasx(event.x)
            x=self.plot_area.canvasxy_to_xy((cx,0))[0]
            if abs(x-self.this_object.mu)<0.9*self.this_object.sigma:
                return
        else:
            print "can not find handle"
        self.edit_area.tag_bind(self.this_item,
                                '<B1-Motion>',
                                self.handle_move)
        self.edit_area.tag_bind(self.this_item,
                                '<ButtonRelease-1>',
                                self.handle_move_end)

    def handle_move(self,event):
        """
        move with handle
        """
        cx=self.edit_area.canvasx(event.x)
        x=self.plot_area.canvasxy_to_xy((cx,0))[0]
        if self.this_handle_type=='mu':
            self.this_object.mu=x
        elif self.this_handle_type=='sigma':
            if x==self.this_object.mu:
                pass
            else:
                self.this_object.sigma=abs(x-self.this_object.mu)
        else:
            print "no handle type"
        self.plot_area.replot_object(self.this_object)
        self.plot_area.replot_object(self.plot_sum)
        self.configure_handle(self.this_index)

    def handle_move_end(self,event):
        """
        stop moving
        """
        self.edit_area.tag_unbind(self.this_item,'<B1-Motion>')
        self.edit_area.tag_unbind(self.this_item,'<Button-Release-1>')

if __name__=='__main__':
    root=Tkinter.Tk()
    editor=gauss_editor(root,width=300,height=300)

    # fast quit by <Escape>
    root.bind('<Escape>',lambda e:e.widget.quit())
    editor.pack(expand=1,fill=Tkinter.BOTH)
    root.mainloop()
