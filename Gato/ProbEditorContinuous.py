#!/usr/bin/env python
################################################################################
#
#       This file is part of Gato (Combinatorial Algorithm Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/~gato
#
#	file:   ProbEditorContinuous.py
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
import gsl.rng
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

    def set_parameters(self,values):
        """
        sets parameters from a tuple
        """
        pass

    def get_parameters(self):
        """
        gets parameters as a tuple
        """
        return None

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
    very general assumptions, too slow in my opinion
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

    def set_parameters(self,values):
        """
        sets the weight factors 
        """
        self.weight_list=weight_list[:len(self.sum_list)-1]
        self.weight_list[len(weight_list):len(self.sum_list)-1]=0.0

    def get_parameters(self):
        """
        returns the weight factors
        """
        return self.weight_list

    def get_sample_values(self,x1,x2):
        """
        merge the sets of sample-values
        """
        x_list=[x1,x2]
        epsilon=abs(x1-x2)/200.0

        for i in range(0,len(self.sum_list)):
            # process each member of sum
            if self.weight_list[i]!=0:
                #get new sample values
                sample_list=self.sum_list[i].get_sample_values(x1,x2)
                # merge old and new list...
                sum=0.0
                count=0
                new_list=[]
                last=min(x_list[0],sample_list[0])
                first=last
                while x_list or sample_list:
                    if count>0 and last-first>epsilon:
                        # mean value
                        new_list.append(sum/count)
                        # keep only last value
                        first=last
                        sum=0.0
                        count=0
                    if not sample_list:
                        last=x_list.pop(0)
                        sum+=last
                        count+=1
                        continue
                    if not x_list:
                        last=sample_list.pop(0)
                        sum+=last
                        count+=1
                        continue
                    if  sample_list[0]>x_list[0]:
                        last=x_list.pop(0)
                        sum+=last
                        count+=1
                    else:
                        last=sample_list.pop(0)
                        sum+=last
                        count+=1
                new_list.append(last)
                x_list=new_list
                
        return new_list

class line_function(plot_object):
    """
    x->a*x+b
    """
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

    def get_parameters(self):
        """
        returns (a,b)
        """
        return (a,b)

    def set_parameters(self,values):
        """
        sets a and b from (a,b)
        """
        self.a=float(values[0])
        self.b=float(values[1])
        
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
        self.norm=1.0/math.sqrt(2.0*math.pi)

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

    def get_parameters(self):
        """
        returns (mu,sigma,a)
        """
        return (self.mu,self.sigma,self.a)

    def set_parameters(self,values):
        """
        sets parameters from (mu,sigma,a)
        """
        self.mu=float(values[0])
        self.sigma=float(values[1])
        self.a=float(values[2])
        
    def get_value(self,x):
        "gauss function"
        return self.a*gsl.rng.gaussian_pdf(x-self.mu,self.sigma)
##        n=(float(x)-self.mu)/self.sigma
##        return math.exp(n*n/-2.0)*self.a/self.sigma*self.norm

    def __repr__(self):
        return "gauss_function: x->%f/(%f*sqrt(2*pi))*exp(-(x-%f)**2/2*%f**2)"%(self.a,self.sigma,self.mu,self.sigma)

class gauss_tail_function(plot_object):
    """
    gauss tail function
    """
    
    def __init__(self,mu=0,sigma=1,tail=0,a=1,color=None):
        "init parameters"
        plot_object.__init__(self,color)
        self.mu=float(mu)
        self.sigma=float(sigma)
        self.tail=float(tail)
        self.a=float(a)
##        self.norm=1.0/math.sqrt(2.0*math.pi)

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

    def get_parameters(self):
        """
        returns (mu,sigma,tail,a)
        """
        return (self.mu,self.sigma,self.tail,self.a)

    def set_parameters(self,values):
        """
        sets parameters from (mu,sigma,tail,a)
        """
        self.mu=float(values[0])
        self.sigma=float(values[1])
        self.tail=float(values[2])
        self.a=float(values[3])

    def get_value(self,x):
        "gauss function"
        return self.a*gsl.rng.gaussian_tail_pdf(x-self.mu,self.tail-self.mu,self.sigma)

    def __repr__(self):
        return "gauss_function: x->%f/(%f*sqrt(2*pi))*exp(-(x-%f)**2/2*%f**2)"%(self.a,self.sigma,self.mu,self.sigma)

