class Node:

    def __init__(self, id, x, y, color = None):
        self.id = id # identification number
        self.x = x
        self.y = y
        self.color = color
        self.connections = set() # all connections must be reciprocal!
        self.domain = ['white', 'blue', 'red', 'green']

    def __str__(self):
        return str((self.id, self.x, self.y, self.connections, self.color, self.domain))

    def link(self, neighbor):
        # Links two Nodes
        self.connections.add(neighbor.id)
        neighbor.connections.add(self.id)

    def unlink(self, neighbor):
        # Unlinks
        self.connections.remove(neighbor.id)
        neighbor.connections.remove(self.id)