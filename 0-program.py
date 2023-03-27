from graphics import *

class EdgeList:
    def __init__(self):
        self.edges = []

    def add_edge(self, start, end):
        self.edges.append((start, end))

class Drawing:
    def __init__(self, width, height, title):
        self.width = width
        self.height = height
        self.title = title
        self.win = GraphWin(title, width, height)

    def draw_line(self, start, end):
        line = Line(Point(*start), Point(*end))
        line.draw(self.win)

    def draw_circle(self, center, radius):
        circle = Circle(Point(*center), radius)
        circle.draw(self.win)

    def draw_bezier_curve(self, p0, p1, p2, p3):
        curve = Curve(Point(*p0), Point(*p1), Point(*p2), Point(*p3))
        curve.draw(self.win)

    def draw_hermite_curve(self, p0, p1, t0, t1):
        curve = Curve(Point(*p0), Point(*p1), t0, t1)
        curve.draw(self.win)

    def transform(self, trans_matrix):
        for obj in self.win.items[:]:
            if isinstance(obj, Line):
                obj.setStart(Point(*self.matrix_mult(trans_matrix, obj.getP1())))
                obj.setEnd(Point(*self.matrix_mult(trans_matrix, obj.getP2())))
            elif isinstance(obj, Circle):
                obj.move(*self.matrix_mult(trans_matrix, obj.getCenter()))
            elif isinstance(obj, Curve):
                for i, cp in enumerate(obj.getPoints()):
                    obj.setPoint(i, Point(*self.matrix_mult(trans_matrix, cp)))

    def rotate(self, angle):
        theta = radians(angle)
        rot_matrix = [[cos(theta), -sin(theta)], [sin(theta), cos(theta)]]
        self.transform(rot_matrix)

    def dilate(self, scale):
        dil_matrix = [[scale, 0], [0, scale]]
        self.transform(dil_matrix)

    def matrix_mult(self, matrix, point):
        x, y = point
        a, b = matrix[0]
        c, d = matrix[1]
        new_x = a * x + b * y
        new_y = c * x + d * y
        return new_x, new_y

    def save_image(self, filename):
        self.win.postscript(file=filename, colormode='color')

    def display_image(self):
        self.win.mainloop()
