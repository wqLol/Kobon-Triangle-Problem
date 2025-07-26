import tkinter as tk
from geometryfuncs import getEquation, Vec2
from decimal import Decimal
import random
from collections import defaultdict

root = tk.Tk()
root.title("Python Line Visualization")
root.geometry("800x600")

canvas_width = 780
canvas_height = 580

canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="white", bd=2, relief="sunken")
canvas.pack(pady=10)

points = [
    Vec2(Decimal(50), Decimal(50)),
    Vec2(Decimal(200), Decimal(100)),
    Vec2(Decimal(100), Decimal(300)),
    Vec2(Decimal(350), Decimal(250)),
    Vec2(Decimal(500), Decimal(50)),
    Vec2(Decimal(700), Decimal(350)),
    Vec2(Decimal(150), Decimal(450)),
    Vec2(Decimal(600), Decimal(150))
]

lines_to_draw = [
    (points[0], points[1]),
    (points[1], points[2]),
    (points[2], points[3]),
    (points[3], points[4]),
    (points[4], points[5]),
    (points[5], points[0]),
    (points[6], points[7]),
    (points[0], points[3])
]

offset_x = 0
offset_y = 0
scale = 1.0
point_radius = 6

def world_to_screen(p: Vec2):
    x = float(p.x) * scale + offset_x
    y = float(p.y) * scale + offset_y
    return x, y

def line_intersection(line1, line2):
    A1, B1, C1 = line1
    A2, B2, C2 = line2
    det = A1*B2 - A2*B1
    if det == 0:
        return None
    x = (B1*C2 - B2*C1) / det
    y = (A2*C1 - A1*C2) / det
    return Vec2(x, y)

def get_line_param(line_p1, line_p2, pt):
    """Get parameter t for point pt on line segment line_p1->line_p2:
       pt = line_p1 + t*(line_p2 - line_p1)
    """
    dx = line_p2.x - line_p1.x
    dy = line_p2.y - line_p1.y
    if abs(dx) >= abs(dy):
        if dx == 0:
            return Decimal(0)
        return (pt.x - line_p1.x) / dx
    else:
        if dy == 0:
            return Decimal(0)
        return (pt.y - line_p1.y) / dy

def approx_equal(p1: Vec2, p2: Vec2, tol=Decimal('1e-12')):
    return abs(p1.x - p2.x) <= tol and abs(p1.y - p2.y) <= tol

def point_hash(p: Vec2):
    # Round to 12 decimals for hashing to avoid floating precision issues
    return (round(float(p.x), 12), round(float(p.y), 12))

# Build data structures:

line_eqs = [getEquation(p1, p2) for p1, p2 in lines_to_draw]
n = len(line_eqs)

# 1) Find all intersection points between lines
intersection_points = dict()  # hash -> Vec2 point
point_id_map = dict()  # hash -> unique id integer
next_point_id = 0

line_points_map = defaultdict(list)  # line index -> list of intersection points on that line

for i in range(n):
    for j in range(i+1, n):
        pt = line_intersection(line_eqs[i], line_eqs[j])
        if pt is not None:
            # Avoid duplicates due to floating precision, hash by rounded coords
            h = point_hash(pt)
            if h not in intersection_points:
                intersection_points[h] = pt
                point_id_map[h] = next_point_id
                next_point_id += 1

            line_points_map[i].append(intersection_points[h])
            line_points_map[j].append(intersection_points[h])

for i, (p1, p2) in enumerate(lines_to_draw):
    pts = line_points_map[i]

    pts_with_t = []
    for pt in pts:
        t = get_line_param(p1, p2, pt)
        pts_with_t.append((t, pt))
    pts_with_t.sort(key=lambda x: x[0])
    line_points_map[i] = [pt for t, pt in pts_with_t]

adjacency = defaultdict(set)  # point_id -> set(point_id)

for i in range(n):
    pts = line_points_map[i]
    for idx in range(len(pts)-1):
        h1 = point_hash(pts[idx])
        h2 = point_hash(pts[idx+1])
        id1 = point_id_map[h1]
        id2 = point_id_map[h2]
        adjacency[id1].add(id2)
        adjacency[id2].add(id1)



def count_and_get_triangles(adjacency):
    triangles = []

    for u in adjacency:
        neighbors_u = adjacency[u]
        for v in neighbors_u:
            if v <= u:
                continue
            neighbors_v = adjacency[v]
            common = neighbors_u.intersection(neighbors_v)
            for w in common:
                if w <= v:
                    continue

                triangles.append((u,v,w))
    return triangles

triangles = count_and_get_triangles(adjacency)
print(f"Number of triangles found in arrangement graph: {len(triangles)}")


