# Improved Bully Algorithm


class Node:
    """ Node class representing a single node in the network.
        data:
            @node_id:
            @leader_id:
            @coordinator:
    """

    def __init__(self, node_id, leader_id=0):
        self.node_id = node_id
        self.leader_id = leader_id
        self.nodes = []

    def announce_victory(self, list_of_nodes):
        for node in list_of_nodes:
            node.leader_id = self.PID
    
    def check_coordinator(self):
        pass

    def election(self):
        pass

    def respond(self):
        pass

    def is_leader(self):
        return self.leader

class Network:
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

def main():
    nw = Network()
    nw.attach(Node(1))
    nw.attach(Node(2))
    # ....

    nw.initialize()

    # sdsd

    # need to test if the coordinator  in the system goes down
    # and when a node that is not the coordinator goes down


if __name__ == "__main__":
    main()
