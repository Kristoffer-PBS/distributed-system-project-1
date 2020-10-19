# Bully Algorithm
# - Each node has an unique ID
# - Each node communicates with each other and broadcasts their ID
# - The node which has the highest ID becomes the leader.

# If P receives a Coordinator message, it treats the sender as the coordinator


class Node:
    __init__(self, pid, coordinator = False):
        self.PID = pid
        self.leader = False
        self.coordinator = coordinator

    

    

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
        self.nodes = {}

    def attach(self, PID):
        pass

    def deattach(self, PID):
        pass



def main():
    pass

if __name__ == "__main__":
    main()