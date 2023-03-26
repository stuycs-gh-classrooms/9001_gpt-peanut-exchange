from graphics import *

class EdgeList:
    def __init__(self):
        self.edges = []
        
    def add_edge(self, start, end):
        self.edges.append((start, end))
        
    def add_circle(self, cx, cy, cz, r, step=0.01):
        points = []
        for i in range(int(1/step) + 1):
            theta = i * step * 2 * pi
            x = r * cos(theta) + cx
            y = r * sin(theta) + cy
            z = cz
            points.append((x, y, z))
        self.add_curve(points, "bezier")
            
    def add_bezier(self, points, step=0.01):
        coefficients = generate_bezier_coefficients(points)
        bezier_points = []
        for t in np.arange(0, 1 + step, step):
            x = y = z = 0
            for i in range(len(points)):
                x += coefficients[i][0] * ((1-t)**(len(points)-1-i)) * (t**i) * points[i][0]
                y += coefficients[i][0] * ((1-t)**(len(points)-1-i)) * (t**i) * points[i][1]
                z += coefficients[i][0] * ((1-t)**(len(points)-1-i)) * (t**i) * points[i][2]
            bezier_points.append((x, y, z))
        self.add_curve(bezier_points, "line")
        
    def add_hermite(self, points, tangents, step=0.01):
        coefficients = generate_hermite_coefficients(points, tangents)
        hermite_points = []
        for t in np.arange(0, 1 + step, step):
            x = y = z = 0
            for i in range(len(points)):
                x += coefficients[i][0] * ((1-t)**(len(points)-1-i)) * (t**i) * points[i][0]
                y += coefficients[i][0] * ((1-t)**(len(points)-1-i)) * (t**i) * points[i][1]
                z += coefficients[i][0] * ((1-t)**(len(points)-1-i)) * (t**i) * points[i][2]
            hermite_points.append((x, y, z))
        self.add_curve(hermite_points, "line")
        
    def add_curve(self, points, curve_type):
        if curve_type == "line":
            for i in range(len(points) - 1):
                self.add_edge(points[i], points[i+1])
        elif curve_type == "bezier":
            for i in range(len(points) - 1):
                start = points[i]
                end = points[i+1]
                self.add_edge(start, end)
        else:
            raise ValueError("Invalid curve type")



class Drawing:
    def __init__(self, width, height, title):
        self.width = width
        self.height = height
        self.title = title
        self.win = GraphWin(title, width, height)
        self.edge_list = EdgeList()
        self.transform_matrix = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

    def parse_file(self, filename):
        with open(filename, 'r') as f:
            for line in f:
                command = line.strip()
                if command == 'line':
                    x0, y0, z0 = map(float, f.readline().split())
                    x1, y1, z1 = map(float, f.readline().split())
                    self.edge_list.add_edge((x0, y0, z0), (x1, y1, z1))
                elif command == 'circle':
                    cx, cy, cz, r = map(float, f.readline().split())
                    self.edge_list.add_circle(cx, cy, cz, r)
                elif command == 'hermite':
                    x0, y0, x1, y1, rx0, ry0, rx1, ry1 = map(float, f.readline().split())
                    self.edge_list.add_hermite(x0, y0, x1, y1, rx0, ry0, rx1, ry1)
                elif command == 'bezier':
                    x0, y0, x1, y1, x2, y2, x3, y3 = map(float, f.readline().split())
                    self.edge_list.add_bezier(x0, y0, x1, y1, x2, y2, x3, y3)
            
                elif command == 'ident':
                    self.transform_matrix = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
                elif command == 'scale':
                    sx, sy, sz = map(float, f.readline().split())
                    scale_matrix = [[sx, 0, 0], [0, sy, 0], [0, 0, sz]]
                    self.transform('multiply', scale_matrix)
                elif command == 'translate':
                    tx, ty, tz = map(float, f.readline().split())
                    translate_matrix = [[1, 0, 0, tx], [0, 1, 0, ty], [0, 0, 1, tz], [0, 0, 0, 1]]
                    self.transform('multiply', translate_matrix)
                elif command == 'rotate':
                    axis = f.readline().strip()
                    theta = float(f.readline())
                    if axis == 'x':
                        rotate_matrix = [[1, 0, 0], [0, cos(theta), -sin(theta)], [0, sin(theta), cos(theta)]]
                    elif axis == 'y':
                        rotate_matrix = [[cos(theta), 0, sin(theta)], [0, 1, 0], [-sin(theta), 0, cos(theta)]]
                    elif axis == 'z':
                        rotate_matrix = [[cos(theta), -sin(theta), 0], [sin(theta), cos(theta), 0], [0, 0, 1]]
                    self.transform('multiply', rotate_matrix)
                elif command == 'apply':
                    self.transform('apply')
                elif command == 'display':
                    self.win.delete('all')
                    for start, end in self.edge_list.edges:
                        self.draw_line(start, end)
                    self.win.update()
                    self.win.mainloop()
                elif command == 'save':
                    filename = f.readline().strip()
                    self.win.delete('all')
                    for start, end in self.edge_list.edges:
                        self.draw_line(start, end)
                    self.win.postscript(file=filename, colormode='color')
                elif command == 'quit':
                    break

    def draw_line(self, start, end):
        line = Line(Point(*start[:2]), Point(*end[:2]))
        line.draw(self.win)

    def transform(self, action, matrix=None):
        if action == 'apply':
            for i, (start, end) in enumerate(self.edge_list.edges):
                start = self.apply_transform(start)
                end = self.apply_transform(end)
                self.edge_list.edges[i] = (start, end)
        elif action == 'multiply':
            self.transform_matrix = self.matrix_multiply(self.transform_matrix, matrix)
    def apply_transform(self, point):
        x, y, z = point
        x_new = x * self.transform_matrix[0][0] + y * self.transform_matrix[0][1] + z * self.transform_matrix[0][2]
        y_new = x * self.transform_matrix[1][0] + y * self.transform_matrix[1][1] + z * self.transform_matrix[1][2]
        z_new = x * self.transform_matrix[2][0] + y * self.transform_matrix[2][1] + z * self.transform_matrix[2][2]
        return x_new, y_new, z_new

    def matrix_multiply(self, a, b):
        if len(a[0]) != len(b):
            raise ValueError("Matrices have incompatible dimensions")
        result = []
        for i in range(len(a)):
            row = []
            for j in range(len(b[0])):
                sum = 0
                for k in range(len(b)):
                    sum += a[i][k] * b[k][j]
                row.append(sum)
            result.append(row)
        return result


    def run(self):
        self.parse_file('script.txt')
        if name == 'main':
            drawing = Drawing(500, 500, 'Drawing')
            drawing.run()

if __name__ == '__main__':
    d = Drawing(500,500,"y")
    d.parse_file('script.txt')

#Note: This program uses the `graphics` module, which provides a simple interface for creating graphics in Python. If you don't have this module installed, you can install it using pip: `pip install graphics`. Also, make sure to replace `script.txt` in the `parse_file` method with the actual filename of your script file.
