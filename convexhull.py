import math

def orientation(p, q, r):
    val = (q[1] - p[1]) * (r[0] - q[0]) - \
          (q[0] - p[0]) * (r[1] - q[1])

    if val == 0:
        return 0
    elif val > 0:
        return 1
    else:
        return 2

def dist_sq(p1, p2):
    return (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2

def convex_hull(points,p0=None):
    n = len(points)
    if n < 3:
        return sorted(points)

    if not p0:
        p0 = min(points, key=lambda p: (p[1], p[0]))
    
    remaining_points = [p for p in points if p != p0]

    def sort_key(p):
        angle = math.atan2(p[1] - p0[1], p[0] - p0[0])
        distance = dist_sq(p0, p)
        return (angle, distance)

    remaining_points.sort(key=sort_key)
    
    unique_sorted_points = [p0]
    for p in remaining_points:
        if len(unique_sorted_points) > 1:
            p_prev = unique_sorted_points[-1]
            p_prev_prev = unique_sorted_points[-2]
            
            if orientation(p_prev_prev, p_prev, p) == 0:
                if dist_sq(p0, p) > dist_sq(p0, p_prev):
                    unique_sorted_points[-1] = p
                continue
                
        unique_sorted_points.append(p)

    hull = []
    
    if len(unique_sorted_points) < 3:
         return sorted(unique_sorted_points)
         
    hull.append(unique_sorted_points[0])
    hull.append(unique_sorted_points[1])

    for i in range(2, len(unique_sorted_points)):
        while len(hull) > 1 and orientation(hull[-2], hull[-1], unique_sorted_points[i]) != 2:
            hull.pop()
        hull.append(unique_sorted_points[i])
    
    return hull