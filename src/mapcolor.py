import random
import svgwrite
import math
import Queue
from collections import namedtuple
import sys
sys.setrecursionlimit(100000)

import time

start_time = time.time()

Point = namedtuple('Point', 'x y')
Line = namedtuple('Line', 'A B Avar Bvar')

from node import *


flag = False

class MapColor:
    def __init__(self, N):
        self.map = [Node(i, random.randint(100, 600), random.randint(100, 600)) for i in range(0, N)]
        # List of Nodes. N number of Nodes auto-generated upon instantiation of MapColor.
        self.lines = []
        # List of lines kept and maintained independently of connection information stored within Nodes.
        # Provides easy, efficient access to all manifested connections for intersection detection and final drawing.
        self.N = N
        # N value stored. Only used in filename to indicate N size.
        self.values = ['white', 'red', 'green', 'blue']
        # Domain of values
        self.number_of_assignments = 0
        # Increments each time a variable is assigned a value
        self.connect()
        self.efficiency_bool = False


    def find_by_id(self, id):
        # Given a Node ID, returns the Node itself or notify of error.
        for variable in self.map:
            if variable.id == id:
                return variable
        else:
            print str(id) + " not found." if flag is True else ()


    def draw(self):
        # Draws and saves the color map.
        map = self.map
        runtime = time.time() - start_time
        self.efficiency_label = "Inefficient"
        if self.efficiency_bool is True: self.efficiency_label = "Efficient"
        name = "results/" + self.efficiency_label + " N=" + str(self.N) + " E=" + str(len(self.lines)) + " A=" + str(self.number_of_assignments) + " T:" + str(runtime * 1000) + "ms.svg"
        # filename: into results directory, N size, E number of edges, A number of assignments, runtime in milliseconds
        dwg = svgwrite.Drawing(filename=name, size=(700, 700), debug=True)
        # Actual working canvas is 500 by 500. A 100 margin is put in all around.
        for line in self.lines:
            dwg.add(dwg.line((line.A.x, line.A.y), (line.B.x, line.B.y), stroke=svgwrite.rgb(10, 10, 16, '%')))
        for variable in map:
            color = variable.color
            if variable.color is None:
                color = 'white'
            dwg.add(dwg.circle(center=(variable.x, variable.y), r=10, fill=color, stroke='black'))
            paragraph = dwg.add(dwg.g(font_size=12))
            paragraph.add(dwg.text(variable.id, (variable.x - 4, variable.y + 5)))
            # Labels points by Node id number
        print (time.time() - start_time) * 1000
        dwg.save()


    def connect(self):
        # Generates connections and lines between Nodes in map.
        print "Connecting..."
        q = Queue.Queue()
        q.put(random.choice(self.map))

        while q.qsize() is not 0:
            current_variable = q.get()
            neighbor = self.find_nearest_unconnected_point(current_variable, self.map, self.lines)
            if flag is True: print str(current_variable.id) + "?->" + str(neighbor.id)
            bool_are_unconnectable = self.are_connectable(current_variable, neighbor, self.lines)
            bool_are_unconnected = self.are_unconnected(current_variable, neighbor)
            bool_is_self = False
            if current_variable is not neighbor:
                bool_is_self = True
            if bool_are_unconnectable and bool_are_unconnected and bool_is_self:
                if flag is True: print str(current_variable.id) + "->" + str(neighbor.id)
                current_variable.link(neighbor)
                # Connection is stored within the nodes. This information will be used for the actual CSP backtracking.
                new_line = Line(Point(current_variable.x, current_variable.y), Point(neighbor.x, neighbor.y),
                                current_variable, neighbor)
                self.lines.append(new_line)
                # Line representing the connection is stored: coordinates of endpoints as well as references to the endpoint Nodes.
                # As noted, lines are used for intersection detection and final drawing only, not CSP backtracking.
                q.put(neighbor)
                q.put(current_variable)
                # Add line to lines list. This is purely for line intersection detection and line drawing.
            elif flag is True:
                str(current_variable.id) + "!->" + str(neighbor.id) + " : " + str((bool_are_unconnectable, bool_are_unconnected, bool_is_self))
        print "Connecting done."

    def solve_randomly(self):
        i = 0
        while self.check_consistency() is False:
            random_variable = random.choice(self.map)
            random_value = random.choice(self.values)
            self.assign_color(random_variable, random_value)
            print "round " + str(i)
            i = i + 1

    def backtrack(self, efficient = False):
        if efficient:
            self.efficiency_bool = True
        self.map = self.recursive_backtracking(self.map, efficient, 0)

    def recursive_backtracking(self, map, efficient, depth = 0):
        print depth
        if self.is_complete(map) is True:
            print "Is complete."
            return map
        elif depth == 1000:
            print "Is incomplete. Result printed anyway."
        variable = self.select_unassigned_variable(map, efficient)
        print variable.domain
        for value in variable.domain:
            if self.is_consistent(variable, value):
                self.assign_color(variable, value, efficient)
                result = self.recursive_backtracking(map, efficient, depth+1)
                if self.is_complete(map) is True:
                    return result
                self.unassign_color(variable, efficient)


    def select_unassigned_variable(self, map, efficient):
        if efficient:
            pq = Queue.PriorityQueue()
            for variable in map:
                if self.is_assigned(variable) is False:
                    pq.put(((-1)*len(variable.domain), variable))
                    # Negative such that smallest domain -> most constrained -> m c variable will have highest priority
            return pq.get()[1]
            # get variable, not priority value, in tuple
        else:
            for variable in map:
                if self.is_assigned(variable) is False:
                    return variable
        print "No unassigned variable left"
        return random.choice(map)


    def is_assigned(self, variable):
        if variable.color is None:
            return False
        else:
            return True

    def is_complete(self, map):
        for variable in map:
            if self.is_consistent(variable) is False:
                return False
        return True

    def is_consistent(self, variable, color = None):
        if color is None:
            for neighbor_id in variable.connections:
                neighbor = self.find_by_id(neighbor_id)
                if neighbor.color is variable.color or variable.color is None:
                    return False
                #print str(variable.id) + " consistent with " + str(neighbor.id)
                #print neighbor.color + " <> " + variable.color
        else:
            for neighbor_id in variable.connections:
                neighbor = self.find_by_id(neighbor_id)
                if neighbor.color is color:
                    return False
                #print str(variable.id) + " consistent with " + str(neighbor.id)
        return True

    def assign_color(self, variable, color, efficient):
        variable.color = color
        if efficient:
            self.update_domain(variable, color)
        self.number_of_assignments = self.number_of_assignments + 1
        #print str(variable.id) + " assigned " + color

    def unassign_color(self, variable, efficient):
        if efficient:
            self.update_domain(variable, variable.color, True)
        variable.color = None
        #print str(variable.id) + " unassigned"

    def update_domain(self, variable, color, unassigning = False):
        if unassigning is False: # i.e. assigning
            variable.domain.remove(color)
            for neighbor_id in variable.connections:
                neighbor = self.find_by_id(neighbor_id)
                if color in neighbor.domain:
                    neighbor.domain.remove(color)
        else:
            variable.domain.append(variable.color)
            for neighbor_id in variable.connections:
                neighbor = self.find_by_id(neighbor_id)
                if color not in neighbor.domain:
                    neighbor.domain.append(color)

    def all_are_assigned(self, map):
        number_of_assigned = 0
        for variable in map:
            number_of_assigned = number_of_assigned + 1
            if self.is_assigned(variable):
                return False
        return True

    def find_nearest_unconnected_point(self, current_variable, map, lines):
        # Finds neighbor point/Node that is 1. nearest but also 2. unconnected and 3. connectable.
        nearest_found = current_variable
        nearest_distance = float("inf")  # Infinite for practical purposes
        for neighbor in map:
            # Looks at all other nodes in map.
            neighbor_distance = self.find_distance(current_variable, neighbor)
            if neighbor_distance <= nearest_distance and neighbor is not current_variable and self.are_unconnected(
                    current_variable, neighbor) and self.are_connectable(current_variable, neighbor, lines):
                nearest_found = neighbor
                nearest_distance = neighbor_distance
        return nearest_found


    def find_distance(self, variable, target):
        # Finds distance between two Nodes
        delta_x = variable.x - target.x
        delta_y = variable.y - target.y
        distance = math.sqrt(math.pow(delta_x, 2) + math.pow(delta_y, 2))
        return distance


    def find_length(self, line):
        # Finds length of a Line named tuple.
        # Function defined for clarity.
        return self.find_distance(line.A, line.B)


    def are_unconnected(self, variable_A, variable_B):
        # Checks to see a connection exists between the two Nodes.
        if variable_A.id in variable_B.connections or variable_B.id in variable_A.connections:
            return False
        else:
            return True


    def are_connectable(self, variable_A, variable_B, lines):
        # Checks for intersections between proposed line and ALL other lines. This is not efficient for a large N size!
        #intended_line = Line(Point(variable_A.x, variable_A.y), Point(variable_B.x, variable_B.y), variable_A, variable_B)
        for line in lines:
            if self.do_intersect(variable_A, variable_B, line.A, line.B):
                if flag is True: print str(variable_A.id) + "->" + str(variable_B.id) + " x " + str(line.Avar.id) + "->" + str(line.Bvar.id)
                return False
        return True


    def do_intersect(self, A, B, C, D):
        # Checks for intersection btwn lines AB and CD
        def ccw(A, B, C):
            # Helper function for do_intersect.
            return (C.y - A.y) * (B.x - A.x) > (B.y - A.y) * (C.x - A.x)

        if (A.x is C.x and A.y is C.y) or (A.x is D.x and A.y is D.y) or (B.x is C.x and B.y is C.y) or (
                        B.x is D.x and B.y is D.y):
            # Without this conditional, the function would otherwise consider coinciding endpoints to be intersections.
            if flag is True: print "False intersection!"
            return False
        return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)