class plot_canvas(Tkinter.Canvas):
    """
    first dirty, but working sketch of a plot canvas
    should be used with the plot objects
    """

    def __init__(self,master,**cnf):
        cnf.update({'highlightthickness':0})
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
        """
        """
        return self.create_line(self.get_coords(plot_object),
                                smooth=0,
                                fill=plot_object.get_color())

    def configure_plot_item(self,item,plot_object):
        """
        """
        self.coords(item,tuple(self.get_coords(plot_object)))
        self.itemconfigure(item,fill=plot_object.get_color())

    def get_coords(self,plot_object):
        """
        """
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

class handle_base:
    """
    base class with common handle methods
    """

    def __init__(self,canvas,report_function,values):
        """
        creates a new handle
        """
        self.canvas=canvas
        self.values=values
        if report_function is not None:
            self.report_function=report_function
        else:
            self.report_function=None

        self.add_handle()

    def __del__(self):
        """
        removes and deletes the handle
        """
        pass

    def create_items(self):
        """
        creates the necessary items, must be configured by set_values
        """
        pass
        
    def add_handle(self):
        """
        adds the handle to a canvas
        """
        self.create_items()
        self.set_values(self.values)
        self.bind_handle()

    def bind_handle(self):
        """
        binds the events
        """
        pass

    def remove_handle(self,canvas):
        """
        remove the handle from the canvas, unbinds the events
        """
        pass

    def start_move_event(self,event):
        """
        event handler for the first click on this handle
        """
        self.current=self.canvas.find_withtag(Tkinter.CURRENT)[0]
        self.canvas.tag_bind(self.current,'<B1-Motion>',self.move_event)
        self.canvas.tag_bind(self.current,'<ButtonRelease-1>',self.end_move_event)
        self.report('move_start')

    def move_event(self,event):
        """
        event handler for moving this handle
        """
        new_values=self.values_from_mouse(event)
        if new_values is not None:
            self.set_values(new_values)
            self.report('move')
        return

    def end_move_event(self,event):
        """
        event handler for release event
        """
        self.canvas.tag_unbind(self.current,'<B1-Motion>')
        self.canvas.tag_unbind(self.current,'<B1-Release>')
        self.current=None
        self.report('move_end')
        return

    def values_from_mouse(self,event):
        """
        calcualte values from mouse position and care of constraints
        """
        values=None
        return values

    def get_values(self):
        """
        get values from actual handle position
        """
        return None

    def set_values(self,values):
        """
        set position of handle from values
        """
        pass

    def report(self,reason):
        """
        call report function
        """
        if self.report_function is not None:
            self.report_function(self,reason,self.get_values())

