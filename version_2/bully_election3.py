# import http.client
# from xmlrpc.server import SimpleXMLRPCServer
# from xmlrpc.server import SimpleXMLRPCRequestHandler
# import xmlrpc.server
# import xmlrpc.client
# import time
# import select
# import socket
# import pickle
# import random

from enum import Enum, unique
from termcolor import colored, cprint
from typing import List, Optional, Union

import sys
import inspect  # used for

import gevent
import zerorpc
from gevent import pool

def getLineInfo():
    """
    Helper function for debug purposes
    """
    print(inspect.stack()[1][1], ":", inspect.stack()[1][2], ":",
          inspect.stack()[1][3])


def node_print():
    pass

# ----------------------------------------------------------------------------------------------------------------------

# TODO test if the is operator works correctly


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


class Node():
    """
    Node class representing a single node in the network.
        data/state:
            @addr: str -- The socket identifier e.g. '127.0.0.1:9000'
            @check_servers_greenlet: Optional[]  -- an abstraction for a light thread, which is used to schedule
            asynchronous calls, and prevent a deadlock between nodes, where each node end up blocking
            each other such, that no on can respond.
            @connections: list[xmlrpc.client]
            @state: State -- The different behaviour a node can be in
            @number_of_connnections: int  -- the number of connections to check

        methods:
            __init__(addr: str, config_file: Optional<str>)
            check_coordinator() ->
            check_netork() -> None
            COORDINATOR(coordinator_id: int) -> None
            election() -> None
            HALT()
            initialize() -> None
            new_coordinator(coordinator_id: int) -> None --
            OK() -> bool

        exceptions:
            None

    """
    # DONE

    def __init__(self, addr: str, config_file='server_config'):
        self.addr: str = addr
        self.check_servers_greenlet = None
        self.coordinator: int = 9    # 9 is the highest node ID in our 'server.config' file
        self.halter: int = -1
        self.idx = 0
        # list of nodes which this node belieces to be in operation
        self.nodes = []
        self.state = State.Normal
        self.servers: List[str] = []

        # open the 'server.config' file in read-only mode
        config_file = open("server.config", "r")

        for line in config_file.readlines():
            line = line.rstrip()   # strip \r and \n characthers from the end of the string
            self.servers.append(line)

        self.number_of_connections: int = len(self.servers)

        cprint("Node address: tcp://{}".format(self.addr), 'magenta')

        self.connections: List[zerorpc.Client] = []

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
                self.connections.append(self)
            else:
                # timeout is the time in seconds the rpc calls wait before throwing an exception
                client = zerorpc.Client(timeout=1.5)
                client.connect("tcp://" + server)
                self.connections.append(client)

    # ------------------------------------------------------------------------------------------------------------------

    # DONE
    def check_network(self):
        """
        The main loop of the Node, where connection to the coordinator is periodically checked
        And based on the response a possible election is hold.
        STEPS:
            1. If the node is the coordinator it has no one to check, and therefore should do nothing.
               NOTE in a more realistic/pragmatic implementation, the coordinator would have to coordinate
               and delegate work to the other nodes in the network, but in this implementation we are only inter-
               ested in demonstrating how the election process work using the Bully Election Algorithm.

               If the node is not the coordinator, then it should send a request to the coordinator, to check
               if it is OK i.e. that it is still runnning and responding.

            2. If no response is given to the OK request, we know that the coordinator is no longer available,
               and we can start an election.
               Since we are using rpc calls to communicate between nodes the only way for a node not active in
               the network to communicate that it is not OK, is for the rpc request to timeout, and thereby
               trowing an exception, which we can except and use.
        """
        while True:
            # halt execution for 2 seconds
            gevent.sleep(2)
            print("waking up")
            print("state is {}".format(self.state))
            # To simulate the coordinator actually doing something, we let it check the state
            # of all other nodes in the network.
            if self.state is State.Normal and self.coordinator == self.idx:
                for (idx, server) in enumerate(self.servers):
                    if idx != self.idx:
                        try:
                            print("Coordinator checking node: {}".format(server))
                            answer: bool = self.connections[idx].OK()

                        except zerorpc.TimeoutExpired:
                            cprint("{} Timeout!".format(server), 'red')
                            getLineInfo()
                            continue

                        if not answer:
                            self.election()
                            return

            # If the node is not the coordinator it should only check if the coordinator is still up,
            # and start an election if it is not.
            # TODO
            elif self.state is State.Normal and self.coordinator != self.idx:
                try:
                    print("Check coordinator is OK")
                    answer: bool = self.connections[self.coordinator].OK()
                    print("{} : OK = {}".format(self.coordinator, answer))
                except zerorpc.TimeoutExpired:
                    print("{} Coordinator is down! starting election".format(
                        self.coordinator))
                    getLineInfo()
                    self.timeout()

    # ------------------------------------------------------------------------------------------------------------------

    # DONE
    def COORDINATOR(self, coordinator_id: int) -> None:
        """
        rpc call used to inform all the other nodes in the network, that a new coordinator has been chosen
        and that all other nodes, should update their state about which node is the coordinator.
        """
        print("A new coordinator has been found.")
        cprint("The coordinator is {}".format(coordinator_id), 'cyan')
        # if it was halted by the coordinator, and its current state is election
        if self.halter == coordinator_id and self.state is State.Election:

            # if self.state is State.Election:
            self.coordinator = coordinator_id
            self.state = State.Reorganization

    # ------------------------------------------------------------------------------------------------------------------

    # DONE
    def election(self):
        """
        Election a new coordinator node of the network using the Bully Election Algorithm
        STEPS:
            1. Node k sends an ELECTION message to all processes with higher identifiers:
               Node_k+1, Node_k+2, ..., Node_n-1.
            2. If no one responds, Node_k wins the election and becomes the coordinator.
            3. If one of the higher-ups answers, it takes over and Node_k job is done.
        """

        cprint("Starting election!!", 'blue')
        cprint("Check the states of higher priority nodes:", 'blue')

        # Only send an 'are_you_OK' to nodes with a higher index that self, because
        # it is unnessesary to ask the ones lower
        count: int = 0
        next_electioners: List[int] = []

        for (idx, server) in enumerate(self.servers[self.idx + 1:]):
            try:
                # TODO this can be optimized. we can make a temporary list, and append the indexes which respond
                # so we potentially can lower the amount of calls we have to do to higher up Nodes, since some of the
                # nodes in current < other < coordinator might also be down
                # response: bool = self.connections[self.idx + 1 + idx].OK()
                self.connections[self.idx + 1 + idx].OK()
                if self.check_servers_greenlet is None:
                    self.coordinator = self.idx + 1 + idx  # TODO hmm
                    self.state = State.Normal
                    self.check_servers_greenlet = self.pool.spawn(self.check_network())
                return
                next_electioners.append(self.idx + 1 + idx)
                count += 1
                # TODO we need to do more with this information
            except zerorpc.TimeoutExpired:
                cprint("{} Timeout!".format(server), 'red')
                getLineInfo()

        cprint("Halt all lower priority nodes including this node:", 'yellow')
        self.HALT(self.idx)
        self.state = State.Election
        self.halter = self.idx
        self.nodes = []

        for (idx, server) in enumerate(self.servers[self.idx::-1]):
            try:
                self.connections[idx].HALT(self.idx)
            except zerorpc.TimeoutExpired:
                cprint("{} Timeout!".format(server), 'red')
                getLineInfo()
                continue
            self.nodes.append(self.connections[idx])

        # reached 'election point', inform nodes of new coordinator
        cprint("Inform nodes of new coordinator:", 'green')
        self.coordinator = self.idx
        self.state = State.Reorganization
        for i in self.nodes:
            try:
                self.connections[idx].COORDINATOR(self.idx)
            except zerorpc.TimeoutExpired:
                cprint("Timeout! Election will be restarted", 'red')
                getLineInfo()
                # FIXME we dont need to know about other nodes being alive, only the coordinator
                self.election()
                return

        # Reorganization
        for node in self.nodes:
            try:
                node.READY(self.idx)
            except zerorpc.TimeoutExpired:
                cprint("Timeout!", 'red')
                self.election()
                return

        self.state = State.Normal
        self.check_servers_greenlet = self.pool.spawn(self.check_network())


        # If no higher nodes have responded then we know that this node should be the coordinator
        # if count == 0:
        #     self.coordinator = self.idx

        #     for (idx, server) in enumerate(self.servers):
        #         try:
        #             self.connections[idx].COORDINATOR(self.coordinator)
        #         except zerorpc.TimeoutExpired:
        #             cprint("{} Timeout!".format(server), 'red')
        #             getLineInfo()

        # else:
        #     # TODO the optimization can be used here
        #     for (idx, server) in enumerate(self.servers[self.idx + 1:]):
        #         try:
        #             self.connections[self.idx + 1 + idx].election()
        #         except zerorpc.TimeoutExpired:
        #             cprint("{} Timeout!".format(server), 'red')
        #             getLineInfo()

        # # Small optimization. When one node has discovered that the coordinator is not responding
        # # it will halt all nodes lower than itself, since if they were to start an election
        # # it would not change who in the end would be elected as coordinator.
        # # print("halt all lower priority nodes including this node:")
        # # self.halt(self.idx)
        # # self.state = State.Election
        # # # self.halt = self.idx
        # # self.nodes = []

        # # FIXME what is the range syntax, and why dont we use a counter variable, to keep track of
        # # whether we can say if we are coordinator or not???
        # for (idx, server) in enumerate(self.servers[self.idx::-1]):
        #     try:
        #         self.connections[idx].HALT(int(idx))
        #     except zerorpc.TimeoutExpired:
        #         cprint("{} Timeout!".format(server), 'red')
        #         getLineInfo()
        #         continue
        #     # self.nodes.append(self.connections[idx])
        #     self.nodes.append(idx)

    # ------------------------------------------------------------------------------------------------------------------
    # TODO WHAT DOES THIS DO???
    # DONE
    def HALT(self, halter: int) -> None:
        """
        Inform the node to halt itself
        """
        self.state = State.Election
        self.halter = halter

    # ------------------------------------------------------------------------------------------------------------------

    # DONE
    def initialize(self) -> None:
        """
        When a node is initialized i.e. started it does not know who the coordinator
        in the network is, and whether or not it should be the coordinator.
        So it should hold an election to figure this out
        """
        cprint("Initializing node...", 'green')
        self.pool = gevent.pool.Group()
        self.recovery_greenlet = self.pool.spawn(self.recovery)

    # ------------------------------------------------------------------------------------------------------------------

    # DONE
    def NORMAL(self) -> bool:
        """
        Let another node query the state of this node
        """
        if self.state is State.Normal:
            return True
        else:
            return False

    # ------------------------------------------------------------------------------------------------------------------

    # DONE
    def OK(self) -> bool:
        """
        Method invoked through rpc to determine if the Node is online.
        If the Node being requested is not alive, then the 'communication' of this
        state is done through a try-except block, where the exception would mean
        that the node is not alive/not responding.
        """
        cprint("[{}] is OK".format(self.addr), 'green')
        return True

    # ------------------------------------------------------------------------------------------------------------------
    # TODO WHAT DOES THIS DO ????
    # DONE
    def READY(self, id) -> None:
        """
        After the topology of the network has been changed, the coordinator will inform all nodes in
        the network, to resume normal behaveiour.
        """
        cprint("Call ready", 'yellow')
        if self.coordinator == id and self.state is State.Reorganization:
            self.state = State.Normal

    # ------------------------------------------------------------------------------------------------------------------

    # DONE
    def recovery(self) -> None:
        """
        Recover from breakdown
        """
        self.halter = -1
        self.election()

    # ------------------------------------------------------------------------------------------------------------------

    # DONE
    def timeout(self) -> None:
        """
        """
        if self.state is State.Normal or self.state is State.Reorganization:
            try:
                self.connections[self.coordinator].OK()
            except zerorpc.TimeoutExpired:
                cprint("{} Timeout!".format(
                    self.servers[self.coordinator]), 'red')
                getLineInfo()
                self.election()
        else:
            self.election()

    # ------------------------------------------------------------------------------------------------------------------


def main() -> None:
    """
    Initialize the node and start the xml-rpc server.
    """
    if len(sys.argv) != 2:
        print("No port was specified - python bully.py <port> e.g. '9000")
        sys.exit(1)

    addr: str = sys.argv[1]
    node = Node(addr)
    server = zerorpc.Server(node)
    server.bind("tcp://" + addr)
    cprint("Starting node at port! [{}] ".format(addr), 'yellow')

    node.initialize()
    server.run()


if __name__ == '__main__':
    main()
