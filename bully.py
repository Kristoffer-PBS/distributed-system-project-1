# Bully Algorithm
# - Each node has an unique ID
# - Each node communicates with each other and broadcasts their ID
# - The node which has the highest ID becomes the leader.

# If P receives a Coordinator message, it treats the sender as the coordinator

# When any process notices that the coordinator is no longer responding to requests, it initiates an election.

# When to elect a coordinator
# - When the system 


class Node:
    __init__(self, pid, coordinator = False, leader_id = 0):
        self.PID = pid
        self.coodinator = coordinator
        self.leader_id = 0

    
    def announce_victory(self, list_of_nodes):
        for node in list_of_nodes:
            node.leader_id = self.PID
    

    def check_coordinator(self):
        pass

        msg "foo"

        if not msg == "OK":
            self.election()


    def election(self):
        pass

    def respond(self):
        """ Respond with OK if alive """
        pass

    def is_leader(self):
        return self.leader


class Network:
    __init__(self):
        self.counter = 0
        self.nodes = []  # list of nodes


    def attach(self, node):
        nodes.attach(node)

    def deattach(self, PID):
        pass

    def initialize(self):
        # initialize system by finding a leader
        pass



def main():
    nw = Network()
    nw.attach(Node(1))
    nw.attach(Node(2))
    # ....

    nw.initialize()
    


if __name__ == "__main__":
    main()