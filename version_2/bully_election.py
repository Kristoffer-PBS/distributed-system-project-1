from enum import Enum, unique
import xmlrpc.server
import xmlrpc.client
import zerorpc
import gevent

import sys
import time
import select
import socket
import pickle
import random

from typing import List
from typing import Optional
from typing import Union


def try_to_print(some_num: Optional[int]):
    if some_num:
        print(some_num)
    else:
        print('Value was None!')


# use tcp protocol to listen on localhost port 7000
# tcp://127.0.0.1:7000

# ----------------------------------------------------------------------------------------------------------------------


@unique  # class decorator
class State(Enum):
    """
    Enumerated type defining the the types of "behaviour state" a Node can be in.
        Possible states:
            @Down           -- Node is down.
            @Election       -- Node is partaking in an election, and is not available for other work.
            @Normal         -- Normal state of operation, when coordinator is known.
            @Reorganization -- The topology of the network has changed, and the Node has to update its own internal
                               representation of the known nodes in the network.

        methods/implementations:
            The built-in str() function has been implemented for this type.
    """
    Down = 1
    Election = 2
    Normal = 3
    Reorganization = 4

    def __str__(self) -> str:
        return "in state: {}".format(self.name)
# ----------------------------------------------------------------------------------------------------------------------


class StateVector():
    def __init__(self):
        # * my implement
        # self.state = State()
        self.state = State.Normal

        # state of the node
        # [Down, Election, Reorganization, Normal]
        # self.state = "Normal"
        # id of the coordinator
        self.coordinator: int = 0
        # description of the task
        self.description = None

        # the node who recently made this node halt execution
        self.halt = -1

        # list of nodes which this node belieces to be in operation
        # Up
        self.nodes: = []


