import zmq
import time
import parse # TODO
import sys
import threading
from threading import Thread
from termcolor import cprint

from typing import Any, Dict, List, Tuple

from enum import Enum, unique



class Node:
    class Info:
        """
        Nested subclass of the Node class, used to create better structure, and avoid the anti-pattern
        of not using structured types to relate related data.
        """
        ip: str
        client_port: int
        server_port: int
        id: int

        def __init__(self, ip: str, client_port: int, server_port: int, id: int) -> None:
            self.id = id
            self.ip = ip
            self.client_port = client_port
            self.server_port = server_port
    # ------------------------------------------------------------------------------------------------------------------

    class Coordinator:
        """
        Collect information about the coordinator into a struct, to relate data.
        """
        coordinator_ip: str
        coordinator_port: int
        coordinator_id: int

        def __init__(self):
            self.coordinator_ip = "d"
            self.coordinator_port = 2
            self.coordinator_id = 3

    # ------------------------------------------------------------------------------------------------------------------
    @unique
    class State(Enum):
        """
        Enumerated sub-type describing the behaveioural state of the Node
        """
        Coordinator = 1
        Normal = 2
        # TODO use this state and check for it to implement the election logic more explicitly
        Halt = 3
        Election = 4
        Down = 5

        def __str__(self) -> str:
            return "in state: {}".format(self.name)
    # ------------------------------------------------------------------------------------------------------------------

    """
        methods:
            is_coordinator() -> Bool:
            run() -> None:
            run_client() -> None:
            run_server() -> None:
    """
    coordinator: Coordinator
    coordinator_id: int
    maxID: int
    network_id: int
    number_of_connections: int
    process_ip: str
    process_server_port: int
    process_client_port: int
    # TODO change to proper type
    nodes: List[Info]



    def __init__(self, process_ip: str, server_port: int, client_port: int, network_id: int) -> None:
        """
        Constructor method.
        args:
            @process_ip: str --
            @server_port: int --
            @client_port: int --
            @network_id: int --
        """
        # TODO
        self.coordinator = self.Coordinator()
        self.process_ip = process_ip
        self.server_port = server_port
        self.client_port = client_port
        self.network_id = network_id
        self.coordinator_id = -1

        config_file = open("nodes.config", 'r')
        input = config_file.readlines()
        # TODO i would rather that the number of nodes is computed, rather than specified in the config file
        number_of_nodes = int(input[0])

        self.maxID = 0
        self.coordinator_id: int = -1

        self.nodes = []

        for i in range(1, number_of_nodes + 1):
            line = parse.parse('{} {} {} {}', input[i])
            self.maxID = max(self.maxID, int(line[3]))
            self.nodes.append(self.Info(
                ip=line[0],
                server_port=line[1],
                client_port=line[2],
                id=int(line[3])
                ))



    # ------------------------------------------------------------------------------------------------------------------
    def connect_to_network(self) -> None:
        """
        Set the subscriber socket of the node, to connect/listen to all the publisher sockets
        on the other nodes in the network.
        """
        for node in self.nodes:
            # TODO this is a bit ambiguous with the variable naming
            if node.id != self.network_id:
                self.subscriber_socket.connect("tcp://{}:{}".format(node.ip, node.server_port))


    # ------------------------------------------------------------------------------------------------------------------
    def connect_to_higher_ids(self):
        """
        Establish connection to all nodes with higher id that self, in the network, since self should
        only contact them when an election is started by self.
        """
        for node in self.nodes:
            if node.id > self.network_id:
                # TODO is it really node.client_port ????
                self.client_socket.connect("tcp://{}:{}".format(node.ip, node.client_port))

    # ------------------------------------------------------------------------------------------------------------------
    # def clock_tick(self, process=None) -> None:
    #     """
    #     main loop
    #     """
    #     if process is State.Coordinator:
    #         while int(self.coordinator_id) == int(self.network_id):
    #             self.clock_socket.send_string("alive {} {} {}".format(self.process_ip, self.process_server_port, self.network_id))
    #             time.sleep(1)
    #     else:
    #         while True:
    #             try:
    #                 coordinator_clock_tick = self.clock_socket2.recv_string()
    #                 request = parse.parse("alive {} {} {}".format(coordinator_clock_tick))
    #                 if (int(request[0] > self.network_id)):
    #                     cprint("coordinator {}".format(coordinator_clock_tick), 'green')
    #                     self.update_coordinator(str(request[0]), str(request[1]), int(request[2]))
    #             except:
    #                 if not self.is_coordinator():
    #                     cprint("Coordinator is down, starting election\n", 'red')
    #                     self.coordinator_id = -1

    # ------------------------------------------------------------------------------------------------------------------
    def declare_coordinator(self) -> None:
        """
        """
        cprint("[{}:{}] is the new coordinator.".format(self.process_ip, self.server_port), 'blue')
        self.update_coordinator(self.process_ip, self.server_port, self.network_id)
        # TODO change thread name
        coordinator_clock_thread: Thread = threading.Thread(target=self.publish, args=["COORDINATOR"])
        coordinator_clock_thread.start()

    # ------------------------------------------------------------------------------------------------------------------
    def disconnect(self) -> None:
        """
        When a node is shutdown i.e. when Ctrl+c is pressed on the keyboard, then this method is called
        in an except block, which ensures that the node 'gently' disconnects from its connection
        to the other nodes in the network.
        """
        for node in self.nodes:
            self.client_socket.disconnect("tcp://{}:{}".format(node.ip, node.server_port))

    # ------------------------------------------------------------------------------------------------------------------
    def establish_connection(self, TIMEOUT: int) -> None:
        """
        Set up the zeromq runtime context.
        Create a zmq reply socket, for the server socket, and a zmq request socket, for the client socket
        args:
            @TIMEOUT: int -- The time (in milliseconds) the client socket, should wait before trowing
                             an exception to indicate, that the node being requested is down.
        """
        self.context = zmq.Contex()

        # create a request socket for the client
        self.client_socket = self.context.socket(zmq.REQ)
        # set the timeout duration to TIMEOUT
        self.client_socket.setsocketopt(zmq.RECVTIMEO, TIMEOUT)

        # create a reply socket for the server port
        self.server_socket = self.context.socket(zmq.REP)
        self.server_socket.bind("tcp://{}:{}".format(self.process_ip, self.server_port))

        self.connect_to_higher_ids()

        self.middleware_context = zmq.Context()

        self.publisher_socket = self.middleware_context.socket(zmq.PUB)
        self.publisher_socket.bind("tcp://{}:{}".format(self.process_ip, self.client_port))

        self.subscriber_socket = self.middleware_context.socket(zmq.SUB)
        # set the timeout duration to TIMEOUT
        self.subscriber_socket.setsockopt(zmq.RCVTIMEO, TIMEOUT)

        self.connect_to_network()
        # TODO why subscribe("")
        self.subscriber_socket.subscribe("")


    # ------------------------------------------------------------------------------------------------------------------
    def is_coordinator(self) -> bool:
        """
        Return true, if the node instance is the coordinator in the network, and false if not.
        """
        return self.coordinator_id == self.network_id

    # ------------------------------------------------------------------------------------------------------------------
    # TODO maybe not the best name
    def publish(self, process=None) -> None:
        """
        """
        # if process == State.Coordinator
        if process == "COORDINATOR":
            while self.coordinator_id == self.network_id:
                # TODO are we sure about the self.client_port
                self.publisher_socket.send_string("UP {} {} {}".format(self.process_ip, self.client_port, self.network_id))
                time.sleep(1)
        else:
            while True:
                try:
                    coordinator_msg = self.subscriber_socket.recv_string()
                    request = parse.parse("UP {} {} {}", coordinator_msg)
                    if int(request[2]) > self.network_id:
                        cprint("coordinator {} is UP".format(coordinator_msg), 'green')
                        self.update_coordinator(str(request[0]), int(request[1]), int(request[2]))
                except:
                    if self.coordinator_id != self.network_id:
                        cprint("Coordinator is down, an election will be started\n", 'red')
                        self.coordinator_id = -1

    # ------------------------------------------------------------------------------------------------------------------
    def run(self) -> None:
        """
        Spin up the node
        """
        self.establish_connection(2000)


        # TODO do we need the args=[]
        publisher_thread: Thread = threading.Thread(target=self.publish, args=[])
        publisher_thread.start()

        server_thread: Thread = threading.Thread(target=self.run_server, args=[])
        server_thread.start()

        client_thread: Thread = threading.Thread(target=self.run_client, args=[])
        client_thread.start()

    # ------------------------------------------------------------------------------------------------------------------
    def run_server(self) -> None:
        while True:
            request: str = self.server_socket.recv_string()
            if request.startswith("ELECTION"):
                self.server_socket.send("OK")

    # ------------------------------------------------------------------------------------------------------------------
    def run_client(self) -> None:
        while True:
            if self.coordinator_id == -1:
                try:
                    if self.network_id == self.maxID:
                        self.declare_coordinator()
                    else:
                        self.client_socket.send_string("ELECTION")
                        request: str = self.client_socket.recv_string()
                except:
                    self.declare_coordinator()


    # ------------------------------------------------------------------------------------------------------------------
    def update_coordinator(self, process_ip: str, server_port: int, network_id: int) -> None:
        """
        Updates self information about which node is the coordinator in the network.
        args:
            @process_ip: str  --
            @server_port: int --
            @network_id: int  --
        """
        self.coordinator_ip   = process_ip
        self.coordinator_port = server_port
        self.coordinator_id   = network_id



# TODO
def check_input(input: Tuple[str, int, int, int]) -> bool:

    return True

# ----------------------------------------------------------------------------------------------------------------------

def main() -> None:

    if len(sys.argv) != 5:
        cprint("WRONG NUMBER OF ARGUMENTS", 'red')
        cprint("{} were given, but 4 is needed".format(len(sys.argv)), 'red')
        sys.exit(1)

    ip: str = str(sys.argv[1])
    server_port: int = int(sys.argv[2])
    client_port: int = int(sys.argv[3])
    network_id: int  = int(sys.argv[4])

    if not check_input((ip, server_port, client_port, network_id)):
        cprint("INVALID INPUT", 'red')
        # TODO
        sys.exit(1)



    node: Node = Node(ip, server_port, client_port, network_id)
    try:
        node.run()
    # when hitting Ctrl+C
    except KeyboardInterrupt:
        node.disconnect()

if __name__ == "__main__":
    main()