#!/usr/bin/env python

# Improved Bully Algorithm
# based on the work presented in the article ...

# Assumptions:

# Limitations (details omitted for simplicity of implementation)

class Node:
    """ Node class representing a single node in the network.
        data:
            @active: bool --
            @coordinator: bool --
            @coordinator_id: unsigned int --
            @election_is_on: bool -- unique to the improved version
            @node_id: unsigned int --
            @nodes: [Node] --

        methods:
            activate()         : None  --
            check_coordinator(): None  --
            deactivate()       : None  --
            election()         : None  --

        exceptions:
            No exceptions can be trown by this class
    """

    def __init__(self, node_id, coordinator_id=None, coordinator=False):
        """ Constructor method
        """
        self.active = True
        self.coodinator = coordinator
        self.coordinator_id = coordinator_id
        self.election_is_on = False  # unique to improved version
        self.node_id = node_id
        self.nodes = []

    def activate(self):
        self.active = True
        self.election()

    def check_coordinator(self):
        pass

    def election(self):
        pass

    def respond(self):
        pass


class Network:
    """ Network class representing a network of nodes.
        data:
            @counter: unsigned int -- number of active nodes in the network
            @nodes: [node]         -- List of nodes

        methods:
            attach(node: Node) -
            deattach(node_id: unsigned int) -
            initialize() -
            tick()

        exceptions:
            No exceptions can be trown by this class
    """

    def __init__(self):
        self.counter = 0
        self.nodes = []  # list of nodes

    def attach(self, node):
        self.nodes.append(node)
        self.counter += 1

    def deattach(self, node_id):
        if node_id < self.counter:
            self.nodes.pop(node_id)
            self.counter -= 1
        pass

    def initialize(self):
        pass
        # at initialization we allready know which node is the highest one, so we
        # can just ask the highest node, to notify the other nodes, and tell
        # them it is the coordinator.
        self.nodes[self.counter].is_coordinator()

    def tick(self):
        """Represent one logic progression in time"""
        for node in self.nodes:
            node.check_coordinator()


def main():
    pass


if __name__ == "__main__":
    main()
