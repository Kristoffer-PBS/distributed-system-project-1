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

    def check_coordinator(self):
        pass

    def election(self):
        pass

    def respond(self):
        pass


class Network:
    def __init__(self):
        self.counter = 0
        self.nodes = []  # list of nodes

    def attach(self, node):
        self.nodes.append(node)

    def deattach(self, node):
        pass


def main():
    pass


if __name__ == "__main__":
    main()
