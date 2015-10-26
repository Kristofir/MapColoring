import random
import svgwrite
import math
import Queue
from collections import namedtuple

import time
start_time = time.time()

Point = namedtuple('Point', 'x y')
Line = namedtuple('Line', 'A B Avar Bvar')

from node import *


class MapColor:
    def __init__(self, N):
        self.map = [Node(i, random.randint(100, 600), random.randint(100, 600)) for i in range(0, N)]
        self.lines = []
        self.N = N
        # list of lines kept independent of internally stored node connections, for intersection detection

    def find_by_id(self, id):
        for variable in self.map:
            if variable.id == id:
                return variable
        else:
            print str(id) + " not found."

    def draw(self):
        map = self.map
        runtime = time.time() - start_time
        name = "N="+str(self.N)+" "+str(runtime*1000) + "ms.svg"
        dwg = svgwrite.Drawing(filename=name, size=(700, 700), debug=True)
        for line in self.lines:
            dwg.add(dwg.line((line.A.x, line.A.y), (line.B.x, line.B.y), stroke=svgwrite.rgb(10, 10, 16, '%')))
        for variable in map:
            dwg.add(dwg.circle(center=(variable.x, variable.y), r=10, fill=variable.color, stroke='black'))
            paragraph = dwg.add(dwg.g(font_size=12))
            paragraph.add(dwg.text(variable.id, (variable.x - 4, variable.y + 5)))
        print (time.time() - start_time)*1000
        dwg.save()

    def connect(self):
        print "Connecting..."
        q = Queue.Queue()
        end = False
        # for variable in self.map:
        #    #print variable
        #    q.put(variable)
        q.put(random.choice(self.map))

        while q.qsize() is not 0:
            current_variable = q.get()
            neighbor = find_nearest_unconnected_point(current_variable, self.map, self.lines)
            print str(current_variable.id) + "?->" + str(neighbor.id)
            bool_are_unconnectable = are_connectable(current_variable, neighbor, self.lines)
            bool_are_unconnected = are_unconnected(current_variable, neighbor)
            bool_is_self = False
            if current_variable is not neighbor:
                bool_is_self = True
            if bool_are_unconnectable and bool_are_unconnected and bool_is_self:
                print str(current_variable.id) + "->" + str(neighbor.id)
                current_variable.link(neighbor)
                # Above linking will be used for CSP solving
                new_line = Line(Point(current_variable.x, current_variable.y), Point(neighbor.x, neighbor.y),
                                current_variable, neighbor)
                self.lines.append(new_line)
                q.put(neighbor)
                q.put(current_variable)
                # Add line to lines list. This is purely for line intersection detection and line drawing.
            else:
                print str(current_variable.id) + "!->" + str(neighbor.id) + " : " + str((bool_are_unconnectable, bool_are_unconnected, bool_is_self))
        print "Connecting done."


def find_nearest_unconnected_point(current_variable, map, lines):
    nearest_found = current_variable
    nearest_distance = 99999  # practically infinite
    for neighbor in map:
        neighbor_distance = find_distance(current_variable, neighbor)
        if neighbor_distance <= nearest_distance and neighbor is not current_variable and are_unconnected(
                current_variable, neighbor) and are_connectable(current_variable, neighbor, lines):
            nearest_found = neighbor
            nearest_distance = neighbor_distance
    return nearest_found


def find_distance(variable, target):
    delta_x = variable.x - target.x
    delta_y = variable.y - target.y
    distance = math.sqrt(math.pow(delta_x, 2) + math.pow(delta_y, 2))
    return distance


def find_length(line):
    # line : Line tuple
    return find_distance(line.A, line.B)


def are_unconnected(variable_A, variable_B):
    # explanation for min and max:
    # connection is stored within keys list as a tuple.
    # tuple is of connected variables' ids: smaller one first.
    if variable_A.id in variable_B.connections or variable_B.id in variable_A.connections:
        return False
    else:
        return True


def are_connectable(variable_A, variable_B, lines):
    intended_line = Line(Point(variable_A.x, variable_A.y), Point(variable_B.x, variable_B.y), variable_A, variable_B)
    for line in lines:
        if do_intersect(variable_A, variable_B, line.A, line.B):
            print str(variable_A.id) + "->" + str(variable_B.id) + " x " + str(line.Avar.id) + "->" + str(line.Bvar.id)
            return False
    return True


def do_intersect(A, B, C, D):
    # checks for intersection btwn lines AB and CD
    def ccw(A, B, C):
        # Helper function for do_intersect.
        return (C.y - A.y) * (B.x - A.x) > (B.y - A.y) * (C.x - A.x)

    if (A.x is C.x and A.y is C.y) or (A.x is D.x and A.y is D.y) or (B.x is C.x and B.y is C.y) or (
                    B.x is D.x and B.y is D.y):
        # Without this conditional, the function would otherwise consider coinciding endpoints to be intersections.
        print "False intersection!"
        return False
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)


mapcolor = MapColor(15)
mapcolor.connect()
mapcolor.draw()
for i in mapcolor.map:
    print i
