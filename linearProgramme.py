import os,sys
sys.path.append(os.curdir)
import random as rd
from manimlib import *
from polygon import polygons_from_lines
from convexhull import convex_hull

def to_int(r):
    e=int(r)
    if e-r ==0 :
        return e
    else:
        return r
    
def get_intersections(line1,line2):
    [a1,b1,c1]=line1
    c1=-c1
    [a2,b2,c2]=line2
    c2=-c2
    try:
        x=(b1*c2-b2*c1)/(a1*b2-a2*b1)
        y=(c1*a2-c2*a1)/(a1*b2-a2*b1)

        return (to_int(x),to_int(y))
    except :
        return None
    
def above(line, pt):
    x, y = pt
    a, b, c = line
    
    if a == 0 and b == 0:
        return 0 >= c

    if b == 0:
        if a > 0:
            return a * x >= c
        else:
            return a * x >= c

    if a == 0:
        if b > 0:
            return b * y >= c
        else:
            return b * y >= c
        
    return a * x + b * y >= c
            


def manage_intersections(lines):
    lines=[[1,0,0],*lines,[0,1,0]]
    intersections=[]
    checked=[]
    for i in range(len(lines)):
        line=lines[i]
        for j in range(len(lines)):
            line2=lines[j]
            if line==line2 or str(line2) in checked:
                continue
            inter=get_intersections(line,line2)
            if not inter or inter[0]<0 or inter[1] <0:
                continue
            intersections.append(inter)
        checked.append(str(line))
    return intersections


def get_line_polygon(line,x_min=0,y_min=0,x_max=None,y_max=None,minimizing=True):
    additionals=[]
    axes=[[1,0,x_min],[0,1,y_min]]
    if minimizing:
        if x_max and y_max:
            lines=[[1,0,x_min],line,[0,1,y_min]]
            additionals=[[0,1,y_max],[1,0,x_max]]
        else:
            lines=[[1,0,x_min],*lines,[0,1,y_min]]
        intersections=[]
        checked=[]
        for i in range(len(lines)):
            line=lines[i]
            for j in range(len(lines)):
                line2=lines[j]

                if line==line2 or str(line2) in checked:
                    continue
                inter=get_intersections(line,line2)
                if not inter or inter[0]<0 or inter[1] <0:
                    continue
                l=len(lines)
                if i < l and j < l:
                    intersections.append(inter)
                    
            if i > 0 and (line[0]==0 or line[1]==0) and additionals and line not in axes:
                e=-1 if line[0]==0 else 0
                inter=get_intersections(line,additionals[e])
                if inter:
                    intersections.append(inter)
                    inter2=get_intersections(additionals[e],lines[e])
                    if inter2:
                        intersections.append(inter2)
        

            checked.append(str(line))
        return convex_hull(intersections)
    
    additionals=[[0,1,y_max],[1,0,x_max]]
    lines=[axes[0],line,axes[1],*additionals]
    intersections=[]
    checked=[]
    
    for i in range(len(lines)):
        line=lines[i]
        for j in range(len(lines)):
            line2=lines[j]

            if line==line2 or str(line2) in checked:
                continue
            inter=get_intersections(line,line2)
            if not inter or inter[0]<0 or inter[1] <0:
                continue
            l=len(lines)
            if i < l and j < l:
                intersections.append(inter)
                
        if i > 0 and (line[0]==0 or line[1]==0) and additionals and line not in axes:
            e=-1 if line[0]==0 else 0
            inter=get_intersections(line,additionals[e])
            if inter:
                intersections.append(inter)
                inter2=get_intersections(additionals[e],lines[e])
                if inter2:
                    intersections.append(inter2)
    

        checked.append(str(line))
    
    intersections=[inter if inter!=(0,0) and above(lines[1],inter) else None for inter in intersections]
    intersections=convex_hull(list(filter(lambda x:x,intersections)))
    if intersections:
        return convex_hull(intersections)
    else:
        return [(0,0),(3,3)]