id_to_point = {pid: intersection_points[h] for h, pid in point_id_map.items()}

def random_color():
    r = random.randint(100, 255)
    g = random.randint(100, 255)
    b = random.randint(100, 255)
    return f'#{r:02x}{g:02x}{b:02x}'

def redraw():
    canvas.delete("all")


    for p1, p2 in lines_to_draw:
        A, B, C = getEquation(p1, p2)

        left = (0 - offset_x) / scale
        right = (canvas_width - offset_x) / scale
        top = (0 - offset_y) / scale
        bottom = (canvas_height - offset_y) / scale

        points_line = []

        def y_at_x(x):
            return (-C - A * Decimal(x)) / B if B != 0 else None

        def x_at_y(y):
            return (-C - B * Decimal(y)) / A if A != 0 else None

        candidates = []
        if B != 0:
            y_left = y_at_x(left)
            if y_left is not None and top <= float(y_left) <= bottom:
                candidates.append((left, float(y_left)))
            y_right = y_at_x(right)
            if y_right is not None and top <= float(y_right) <= bottom:
                candidates.append((right, float(y_right)))
        if A != 0:
            x_top = x_at_y(top)
            if x_top is not None and left <= float(x_top) <= right:
                candidates.append((float(x_top), top))
            x_bottom = x_at_y(bottom)
            if x_bottom is not None and left <= float(x_bottom) <= right:
                candidates.append((float(x_bottom), bottom))

        unique_points = []
        for pt in candidates:
            if pt not in unique_points:
                unique_points.append(pt)

        if len(unique_points) < 2:

            if B == 0 and A != 0:
                x = float(-C / A)
                unique_points = [(x, top), (x, bottom)]
            elif A == 0 and B != 0:
                y = float(-C / B)
                unique_points = [(left, y), (right, y)]

        if len(unique_points) == 2:
            x1, y1 = world_to_screen(Vec2(Decimal(unique_points[0][0]), Decimal(unique_points[0][1])))
            x2, y2 = world_to_screen(Vec2(Decimal(unique_points[1][0]), Decimal(unique_points[1][1])))
            canvas.create_line(x1, y1, x2, y2, fill="#4299e1", width=3)

    for p in points:
        x, y = world_to_screen(p)
        canvas.create_oval(
            x - point_radius, y - point_radius,
            x + point_radius, y + point_radius,
            fill="#e53e3e", outline="#c53030"
        )


    for pt in intersection_points.values():
        x, y = world_to_screen(pt)
        r = 3
        canvas.create_oval(x - r, y - r, x + r, y + r, fill="black")

    for tri in triangles:
        pts = [id_to_point[pid] for pid in tri]
        pts_screen = [world_to_screen(p) for p in pts]
        color = random_color()
        canvas.create_polygon(
            *sum(pts_screen, ()),
            fill=color,
            outline="black",
            width=2
        )


last_x = None
last_y = None

def on_button_press(event):
    global last_x, last_y
    last_x, last_y = event.x, event.y

def on_move_press(event):
    global last_x, last_y, offset_x, offset_y
    dx = event.x - last_x
    dy = event.y - last_y
    last_x, last_y = event.x, event.y

    offset_x += dx
    offset_y += dy
    redraw()

def on_mousewheel(event):
    global scale, offset_x, offset_y

    mouse_x = event.x
    mouse_y = event.y
    zoom_factor = 1.1 if event.delta > 0 else 1 / 1.1

    new_scale = scale * zoom_factor
    if new_scale < 0.1:
        new_scale = 0.1
    if new_scale > 10:
        new_scale = 10

    wx_before = (mouse_x - offset_x) / scale
    wy_before = (mouse_y - offset_y) / scale
    wx_after = (mouse_x - offset_x) / new_scale
    wy_after = (mouse_y - offset_y) / new_scale

    offset_x += (wx_after - wx_before) * new_scale
    offset_y += (wy_after - wy_before) * new_scale

    scale = new_scale
    redraw()

canvas.bind("<ButtonPress-1>", on_button_press)
canvas.bind("<B1-Motion>", on_move_press)

if root.tk.call("tk", "windowingsystem") == 'win32':
    canvas.bind("<MouseWheel>", on_mousewheel)
else:
    canvas.bind("<Button-4>", lambda e: on_mousewheel(type('Event', (), {'delta': 120, 'x': e.x, 'y': e.y})))
    canvas.bind("<Button-5>", lambda e: on_mousewheel(type('Event', (), {'delta': -120, 'x': e.x, 'y': e.y})))

print(f"Number of triangles found in arrangement graph: {len(triangles)}")

redraw()
root.mainloop()
