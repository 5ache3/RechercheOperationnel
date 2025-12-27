import math
import numpy as np
from convexhull import convex_hull
EPS = 1e-9
ROUND = 9

def norm(p):
    return (round(p[0], ROUND), round(p[1], ROUND))

def intersect(l1, l2):
    a1,b1,c1 = l1
    a2,b2,c2 = l2
    det = a1*b2 - a2*b1
    if abs(det) < EPS:
        return None
    x = (b1*c2 - b2*c1) / det
    y = (c1*a2 - c2*a1) / det
    return norm((x,y))

def unique_points(pts):
    uniq = []
    for p in pts:
        if not any(math.hypot(p[0]-q[0], p[1]-q[1]) < 10**(-ROUND) for q in uniq):
            uniq.append(p)
    return uniq

def sort_points_along_line(line, pts):
    a,b,c = line
    dx, dy = b, -a   # direction vector of line
    if abs(dx) < EPS and abs(dy) < EPS:
        return sorted(pts)
    return sorted(pts, key=lambda p: p[0]*dx + p[1]*dy)

def build_segments(lines):
    segs = []
    all_pts = set()
    for i, L in enumerate(lines):
        pts = []
        for j, M in enumerate(lines):
            if i == j: continue
            p = intersect(L, M)
            if p is not None and p[0]>=0 and p[1]>=0:
                pts.append(p)
                all_pts.add(p)
        pts = unique_points(pts)
        pts = sort_points_along_line(L, pts)
        segs.append(pts)
    return segs, all_pts

def build_graph(segs):
    g = {}
    def add(a,b):
        g.setdefault(a, set()).add(b)
        g.setdefault(b, set()).add(a)
    for pts in segs:
        for i in range(len(pts)-1):
            a = pts[i]; b = pts[i+1]
            if a == b: continue
            add(a,b)
    # convert sets -> lists
    for k in list(g.keys()):
        g[k] = list(g[k])
    return g

def build_ccw_neighbors(graph):
    ccw = {}
    for v, neigh in graph.items():
        vx, vy = v
        neigh_sorted = sorted(neigh, key=lambda u: math.atan2(u[1]-vy, u[0]-vx))
        ccw[v] = neigh_sorted
    return ccw

def walk_face_from_directed_edge(ccw_neigh, start_u, start_v, maxsteps=10000):
    start = (start_u, start_v)
    u, v = start_u, start_v
    face = []
    steps = 0
    while True:
        face.append(u)
        steps += 1
        if steps > maxsteps:
            raise RuntimeError("stuck in face walk loop")
        neigh = ccw_neigh[v]
        # find index of u in ccw list of v
        try:
            idx = neigh.index(u)
        except ValueError:
            # numerical mismatch — abort
            return None
        # to keep face on left of directed edges, choose neighbor BEFORE u in CCW order
        next_idx = (idx - 1) % len(neigh)
        w = neigh[next_idx]
        u, v = v, w
        if (u, v) == start:
            break
    return face

def polygon_area(poly):
    a = 0.0
    n = len(poly)
    for i in range(n):
        x1,y1 = poly[i]
        x2,y2 = poly[(i+1)%n]
        a += x1*y2 - x2*y1
    return 0.5 * a

def pick_bottom_face(faces):
    cand = []
    for f in faces:
        if (0.0, 0.0) in f:
            area = abs(polygon_area(f))
            if area > EPS:
                cand.append((area, f))
    if not cand:
        return None
    cand.sort(key=lambda x: x[0])
    return cand[0][1]

def enumerate_all_faces(graph):
    ccw_neigh = build_ccw_neighbors(graph)
    visited = { (u,v): False for u in graph for v in graph[u] }
    faces = []
    for (u0, v0), seen in list(visited.items()):
        if seen: continue
        u, v = u0, v0
        face = []
        while True:
            visited[(u,v)] = True
            face.append(u)
            neigh = ccw_neigh[v]
            try:
                idx = neigh.index(u)
            except ValueError:
                break
            w = neigh[(idx - 1) % len(neigh)]
            u, v = v, w
            if (u, v) == (u0, v0):
                break
        if len(face) >= 3 and abs(polygon_area(face)) > EPS:
            faces.append(face)
    return faces, ccw_neigh

def top_face_by_sliding(graph, all_points):
    # choose highest vertex
    highest = max(all_points, key=lambda p: p[1])
    # neighbors sorted by descent (most negative dy first)
    neighs = sorted(graph.get(highest, []), key=lambda n: (n[1]-highest[1], abs(n[0]-highest[0])))
    if not neighs:
        return None
    faces, ccw = enumerate_all_faces(graph)
    # try each neighbor as initial directed edge (highest -> neigh) in order of steepest descent
    for n in neighs:
        face = walk_face_from_directed_edge(ccw, highest, n)
        if face and highest in face and abs(polygon_area(face)) > EPS:
            lis=[]

            for node in face :
                if node[0]>=0 and node[1]>=0:
                    lis.append(node)
            
            return lis
    # fallback: if none found, pick smallest face containing highest
    cand = []
    for f in faces:
        if highest in f:
            print(f)
            cand.append((abs(polygon_area(f)), f))
    if not cand:
        return None
    cand.sort(key=lambda x: x[0])


    return cand[0][1]

def get_uper_polygon(face,x_max,y_max):

    lis=[(x_max,y_max),(0,y_max)]
    for p in face[::-1] :
        if p[0]==0 and p[1]==0:
            continue
        lis.append(p)
    lis.append((x_max,0))
    return lis


def polygons_from_lines(lines,x_max,y_max,minim=True):
    # lines: list of (a,b,c)
    lines.append([1,0,x_max])
    lines.append([0,1,y_max])

    lines=[(line[0],line[1],-line[2]) for line in lines]

    full = list(lines) + [(1,0,0), (0,1,0),]
    segs, all_pts = build_segments(full)
    graph = build_graph(segs)
    faces, _ = enumerate_all_faces(graph)
    bottom = convex_hull(pick_bottom_face(faces))
    
    full_poly = top_face_by_sliding(graph, all_pts)
    top=get_uper_polygon(bottom,x_max,y_max)
    if not minim:
        return [bottom,top]
    return [convex_hull(full_poly),bottom]

if __name__ == "__main__":

    lines = lines=[
            [10,5,35],
            [5,15,30],
            # [9,0,25],
            [0,6,25],
        ]
    bottom, top= polygons_from_lines(lines,x_max=20,y_max=10,minim=False)
    print(bottom)
    print(top)