class Node():
    """
    Node class representing a single node in the network.
        data/state:
            @addr: str -- The socket identifier e.g. '127.0.0.1:9000'
            @connections: list[xmlrpc.client]
            @number_of_connnections: int  -- the number of connections to check

        methods:
            __init__(addr: str, config_file: Optional<str>): None
            check_coordinator():
            election(): None


        exceptions:

    """

    def __init__(self, addr: str, config_file='server_config'):
        self.addr: str = addr
        self.state_vector = StateVector()
        self.state_vector.state = "Normal"

        config_file = open("server.config", "r")
        self.servers = []

        # * what does this do???
        self.check_servers_greenlet = None

        for line in config_file.readlines():
            line = line.rstrip()   # strip \r and \n characthers from the end of the string
            self.servers.append(line)

        print("My address: {}".format(self.addr))
        print("Server list: {}".format(str(self.servers)))

        self.number_of_connections: int = len(self.servers)

        self.conntections: List[int] = []

        # Iterate through the list of potential nodes/servers in our network, which
        # is constant at the initialization of the network. i.e. we specify
        # the maximum number of nodes that can be in our network topology.
        # for each network address, we create an rcp client on the specific
        # socket port, and append it to a list of connections.
        for (idx, server) in enumerate(self.servers):
            # One of the strings in the file 'server.config' will be the port
            # of the current process i.e. itself. We use this address to extract
            # the unique ID, used in the election algorithm.
            if server == self.addr:
                self.idx = idx
                # why do we connect ourself to this list?
                self.conntections.append(self)
            else:
                # create client
                client = zerorpc.Client(timeout=2)
                # tcp = "tcp://" + server
                # append the server port to the tcp header
                tcp = "tcp://{}".format(server)
                client.connect(tcp)
                # client.connect("tcp://" + server)
                self.conntections.append(client)

    def are_you_there(self) -> bool:
        return True

    def are_you_normal(self) -> bool:
        if self.state_vector.state is State.Normal:
            return True
        else:
            return False

    # * what is j
    def halt(self, j) -> None:
        self.state_vector.state = State.Election
        self.state_vector.halt = j

    def new_coordinator(self, j) -> None:
        print("Call new_coordinator")
        if self.state_vector.halt == j and self.state_vector.state is State.Election:
            self.state_vector.coordinator = j
            self.state_vector.state = State.Reorganization

    def ready(self, j, x=None):
        print("Call ready")
        if self.state_vector.coordinator == j and self.state_vector.state is State.Reorganization:
            self.state_vector.description = x
            self.state_vector.state = State.Normal

    # Juicy part!
    def election(self):
        """
        Election a new coordinator node of the network using the Bully Election Algorithm
        STEPS:
            1.
            2.
            3.
            4.
        """
        print("Chekc the states of higher priority nodes:")

        # Only send an 'are_you_OK' to nodes with a higher index that self, because
        # it is unnessesary to ask the ones lower
        for (idx, server) in enumerate(self.servers[self.idx + 1:]):
            try:
                self.conntections[self.idx + 1 +
                                  idx].are_you_there()  # rpc call
                if self.check_servers_greenlet is None:
                    self.state_vector.coordinator = self.idx + 1 + idx
                    self.state_vector.state = State.Normal
                    self.check_servers_greenlet = self.pool.spawn(self.check())
                return
            except zerorpc.TimeoutExpired:
                print("{} Timeout!".format(server))

        print("halt all lower priority nodes including this node:")
        self.halt(self.idx)
        self.state_vector.state = State.Election
        self.state_vector.halt = self.idx
        self.state_vector.nodes = []

        for (idx, server) in enumerate(self.servers[self.idx::-1]):
            try:
                self.conntections[idx].halt[self.idx]
            except zerorpc.TimeoutExpired:
                print("{} Timeout".format(server))
                continue
            self.state_vector.nodes.append(self.conntections[idx])

        # reached 'election point', inform nodes of new coordinator
        print("Inform nodes of new coordinator:")
        self.state_vector.coordinator = self.idx
        self.state_vector.state = State.Reorganization
        for j in self.state_vector.nodes:
            try:
                j.new_coordinator(self.idx)
            except zerorpc.TimeoutExpired:
                print("Timeout! Election will be restarted")
                self.election()
                return

        # Reorganization
        for node in self.state_vector.nodes:
            try:
                node.ready(self.idx, self.state_vector.description)
            except zerorpc.TimeoutExpired:
                print("Timeout!")
                self.election()
                return

        self.state_vector.state = State.Normal
        print("[{}] Starting ZeroRPC Server".format(self.servers[self.idx]))
        self.check_servers_greenlet = self.pool.spawn(self.check())

    def recovery(self):
        self.state_vector.halt = -1
        self.election()

    # TODO should have a different name
    def check(self):
        """
        The main loop of the Node, where connection to the coordinator is periodically checked
        And based on the response a possible election is hold.
        """
        while True:
            gevent.sleep(2)  # sys.sleep(2)

            # If node is the coordinator
            if self.state_vector.state is State.Normal and self.state_vector.coordinator == self.idx:
                for (idx, server) in enumerate(self.servers):
                    if idx != self.idx:
                        try:
                            # rpc call
                            answer = self.conntections[idx].are_you_normal()
                            print("{} : are_you_normal = {}".format(
                                server, answer))
                        except zerorpc.TimeoutExpired:
                            print("{} Timeout!".format(server))
                            continue

                        # if we do not receive a response we start an election
                        # but why should the coordinator start an election
                        # if it registers a lower node is not responding ???
                        # TODO
                        if not answer:
                            self.election()
                            return

            # if node is not the coordinator
            # FIXME why do we say elif, a node can either be the coordinator or not, so by
            # simply checking if it is a coordnator above, we can conclude that it is not otherwise.
            elif self.state_vector.state is State.Normal and self.state_vector.coordinator != self.idx:
                print("check coordinator's state")
                try:
                    result = self.conntections[self.state_vector.coordinator].are_you_there(
                    )
                    print("{} : are_you_there = {}".format(
                        self.servers[self.state_vector.coordinator], result))
                # The exception is used to deduce that the coordinator is down, and
                # that we then have to hold an election to find a new coordinator
                except zerorpc.TimeoutExpired:
                    print("coordinator down, raise election.")
                    self.timeout()

    def timeout(self):
        """
        """
        # FIXME how is the state related to the allowed functionality
        if self.state_vector.state is State.Normal or self.state_vector.state is State.Reorganization:
            try:
                self.conntections[self.state_vector.coordinator].are_you_there()
            except zerorpc.TimeoutExpired:
                print("{} Timeout!".format(
                    self.servers[self.state_vector.coordinator]))
                self.election()
        else:
            self.election()

    def start(self):
        self.pool = gevent.pool.Group()
        self.recovery_greenlet = self.pool.spawn(self.recovery)


def main() -> None:
    """
    Initialize the node and start the rpc server.
    """
    if len(sys.argv) != 2:
        print("No tcp address was specified - python bully.py <port> e.g. '127.0.0.1:9000")
        sys.exit(1)

    addr: str = sys.argv[1]
    node: Node = Node(addr)
    server = zerorpc.Server(node)
    tcp: str = "tcp://" + addr
    server.bind("tcp://" + addr)
    # server.bind(tcp)
    node.start()

    print("[{}] Starting node at port!".format(addr))
    server.run()


if __name__ == '__main__':
    main()