def manage_axes(lines,x_range=[0,20,1],y_range=[0,10,1]):
    intersections=manage_intersections(lines)
    max_x=0
    max_y=0
    for point in intersections:
        if point[0]>max_x:
            max_x=point[0]

        if point[1]>max_y:
            max_y=point[1]

    if max_y > 10:
        y_range=[0,math.ceil(max_y)+1,math.ceil(max_y/10)]
    if max_x > 10:
        x_range=[0,math.ceil(max_x)+2,math.ceil(max_x/20)]
    
    return {"x_range":x_range,"y_range":y_range}



def createGraph(axes:Axes,xyz,color=BLUE,epsi=0.05):
    a=xyz[0]
    b=xyz[1]
    c=xyz[2]
    
    if b==0:
        x_val=c/a
        t_range=axes.y_range
        return axes.get_parametric_curve(lambda t : np.array([x_val,t,0]),t_range=t_range,color=color)
    
    if a==0:
        y_val=c/b
        line=axes.get_graph(lambda t:y_val,color=color)
        return line
    
    line=axes.get_graph(lambda x:(-a*x+c)/b,x_range=[-epsi,min(c/a+epsi,axes.x_range[1])],color=color,)
    return line
    # return line

def get_inequality_poly(axes:Axes,line,less=True,color=RED,opacity=.3):
    y_min=axes.y_range[0]
    y_max=axes.y_range[1]
    x_min=axes.x_range[0]
    x_max=axes.x_range[1]
    inter=get_line_polygon(line,x_min=x_min,y_min=y_min,x_max=x_max,y_max=y_max,minimizing=less)
    
    return Polygon(*[axes.c2p(*p) for p in inter],color=color,fill_opacity=opacity,stroke_width=0)


def above_all_lines(point,lines,minim=False):
    valid=True
    x=point[0]
    y=point[1]
    epsi=10e-9
    if minim:
        for line in lines:
            [a,b,c]=line
            c=-c
            if (a*x + b*y +c)<0:
                valid=False
    else:
        for line in lines:
            [a,b,c]=line
            c=-c
            if (a*x + b*y +c)>epsi:
                valid=False
    return valid


def find_lines_by_intersection(lines,p):
    lis=[]
    lines.append([0,1,0])
    lines.append([1,0,0])
    for line in lines:
        if p[0]*line[0]+p[1]*line[1]==line[2] and line not in lis:
            lis.append(line)
    return lis

def calculate_ranges(lines,func):
    
    l1=[]
    X,Y=func
    for line in lines:
        if line[1]==0:
            l1.append(0)
        elif line[0]==0:
            l1.append(X*2)
        else:
            l1.append(line[0]*Y/line[1])
            
    
    l2=[]
    for line in lines:
        if line[1]==0:
            l2.append(Y*2)
        elif line[0]==0:
            l2.append(0)
        else:
            l2.append(line[1]*X/line[0])
        
    l1.sort()
    l2.sort()
    return [l1,l2]

def same_point(p1,p2):
    return p1[0]==p2[0] & p1[1]==p2[1]

def fade_group(self,op):
    self.play(self.axes.animate.set_opacity(op),
        self.graphs_red.animate.set_opacity(op*op),
        self.polys[0].animate.set_opacity(op*op),
        self.solutions.animate.set_opacity(op*op),
        # self.labels[0].animate.set_opacity(op),
        self.labels[2].animate.set_opacity(op),
        self.brace.animate.set_opacity(op),
        self.sol_box.animate.set_opacity(0),
        VGroup(*[self.dots[i] if i!=self.opt_point else Dot(radius=0) for i in range(len(self.dots))]).animate.set_opacity(op),
        VGroup(*[ 
            self.labels[1][i] if self.lines[i] not in self.concerned_lines else Dot(radius=0)
            for i in range(len(self.labels[1]))
            ]).animate.set_opacity(op),
        VGroup(*[ 
            self.graphs[i] if self.lines[i] not in self.concerned_lines else Dot(radius=0)
            for i in range(len(self.labels[1]))
            ]).animate.set_opacity(op),
        )
    
