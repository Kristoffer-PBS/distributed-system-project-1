#!/usr/bin/env python

import zerorpc
import gevent

import sys


# Bully Algorithm
# - Each node has an unique ID
# - Each node communicates with each other and broadcasts their ID
# - The node which has the highest ID becomes the leader.

# If P receives a Coordinator message, it treats the sender as the coordinator

# When any process notices that the coordinator is no longer responding to requests, it initiates an election.

# When to elect a coordinator
# - When the system


class Node:
    """ Node class representing a single node in the network.
        data:
            @node_id: unsigned int --
            @coordinator: unsigned int --
            @coordinator_id: unsigned int --
            @active: bool --
            @nodes: [Node] --

        methods:
            activate() --
            check_coordinator() -
            deactivate() --
            election() -

        exceptions:
            No exceptions can be trown by this class
    """

    def __init__(self, node_id, coordinator_id=None, coordinator=False):
        """ Constructor method
        """
        self.active = True
        self.coodinator = coordinator
        self.coodinator_id = coordinator_id
        self.node_id = node_id
        self.nodes = []

    def activate(self):
        self.active = True
        self.election()

    def announce_victory(self, list_of_nodes):
        """
        """
        for node in list_of_nodes:
            node.leader_id = self.PID

    def check_coordinator(self):
        """
        """
        pass

        msg "foo"

        if not msg == "OK":
            self.election()

    def election(self):
        """
        """
        # node i attepts to become coordinator.
        # First step is to check if any higher priority nodes  are up,
        # iff any such nodee is up, quit.
        pass

    def respond(self):
        """ Respond with OK if alive """
        pass

    def is_leader(self):
        """
        """
        return self.leader


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

    def deattach(self, PID):
        if PID < self.counter:
            self.nodes.pop(PID)
            self.counter -= 1

    def initialize(self):

        # initialize system by finding a leader
        pass

    def tick(self):
        """Represent one logic progression in time"""
        for node in self.nodes:
            node.check_coordinator()


# Testing code

def main():
    nw = Network()
    nw.attach(Node(1))
    nw.attach(Node(2))
    nw.attach(Node(3))
    nw.attach(Node(4))
    nw.attach(Node(5))
    nw.attach(Node(6))
    # ....

    nw.initialize()

    for i in range(0, 100):
        nw.tick()

    # sdsd

    # need to test if the coordinator  in the system goes down
    # and when a node that is not the coordinator goes down


if __name__ == "__main__":
    main()