class gaussian_handle(handle_base):
    """
    handle for parameters of gaussian curve 
    """

    def __init__(self,canvas,report_function,values,**conf):
        """
        """
        # for argument dictionaries of other function calls
        conf.update(conf.get('arg_dict',{}))
        self.color=conf.get('color','')
        self.pos_x=conf.get('pos_x',0.0)
        self.pos_y=conf.get('pos_y',0.0)
        self.d_x=conf.get('d_x',1.0)
        self.d_y=conf.get('d_y',1.0)
        
        handle_base.__init__(self,canvas,
                             report_function,
                             values)

    def create_items(self):
        """
        four items are created:

        - handle rectangle for mu

        - handle line for mu+sigma

        - handle line for mu-sigma

        - line between two sigma handles
        """
        self.sigma_line=self.canvas.create_line((0,0,0,0),
                                                fill=self.color,
                                                tag='sigma_line')
        self.mu_handle=self.canvas.create_polygon((0,0,0,0,0,0),
                                                  fill=self.color,
                                                  outline=self.color,
                                                  tag='mu_handle')
        self.sigma1_handle=self.canvas.create_line((0,0,0,0),
                                                   fill=self.color,
                                                   tag='sigma1_handle')
        self.sigma2_handle=self.canvas.create_line((0,0,0,0),
                                                   fill=self.color,
                                                   tag='sigma2_handle')

    def set_values(self,values):
        """
        takes (mu,sigma) as value
        """
        dist=math.sqrt(self.d_x*self.d_x+self.d_y*self.d_y)
        step_x=self.d_x/dist
        step_y=self.d_y/dist
        p_step_x=step_y
        p_step_y=-step_x
        pos_mu=(self.pos_x+self.d_x*values[0],self.pos_y+self.d_y*values[0])
        pos_sigma1=(pos_mu[0]+self.d_x*values[1],
                    pos_mu[1]+self.d_y*values[1])
        pos_sigma2=(pos_mu[0]-self.d_x*values[1],
                    pos_mu[1]-self.d_y*values[1])

        self.canvas.coords(self.mu_handle,(pos_mu[0]+step_x+p_step_x*3,
                                           pos_mu[1]+step_y+p_step_y*3,
                                           pos_mu[0]-step_x+p_step_x*3,
                                           pos_mu[1]-step_y+p_step_y*3,
                                           pos_mu[0]-step_x-p_step_x*3,
                                           pos_mu[1]-step_y-p_step_y*3,
                                           pos_mu[0]+step_x-p_step_x*3,
                                           pos_mu[1]+step_y-p_step_y*3,))
        self.canvas.coords(self.sigma1_handle,(pos_sigma1[0]+p_step_x*3,
                                               pos_sigma1[1]+p_step_y*3,
                                               pos_sigma1[0]-p_step_x*3,
                                               pos_sigma1[1]-p_step_y*3,))
        self.canvas.coords(self.sigma2_handle,(pos_sigma2[0]+p_step_x*3,
                                               pos_sigma2[1]+p_step_y*3,
                                               pos_sigma2[0]-p_step_x*3,
                                               pos_sigma2[1]-p_step_y*3,))
        self.canvas.coords(self.sigma_line,(pos_sigma1[0],
                                            pos_sigma1[1],
                                            pos_sigma2[0],
                                            pos_sigma2[1],))
        self.values=values

    def get_values(self):
        """
        returns internal value cache
        """
        return self.values

    def bind_handle(self):
        """
        binds the three handles
        """
        self.canvas.tag_bind(self.sigma1_handle,'<Button-1>',self.start_move_event)
        self.canvas.tag_bind(self.sigma2_handle,'<Button-1>',self.start_move_event)
        self.canvas.tag_bind(self.mu_handle,'<Button-1>',self.start_move_event)

    def start_move_event(self,event):
        """
        finds out, which part of the handle is selected and prepares for move tracing
        """
        current=self.canvas.find_withtag(Tkinter.CURRENT)[0]
        if self.mu_handle==current or \
           self.sigma1_handle==current or \
           self.sigma2_handle==current:
            handle_base.start_move_event(self,event)
        else:
            print self.start_move_event.__name__,\
                  ": don't know what to do with this event"
        return

    def values_from_mouse(self,event):
        """
        project the value to the handle base line and calculate new value
        """
        c_x=self.canvas.canvasx(event.x)-self.pos_x
        c_y=self.canvas.canvasy(event.y)-self.pos_y
        v=(self.d_x*c_x+self.d_y*c_y)/\
           (self.d_x*self.d_x+self.d_y*self.d_y)
        values=None
        if self.mu_handle==self.current:
            values=(v,self.values[1])
        elif self.sigma1_handle==self.current or self.sigma2_handle==self.current:
            if v!=self.values[0]:
                values=(self.values[0],abs(v-self.values[0]))
        else:
            print self.move_event.__name__,\
                  ": don't know what to do with this event"
        return values

class gaussian_tail_handle(gaussian_handle):
    """
    handle for parameters of gaussian curve 
    """

    def __init__(self,canvas,report_function,values,**conf):
        """
        """
        self.tail=values[2]
        values=(values[0],values[1])
        gaussian_handle.__init__(self,canvas,report_function,values,arg_dict=conf)

    def create_items(self):
        """
        adds the tail-handle as a circle
        """
        gaussian_handle.create_items(self)
        self.tail_handle=self.canvas.create_oval((0,0,0,0),
                                                 fill=self.color,
                                                 outline=self.color)

    def set_values(self,values):
        """
        accepts tuples (mu,sigma,tail) and (mu,sigma)
        """
        if len(values)>2:
            self.tail=values[2]
        self.canvas.coords(self.tail_handle,
                           self.d_x*self.tail+self.pos_x+3,
                           self.d_y*self.tail+self.pos_y+3,
                           self.d_x*self.tail+self.pos_x-3,
                           self.d_y*self.tail+self.pos_y-3)
        gaussian_handle.set_values(self,(values[0],values[1]))

    def get_values(self):
        """
        return tupel (mu,sigma,tail)
        """
        values=gaussian_handle.get_values(self)
        return (values[0],values[1],self.tail)

    def bind_handle(self):
        """
        binds additional tail circle
        """
        self.canvas.tag_bind(self.tail_handle,'<Button-1>',self.start_move_event)
        gaussian_handle.bind_handle(self)
        return

    def start_move_event(self,event):
        """
        validates, if a handle is clicked
        """
        current=self.canvas.find_withtag(Tkinter.CURRENT)[0]
        if self.tail_handle==current:
            handle_base.start_move_event(self,event)
        else:
            gaussian_handle.start_move_event(self,event)
        return

    def values_from_mouse(self,event):
        """
        calculates new value for tail circle or forwards to base class
        """
        if self.tail_handle==self.current:
            c_x=self.canvas.canvasx(event.x)-self.pos_x
            c_y=self.canvas.canvasy(event.y)-self.pos_y
            v=(self.d_x*c_x+self.d_y*c_y)/\
               (self.d_x*self.d_x+self.d_y*self.d_y)
            return (self.values[0],self.values[1],v)
        else:
            values=gaussian_handle.values_from_mouse(self,event)
            if values is not None:
                return (values[0],values[1],self.tail)
            else:
                return None
            