class PL(Scene):
    def initializer(self):
        func=self.func
        lines=self.lines
        minimizing=self.minimizing
        colors=self.colors
        axes =Axes(
            **manage_axes([[*d] for d in lines]),
            height=6,
            width=8,
            axis_config={
            "include_tip":True,
            }
        )
        axes.add_coordinate_labels()

        axes.to_edge(LEFT)
        self.axes=axes

        self.graphs=[createGraph(axes,lines[i],color=colors[i%len(colors)]) for i in range(len(lines))]
        self.graphs_red=VGroup(*[get_inequality_poly(axes,line,minimizing,color=RED) for line in lines])
        
        self.labels=VGroup(Tex(f"{'Min' if minimizing else 'Max'} F(X,Y) = {func[0]}X + {func[1]}Y "),
                    VGroup(*[Tex(f"{lines[i][0]}X + {lines[i][1]}Y={lines[i][2]}",fill_color=colors[i])  for i in range(len(lines))]).arrange(DOWN),
                    Tex("X\geq 0,Y \geq 0")
        ).arrange(DOWN).scale(.6).to_corner(UR)

        self.brace=Brace(VGroup(self.labels[1:]),direction=LEFT,fill_opacity=.7)

        self.polys=VGroup(*[
                Polygon(*[axes.c2p(r[0],r[1]) for r in polygon],color=[GREEN,RED][i],fill_opacity=.7,stroke_width=0)
                for i,polygon in enumerate(polygons_from_lines([
                    [i for i in d] for d in lines
                    ]
                    ,x_max=axes.x_range[1],
                    y_max=axes.y_range[1],
                    minim=minimizing
                    ))
            ])
        
        self.intersections=list(
            filter(lambda p: above_all_lines(p,lines,minimizing),manage_intersections(lines))
            )
        
        results=[p[0]*func[0]+p[1]*func[1] for p in self.intersections]
        
        opt_val= min(results) if minimizing else max(results)
        
        self.opt_point=results.index(opt_val)

        self.dots=VGroup(*[
            Dot(
                axes.c2p(*p),
                radius=.05,
                fill_color=YELLOW if p!=self.intersections[self.opt_point] else BLUE 
                ) for p in self.intersections]
        )
        self.solutions=VGroup(*[
            Tex(f"F({round(p[0],1)},{round(p[1],1)}) = {round(p[0]*func[0]+p[1]*func[1],2)}")
            for p in self.intersections]
        ).arrange(DOWN).next_to(self.labels,DOWN*2).scale(.6)

        self.sol_box=SurroundingRectangle(self.solutions[self.opt_point])


    def animate_simple_PL(self):
        self.add(self.axes)
        self.add(self.labels[0],self.brace,self.labels[2])

        for i in range(len(self.graphs)):
            self.play(FadeIn(self.graphs_red[i]),ShowCreation(self.graphs[i]),Write(self.labels[1][i]))
        
        self.add(self.polys[0])

        self.add(self.dots,self.solutions,self.sol_box)


    def analyse(self):
        func=self.func
        axes=self.axes
        intersections=self.intersections
        c_lines=find_lines_by_intersection(self.lines,intersections[self.opt_point])
        try:
            if c_lines[0][0]/c_lines[0][1] <=c_lines[1][0]/c_lines[1][1]:
                self.concerned_lines=c_lines
            else:
                self.concerned_lines=c_lines[::-1]
        except:
            self.concerned_lines=c_lines

        [start_1,end_1],[start_2,end_2]=calculate_ranges(self.concerned_lines,func)
        

        # TODO : animate the process of finding the ranges of optimality

        X=ValueTracker(func[0])
        Y=ValueTracker(func[1])
        self.X=X
        self.Y=Y
        obj_func=always_redraw(lambda:
            Text(f"{'Min' if self.minimizing else 'Max'} F(X,Y) = {round(X.get_value(),1)}X + {round(Y.get_value(),1)}Y ").scale(.6).move_to(self.labels[0])
        )

        self.remove(self.labels[0])
        self.add(obj_func)

        
        apdatable_solutions= always_redraw(lambda:
            VGroup(*[
                Text(f"F({round(p[0],1)},{round(p[1],1)}) = {round(p[0]*X.get_value()+p[1]*Y.get_value(),2)}")
                for p in intersections]
            ).arrange(DOWN).move_to(self.solutions).scale(.6)                         
        )
        def get_results():
            return [p[0]*X.get_value() + p[1]*Y.get_value() for p in intersections]
        def opt_index():
            values = get_results()
            return values.index(min(values)) if self.minimizing else values.index(max(values))
        box = always_redraw(lambda:
            SurroundingRectangle(apdatable_solutions[opt_index()])
        )
        self.remove(self.sol_box)
        self.add(box)

        range1=NumberLine(x_range=[start_1,end_1,int((end_1-start_1)/5)],width=4.5,include_ticks=True,include_numbers=False).next_to(apdatable_solutions,DOWN*3)
        self.range_x=range1
        t1= always_redraw(lambda:
            VGroup(Text(f"{round(X.get_value())}"),Triangle(fill_opacity=1,color=RED).scale(0.2).rotate(PI)).arrange(DOWN).scale(.35)
            .move_to(range1.n2p(X.get_value()) + UP*0.25) 
        )

        r1_start=Tex(f'{round(start_1)}').next_to(range1.n2p(start_1),DOWN*.5).scale(.35)
        r1_end=Tex(f'{round(end_1)}').next_to(range1.n2p(end_1),DOWN*.5).scale(.35)
        
        range2=NumberLine(x_range=[start_2,end_2,int((end_2-start_2)/5)],width=4.5,include_ticks=True,include_numbers=False).next_to(range1,DOWN*3)
        self.range_y=range2
        t2= always_redraw(lambda:
            VGroup(Text(f"{round(Y.get_value())}"),Triangle(fill_opacity=1,color=RED).scale(0.2).rotate(PI)).arrange(DOWN).scale(.35)
            .move_to(range2.n2p(Y.get_value()) + UP*0.25) 
        )
        r2_start=Tex(f'{round(start_2)}').next_to(range2.n2p(start_2),DOWN*.5).scale(.35)
        r2_end=Tex(f'{round(end_2)}').next_to(range2.n2p(end_2),DOWN*.5).scale(.35)


        self.remove(self.solutions)
        self.add(apdatable_solutions,range1,range2,r1_start,r1_end,r2_start,r2_end,t1,t2)
        
        line= always_redraw(lambda:
            createGraph(axes,[X.get_value(),Y.get_value(),0],epsi=axes.x_range[1])
            .move_to(axes.c2p(*intersections[self.opt_point])))
        
        self.add(line)
        test=False
        # self.embed()
        if test:
            self.play(X.animate.set_value(start_1),run_time=5)
            self.wait()
            self.play(X.animate.set_value(start_1-5),run_time=2)
            self.wait()
            X.set_value(func[0])
            self.play(X.animate.set_value(end_1),run_time=5)
            self.wait()
            self.play(X.animate.set_value(end_1+10),run_time=2)
            self.wait()
            X.set_value(func[0])

            self.play(Y.animate.set_value(start_2),run_time=5)
            self.wait()
            self.play(Y.animate.set_value(start_2-10),run_time=2)
            self.wait()
            Y.set_value(func[1])
            self.play(Y.animate.set_value(end_2),run_time=5)
            self.wait()
            self.play(Y.animate.set_value(end_2+10),run_time=2)
            self.wait()
            Y.set_value(func[1])
            self.wait(3)
    
    def on_key_press(self,symbol,modifiers):
        from pyglet.window import key 

        if symbol == key.X:
            pos=self.range_x.p2n(self.mouse_point.get_center())
            self.X.set_value(pos)
        if symbol == key.Y:
            pos=self.range_y.p2n(self.mouse_point.get_center())
            self.Y.set_value(pos)
        if symbol == key.R:
            self.X.set_value(self.func[0])
            self.Y.set_value(self.func[1])
        
        super().on_key_press(symbol,modifiers)
        
    def construct(self):
        func=[1200,500]
        lines=[
            [10,5,200],
            [2,3,60],
            [1,1,34],
        ]
        minimizing=False
        
        colors=[BLUE_C,GREEN,RED,BLUE_C,GREEN,RED,YELLOW]

        self.func=func
        self.lines=lines
        self.colors=colors
        self.minimizing=minimizing

        

        self.initializer()
        self.animate_simple_PL()
        self.analyse()