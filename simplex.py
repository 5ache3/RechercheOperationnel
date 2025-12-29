from manimlib import *
from fractions import Fraction
import os,sys
sys.path.append(os.curdir)
from table import Table

class SimplexSolver:

    def __init__(self,programme):
        self.programme=programme
        t0=self.firstTable()
        self.tables=[]
        self.next_simplex(t0)
    
    def get_pivot(self,lis):
        col_pivot=0
        m=0
        for i in range(1,len(lis[-1])):
            item=lis[-1][i]
            if item>m:
                m=item
                col_pivot=i
        row_pivot=-15
        m=-1
        for i in range(1,len(lis)-1):
            if lis[i][col_pivot]==0:
                continue
            item=lis[i][-1]/lis[i][col_pivot]
            if m==-1 and item >=0:
                m=item
                row_pivot=i
            if item >= 0 and item <m:
                m=item
                row_pivot=i
        return [row_pivot,col_pivot]

    def firstTable(self):
        def line_helper(line,ind,n):
            lis=[]

            for item in line[0]:
                lis.append(item)

            for i in range(n):
                if i == ind:
                    lis.append(1)
                else :
                    lis.append(0)
            return lis
            
        def header_helper(nb_vars,nb_eps):
            lis=['']
            for i in range(nb_vars):
                lis.append(f'X_{{{i+1}}}')

            for i in range(nb_eps):
                lis.append(f'e_{{{i+1}}}')
            lis.append('')
            return lis

        def footer_helper(vars,nb_eps):
            lis=['Z']
            for item in vars:
                lis.append(item)

            for i in range(nb_eps):
                lis.append(0)
            lis.append(0)
            return lis
        
        f = self.programme['function']
        sc = self.programme['contraintes']
        t=[]
        t.append(header_helper(len(f),len(sc)))
        i=0
        for line in sc:
            t.append([
                fr'e_{{{i+1}}}',*line_helper(line,i,len(sc)),line[1]
            ])
            i+=1
        t.append(footer_helper(f,len(sc)))

        return t
    
    def next_simplex(self,lis,pivot=None):
        if not pivot:
            pivot=self.get_pivot(lis)
            self.tables.append({
                'piv':pivot,
                'table':lis
            })
            return self.next_simplex(lis,pivot)
        lis2=[]
        for i in range(len(lis)):
            lis2.append([])
            for j in range(len(lis[i])):
                lis2[i].append(lis[i][j])

        r_p,c_p=pivot
        lis2[r_p][0]=lis2[0][c_p]
        for i in range(1,len(lis)):
            lis2[i][c_p]=0

        for i in range(1,len(lis[r_p])):
            lis2[r_p][i]=Fraction(lis[r_p][i],lis[r_p][c_p])
        
        for i in range(1,len(lis)):
            if i== r_p:
                continue
            for j in range(1,len(lis[i])):
                if j== c_p:
                    continue
                lis2[i][j] = lis[i][j] - Fraction(lis[r_p][j]*lis[i][c_p],lis[r_p][c_p])
        
        final=True
        for i in range(1,len(lis2[-1])):
            if float(lis2[-1][i]) > 0:
                final=False

        if not final:
            pivot=self.get_pivot(lis2)
            self.tables.append({
                'piv':pivot,
                'table':lis2
            })

            return self.next_simplex(lis2,pivot)
        self.tables.append({
            'piv':None,
            'table':lis2
        })
        return lis2



class Simplex(Scene):

    def construct(self):
        f=[1200,1000]

        sc=[
            [[10,5],200],
            [[2,3],60],
            [[1,1],34],
        ]
        programme={"function":f,"contraintes":sc}
        p=SimplexSolver(programme)

        tables=p.tables
        table=tables[1]['table']
        main_t=[t[1:] for t in table[1:]]
        # t0=Table(
        #     table=main_t,
        #     col_labels=[Tex(t) for t in table[0][1:]],
        #     row_labels=[Tex(t[0]) for t in table[1:]]
        #     )
        t0=Table(table).scale(.5)
        

        c=t0.get_cell_b((2,3))
        c2=t0.get_cell_b((2,5))
        rec=SurroundingRectangle(VGroup(c,c2),buff=0,fill_color=RED,fill_opacity=.4,stroke_width=0)
        self.play(t0.create_lables())
        self.play(ShowCreation(rec))