class gauss_editor(Tkinter.Frame):
    """
    first demonstration of continous prob editor
    """
    
    def __init__(self,master,**cnf):
        """
        glues a plot area, a handle area and a pie together
        """
        Tkinter.Frame.__init__(self,master,cnf)
        self.plot_area=plot_canvas(self,bg='white')
        self.edit_area=Tkinter.Canvas(self,bg='white',highlightthickness=0)
        self.edit_area.bind('<Configure>',self.configure_handles)

        self.plot_list=[]
        self.handle_list=[]
        
        #some nonsence data
        self.plot_area.scale_y=100.0
        self.plot_area.scale_x=50.0        

        d={}
        color_list=['red','green','blue','yellow']

        for i in range(1,5):
            o=gauss_tail_function(mu=i*2.0,
                                  sigma=1.0,
                                  tail=0.0,
                                  a=i/2.0,
                                  color=color_list[i-1])
            self.plot_list.append(o)
            self.plot_area.add_plot_object(o)
            d[str(i)]=i/2.0
        self.dict=ProbEditorBasics.ProbDict(d)

        self.plot_sum=sum_function(sum_list=self.plot_list,color='red')
        self.plot_area.add_plot_object(self.plot_sum)
        self.create_handles()

        keys=self.dict.keys()
        keys.sort()
        self.pie=ProbEditorWidgets.e_pie_chart(self,
                                               self.dict,
                                               keys,
                                               color_list,
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
        recieve modifications of pie
        """
        if what=='new value' or what=='move value':
            for k in dict.keys():
                i=int(k)-1
                self.plot_list[i].a=dict[k]
                self.plot_area.replot_object(self.plot_list[i])
            self.plot_area.replot_object(self.plot_sum)

    def handle_report(self,who,what,values):
        """
        sets new values to the plot object
        """
        plot_object=self.plot_list[self.handle_list.index(who)]
        l=list(values)
        l.append(plot_object.a)
        plot_object.set_parameters(l)
        self.plot_area.replot_object(plot_object)
        self.plot_area.replot_object(self.plot_sum)

    def create_handles(self):
        """
        creates handles for objects in list
        """
        pos=0
        self.edit_area.configure(height=10*len(self.plot_list))
        for o in self.plot_list:
            if o.__class__.__name__=='gauss_function':
                handle=gaussian_handle(self.edit_area,
                                       self.handle_report,
                                       (o.mu,o.sigma),
                                       color=o.get_color(),
                                       pos_y=pos+10)
                self.handle_list.append(handle)
            elif o.__class__.__name__=='gauss_tail_function':
                handle=gaussian_tail_handle(self.edit_area,
                                            self.handle_report,
                                            (o.mu,o.sigma,o.tail),
                                            color=o.get_color(),
                                            pos_y=pos+10)
                self.handle_list.append(handle)
            else:
                print "no handle for %s"%(o.__class__.__name__)
            pos+=10

    def configure_handles(self,event):
        """
        configure handles for gauss functions
        """
        if self.plot_area.configured==0:
            return
        i=0
        self.edit_area.configure(height=10*len(self.handle_list))
        for h in self.handle_list:
            values=h.get_values()
            h.pos_x=self.plot_area.xy_to_canvasxy((0,0))[0]
            h.pos_y=i*10+5
            # not fine
            h.d_x=(self.plot_area.xy_to_canvasxy((100,0))[0]-
                   self.plot_area.xy_to_canvasxy((0,0))[0])/100.0
            h.d_y=0.0
            h.set_values(values)
            i+=1

if __name__=='__main__':
    root=Tkinter.Tk()
    editor=gauss_editor(root,width=300,height=300)
    # fast quit by <Escape>
    root.bind('<Escape>',lambda e:e.widget.quit())
    editor.pack(expand=1,fill=Tkinter.BOTH)
    root.mainloop()
