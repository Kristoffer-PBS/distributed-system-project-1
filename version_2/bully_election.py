from enum import Enum, unique
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import xmlrpc.server
import xmlrpc.client
import sys
import time
import select
import socket
import pickle
import random

from typing import List
from typing import Optional
from typing import Union

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


class Node():
    """
    Node class representing a single node in the network.
        data/state:
            @addr: str -- The socket identifier e.g. '127.0.0.1:9000'
            @connections: list[xmlrpc.client]
            @state: State -- The different behaviour a node can be in
            @number_of_connnections: int  -- the number of connections to check

        methods:
            __init__(addr: str, config_file: Optional<str>)
            check_coordinator() ->
            election() -> None
            new_coordinator(coordinator_id: int) -> None --
            OK() -> bool

        exceptions:
            None

    """

    def __init__(self, addr: str, config_file='server_config'):
        self.addr: str = addr
        self.coordinator: int = 0
        # TODO delete field
        # description of the task
        self.description = None
        # the node who recently made this node halt execution
        self.halt = -1
        # list of nodes which this node belieces to be in operation
        self.nodes = []
        self.state = State.Normal
        self.servers = []

        # open the 'server.config' file in read-only mode
        config_file = open("server.config", "r")

        for line in config_file.readlines():
            line = line.rstrip()   # strip \r and \n characthers from the end of the string
            self.servers.append(line)

        print("My address: {}".format(self.addr))
        print("Server list: {}".format(str(self.servers)))

        self.number_of_connections: int = len(self.servers)

        # TODO change type
        self.connections: List[ServerProxy] = []

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
                # create client
                client = xmlrpc.client.ServerProxy("http://".join(server))
                self.connections.append(client)

        # New node need to figure out who is the coordinator
        self.initialize()
    # ------------------------------------------------------------------------------------------------------------------

    def OK(self) -> bool:
        """
        Method invoked through rpc to determine if the Node is online.
        If the Node being requested is not alive, then the 'communication' of this
        state is done through a try-except block, where the exception would mean
        that the node is not alive/not responding.
        """
        return True

    # ------------------------------------------------------------------------------------------------------------------
    def are_you_normal(self) -> bool:
        """
        Let another node query the state of this node
        """
        if self.state is State.Normal:
            return True
        else:
            return False

    # ------------------------------------------------------------------------------------------------------------------
    # TODO WHAT DOES THIS DO???
    def halt(self, halter: int) -> None:
        """
        Inform the node to halt itself
        """
        self.state = State.Election
        self.halt = halter

    # ------------------------------------------------------------------------------------------------------------------
    def new_coordinator(self, coordinator_id: int) -> None:
        """
        rpc call used to inform all the other nodes in the network, that a new coordinator has been chosen
        and that all other nodes, should update their state about which node is the coordinator.
        """
        print("A new coordinator has been found.")
        print("The coordinator is".format(coordinator_id))
        if self.state is State.Election:
            self.coordinator = coordinator_id
            self.state = State.Reorganization

        # TODO what does halt do
        # if self.halt == j and self.state is State.Election:
        #     self.coordinator = j
        #     self.state = State.Reorganization

    # ------------------------------------------------------------------------------------------------------------------
    # TODO WHAT DOES THIS DO ????
    def ready(self, j, x=None):
        print("Call ready")
        if self.coordinator == j and self.state is State.Reorganization:
            self.description = x
            self.state = State.Normal
    # ------------------------------------------------------------------------------------------------------------------
    # Juicy part!

    def election(self):
        """
        Election a new coordinator node of the network using the Bully Election Algorithm
        STEPS:
            1. Node k sends an ELECTION message to all processes with higher identifiers:
               Node_k+1, Node_k+2, ..., Node_n-1.
            2. If no one responds, Node_k wins the election and becomes the coordinator.
            3. If one of the higher-ups answers, it takes over and Node_k job is done.
        """

        print("Check the states of higher priority nodes:")

        # Only send an 'are_you_OK' to nodes with a higher index that self, because
        # it is unnessesary to ask the ones lower
        count: int = 0
        next_electioners: List[int] = []
        for (idx, server) in enumerate(self.servers[self.idx + 1:]):
            try:
                # TODO this can be optimized. we can make a temporary list, and append the indexes which respond
                # so we potentially can lower the amount of calls we have to do to higher up Nodes, since some of the
                # nodes in current < other < coordinator might also be down
                self.connections[self.idx + 1 + idx].OK()
                next_electioners.append(self.idx + 1 + idx)
                count += 1
                # TODO we need to do more with this information
                # self.state
            except ConnectionRefusedError as err:
                print("{} Timeout!".format(server))

        # If no higher nodes have responded then we know that this node should be the coordinator
        if count == 0:
            self.coordinator = self.idx

            for (idx, server) in enumerate(servers[self.number_of_connections]):
                try:
                    self.connections[idx].new_coordinator(self.idx)
                except ConnectionRefusedError:
                    print("{} Timeout!".format(server))

        else:
            # TODO the optimization can be used here
            for (idx, server) in enumerate(servers[self.idx + 1:]):
                try:
                    self.connections[self.idx + 1 + idx].election()
                except ConnectionRefusedError:
                    print("{} Timeout!".format(server))

            # try:
            #     self.connections[self.idx + 1 +
            #                      idx].are_you_there()  # rpc call
            #     if self.check_servers_greenlet is None:
            #         self.coordinator = self.idx + 1 + idx
            #         self.state = State.Normal
            #         self.check_servers_greenlet = self.pool.spawn(self.check())
            #     return
            # except zerorpc.TimeoutExpired:
            #     print("{} Timeout!".format(server))

        # Small optimization. When one node has discovered that the coordinator is not responding
        # it will halt all nodes lower than itself, since if they were to start an election
        # it would not change who in the end would be elected as coordinator.
        print("halt all lower priority nodes including this node:")
        self.halt(self.idx)
        self.state = State.Election
        self.halt = self.idx
        self.nodes = []

        # FIXME what is the range syntax, and why dont we use a counter variable, to keep track of
        # whether we can say if we are coordinator or not???
        for (idx, server) in enumerate(self.servers[self.idx::-1]):
            try:
                self.connections[idx].halt[self.idx]
            except ConnectionRefusedError:
                print("{}, Timeout!".format(server))
                continue
            self.nodes.append(self.connections[idx])

            # except zerorpc.TimeoutExpired:
            #     print("{} Timeout".format(server))
            #     continue
            # self.state_vetor.nodes.append(self.conntections[idx])

        # reached 'election point', inform nodes of new coordinator
        print("Inform nodes of new coordinator:")
        self.coordinator = self.idx
        self.state = State.Reorganization
        for node in self.nodes:
            try:
                node.new_coordinator(self.idx)
            except ConnectionRefusedError:
                print("Timeout! Election will be restarted")
                # FIXME we dont need to know about other nodes being alive, only the coordinator
                self.election()
                return

            # except zerorpc.TimeoutExpired:
            #     print("Timeout! Election will be restarted")
            #     self.election()
            #     return

        # Reorganization
        for node in self.nodes:
            try:
                node.ready(self.idx, self.description)
            except ConnectionRefusedError:
                print("Timeout!")
                self.election()
                return
            # except zerorpc.TimeoutExpired:
            #     print("Timeout!")
            #     self.election()
            #     return

        # FIXME i dont think this is relevant for us
        self.state = State.Normal
    # ------------------------------------------------------------------------------------------------------------------

    def recovery(self):
        self.halt = -1
        self.election()
    # ------------------------------------------------------------------------------------------------------------------
    # TODO should have a different name

    def check(self):
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
            time.sleep(2)
            if self.state is State.Normal:
                try:
                    print("Check coordinator is OK")
                    answer: bool = self.connections[self.coordinator].OK()
                    print("{} : OK = {}".format(self.coordinator, answer))
                except ConnectionRefusedError:
                    print("{} Coordinator is down! starting election".format(
                        self.coordinator))
                    self.election()

            # If node is the coordinator
            # if self.state is State.Normal and self.coordinator == self.idx:
            #     for (idx, server) in enumerate(self.servers):
            #         if idx != self.idx:
            #             try:
            #                 # rpc call
            #                 answer: bool = self.connections[idx].OK()
            #                 print("{} : OK = {}".format(server, answer))
            #             except ConnectionRefusedError:
            #                 print("{} Timeout!".format(server))
            #                 continue
            #             # except zerorpc.TimeoutExpired:
            #             #     print("{} Timeout!".format(server))
            #             #     continue

            #             # if we do not receive a response we start an election
            #             # but why should the coordinator start an election
            #             # if it registers a lower node is not responding ???
            #             # TODO
            #             if not answer:
            #                 self.election()
            #                 return

            # # if node is not the coordinator
            # # FIXME why do we say elif, a node can either be the coordinator or not, so by
            # # simply checking if it is a coordnator above, we can conclude that it is not otherwise.
            # elif self.state is State.Normal and self.coordinator != self.idx:
            #     print("check coordinator's state")
            #     try:
            #         resul = self.conntections[self.coordinator].are_you_there(
            #         )
            #         print("{} : are_you_there = {}".format(
            #             self.servers[self.coordinator], result))
            #     # The exception is used to deduce that the coordinator is down, and
            #     # that we then have to hold an election to find a new coordinator
            #     except zerorpc.TimeoutExpired:
            #         print("coordinator down, raise election.")
            #         self.timeout()

    # ------------------------------------------------------------------------------------------------------------------
    def timeout(self):
        """
        """
        # FIXME how is the state related to the allowed functionality
        if self.state is State.Normal or self.state is State.Reorganization:
            try:
                self.connections[self.coordinator].are_you_there()
            except zerorpc.TimeoutExpired:
                print("{} Timeout!".format(
                    self.servers[self.coordinator]))
                self.election()
        else:
            self.election()
    # ------------------------------------------------------------------------------------------------------------------

    def initialize(self) -> None:
        """
        When a node is initialized i.e. started it does not know who the coordinator
        in the network is, and whether or not it should be the coordinator.
        So it should hold an election to figure this out
        """
        self.election()

    # def start(self):
    #     self.pool = gevent.pool.Group()
    #     self.recovery_greenlet = self.pool.spawn(self.recovery)
    # ------------------------------------------------------------------------------------------------------------------


def main() -> None:
    """
    Initialize the node and start the xml-rpc server.
    """
    if len(sys.argv) != 2:
        print("No address was specified - python bully.py <port> e.g. '127.0.0.1:9000")
        sys.exit(1)

    addr: str = sys.argv[1]
    node: Node = Node(addr)
    port: str = addr.split(':')

    server = zerorpc.Server(node)
    tcp: str = "tcp://" + addr
    server.bind("tcp://" + addr)
    # server.bind(tcp)
    node.start()

    with SimpleXMLRPCServer(('localhost', 8000)) as server:
        server.register_introspection_functions()

    server.register_instance(Node)

    print("[{}] Starting node at port!".format(addr))
    print("Serving XML-RPC in local host port 8000")
    try:
        # Run the server's main loop
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, exiting.")
        sys.exit(0)


if __name__ == '__main__':
    main()
