import zmq
import time
import parse # TODO
import sys
import threading
from threading import Thread
from termcolor import cprint

import re # regular expressions
from typing import Any, Dict, List, Tuple, Optional
import inspect # debug information
from enum import Enum, unique

from pickle import dump, loads


def get_line_info() -> None:
    """
    Helper function for debug purposes.
    """
    print(inspect.stack()[1][1], ":", inspect.stack()[1][2], ":", inspect.stack()[1][3])


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
        coordinator_ip:   Optional[str]
        coordinator_port: Optional[int]
        coordinator_id:   Optional[int]

        def __init__(self, coordinator_ip: str=None, coordinator_port: int=None, coordinator_id: int=None):
            self.coordinator_ip   = coordinator_ip
            self.coordinator_port = coordinator_port
            self.coordinator_id   = coordinator_id

        def __str__(self) -> str:
            return "coordinator {} {} {}".format(self.coordinator_ip, self.coordinator_port, self.coordinator_id)

        def update(self, host_ip: str, server_port: int, network_id: int) -> None:
            """
            Updates self information about which node is the coordinator in the network.
            args:
                @host_ip: str  --
                @server_port: int --
                @network_id: int  --
            """
            self.coordinator_ip   = host_ip
            self.coordinator_port = server_port
            self.coordinator_id   = network_id

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
    maxID: int
    network_id: int
    number_of_connections: int
    host_ip: str
    process_server_port: int
    process_client_port: int
    # TODO change to proper type
    nodes: List[Info]



    def __init__(self, host_ip: str, client_port: int, server_port: int, network_id: int) -> None:
        """
        Constructor method.
        args:
            @host_ip: str --
            @server_port: int --
            @client_port: int --
            @network_id: int --
        """
        self.host_ip  = host_ip
        self.client_port = client_port
        self.server_port = server_port
        self.network_id  = network_id

        self.coordinator = self.Coordinator()

        self.maxID = 0

        self.nodes = []
        self.number_of_nodes: int = 0
        network_config = open("network.config", 'r')

        for line in network_config.readlines():
            line = line.rstrip()
            # TODO
            host_ip, server_port, publisher_port, id = line.split()
            line = parse.parse('{} {} {} {}', line)

            self.maxID = max(self.maxID, int(line[3]))
            self.nodes.append(self.Info(
                ip=line[0],
                client_port=int(line[1]),
                server_port=int(line[2]),
                id=int(line[3])
                ))

            self.number_of_nodes += 1

    # ------------------------------------------------------------------------------------------------------------------
    def connect_to_network(self) -> None:
        """
        Set the subscriber socket of the node, to connect/listen to all the publisher sockets
        on the other nodes in the network.
        """
        for node in self.nodes:
            # TODO this is a bit ambiguous with the variable naming
            if node.id != self.network_id:
                self.subscriber_socket.connect(f"tcp://{node.ip}:{node.server_port}")
                # self.subscriber_socket.connect("tcp://{}:{}".format(node.ip, node.server_port))


    # ------------------------------------------------------------------------------------------------------------------
    def connect_to_higher_ids(self):
        """
        Establish connection to all nodes with higher id that self, in the network, since self should
        only contact them when an election is started by self.
        """
        for node in self.nodes:
            if node.id > self.network_id:
                # TODO is it really node.client_port ????
                self.client_socket.connect(f"tcp://{node.ip}:{node.client_port}")
                # self.client_socket.connect("tcp://{}:{}".format(node.ip, node.client_port))

    # ------------------------------------------------------------------------------------------------------------------
    def declare_coordinator(self, msg_count: int) -> None:
        """
        """
        cprint(f"[{self.host_ip}:{self.server_port}] is the new coordinator", 'green')
        # cprint("[{}:{}] is the new coordinator.".format(self.host_ip, self.server_port), 'cyan')
        self.coordinator.update(self.host_ip, self.server_port, self.network_id)

        #coordinator_publisher_thread: Thread = threading.Thread(target=self.check_network, args=["COORDINATOR"])
        coordinator_publisher_thread: Thread = threading.Thread(target=self.check_network, args=["COORDINATOR"])
        coordinator_publisher_thread.start()

    # ------------------------------------------------------------------------------------------------------------------
    def disconnect(self) -> None:
        """
        When a node is shutdown i.e. when Ctrl+c is pressed on the keyboard, then this method is called
        in an except block, which ensures that the node 'gently' disconnects from its connection
        to the other nodes in the network.
        """
        for node in self.nodes:
            # self.client_socket.disconnect("tcp://{}:{}".format(node.ip, node.server_port))
            # self.client_socket.disconnect("tcp://{}:{}".format(node.ip, node.client_port))
            self.client_socket.disconnect(f"tcp://{node.ip}:{node.client_port}")

    # ------------------------------------------------------------------------------------------------------------------
    def establish_connection(self, TIMEOUT: int) -> None:
        """
        Set up the zeromq runtime context.
        Create a zmq reply socket, for the server socket, and a zmq request socket, for the client socket
        args:
            @TIMEOUT: int -- The time (in milliseconds) the client socket, should wait before trowing
                             an exception to indicate, that the node being requested is down.
        """
        self.context = zmq.Context()

        # create a request socket for the client
        self.client_socket = self.context.socket(zmq.REQ)
        # set the timeout duration to TIMEOUT
        self.client_socket.setsockopt(zmq.RCVTIMEO, TIMEOUT)

        # create a reply socket for the server port
        self.server_socket = self.context.socket(zmq.REP)
        self.server_socket.bind(f"tcp://{self.host_ip}:{self.server_port}")
        # self.server_socket.bind("tcp://{}:{}".format(self.host_ip, self.server_port))

        self.connect_to_higher_ids()

        self.middleware_context = zmq.Context()

        self.publisher_socket = self.middleware_context.socket(zmq.PUB)
        self.publisher_socket.bind(f"tcp://{self.host_ip}:{self.client_port}")
        # self.publisher_socket.bind("tcp://{}:{}".format(self.host_ip, self.client_port))

        # list of subsribers
        self.subscribers = []

        self.subscriber_socket = self.middleware_context.socket(zmq.SUB)
        # set the timeout duration to TIMEOUT
        self.subscriber_socket.setsockopt(zmq.RCVTIMEO, TIMEOUT)
        # topic subscribtion filter
        # self.subscriber_socket.setsockopt(zmq.SUBSCRIBE, "")
        self.connect_to_network()
        self.subscriber_socket.subscribe("")

        get_line_info()
        # TODO why subscribe("")
        # By subscribing to "" (an empty subscription), the subscriber will get everything
        # published on the topic/port (every single topic from publisher)

        # assert
        # self.context.destroy()


    # ------------------------------------------------------------------------------------------------------------------
    def is_coordinator(self) -> bool:
        """
        Return true, if the node instance is the coordinator in the network, and false if not.
        """
        return self.coordinator.coordinator_id == self.network_id

    # ------------------------------------------------------------------------------------------------------------------
    # TODO maybe not the best name
    # FIXME could be called check instead
    # TODO use an enum type instead of a plain string
    def check_network(self, state: str) -> None:
        """
        """

        #if state is self.State.Normal:
        if state == "NORMAL":
            while True:
                try:
                    coordinator_msg = self.subscriber_socket.recv_string()
                    # request = parse.parse("UP {} {} {}", coordinator_msg)
                    _, host_ip, client_port, network_id = coordinator_msg.split()
                    if int(request[2]) > self.network_id:
                        cprint("coordinator {} is UP".format(coordinator_msg), 'green')
                        self.coordinator.update(str(request[0]), int(request[1]), int(request[2]))
                # except:
                except zmq.ZMQError as e:
                    if self.coordinator.coordinator_id != self.network_id:
                        cprint("Coordinator is down, an election will be started\n", 'red')
                        self.coordinator.coordinator_id = None

        #elif state is self.State.Coordinator:
        elif state == "COORDINATOR":
            while self.coordinator.coordinator_id == self.network_id:
                # TODO are we sure about the self.client_port
                # self.publisher_socket.send_string(b"UP {} {} {} {}".)
                self.publisher_socket.send_string(f"UP {self.host_ip} {self.client_port} {self.network_id}")
                # self.publisher_socket.send_string("UP {} {} {}".format(self.host_ip, self.client_port, self.network_id))
                get_line_info()
                time.sleep(1)




        # if process == State.Coordinator
        # if process == "COORDINATOR":
        #     while self.coordinator.coordinator_id == self.network_id:
        #         # TODO are we sure about the self.client_port
        #         self.publisher_socket.send_string("UP {} {} {}".format(self.host_ip, self.client_port, self.network_id))
        #         time.sleep(1)
        # else:
        #     while True:
        #         try:
        #             coordinator_msg = self.subscriber_socket.recv_string()
        #             request = parse.parse("UP {} {} {}", coordinator_msg)
        #             if int(request[2]) > self.network_id:
        #                 cprint("coordinator {} is UP".format(coordinator_msg), 'green')
        #                 self.coordinator.update(str(request[0]), int(request[1]), int(request[2]))
        #         except:
        #             if self.coordinator.coordinator_id != self.network_id:
        #                 cprint("Coordinator is down, an election will be started\n", 'red')
        #                 self.coordinator.coordinator_id = None

    # ------------------------------------------------------------------------------------------------------------------
    def run(self) -> None:
        """
        Spin up the node
        """
        self.establish_connection(2000)

        # TODO do we need the args=[]
        publisher_thread: Thread = threading.Thread(target=self.check_network, args=["NORMAL"])
        publisher_thread.start()

        server_thread: Thread = threading.Thread(target=self.run_server, args=[])
        server_thread.start()

        client_thread: Thread = threading.Thread(target=self.run_client, args=[])
        client_thread.start()

    # ------------------------------------------------------------------------------------------------------------------
    def run_server(self) -> None:
        """
        """
        while True:
            # Wait for next request from client
            request: str = self.server_socket.recv_string()
            # TODO this is where we have to add the logic
            if request.startswith("ELECTION"):
                self.server_socket.send("OK")

    # ------------------------------------------------------------------------------------------------------------------
    def run_client(self) -> None:
        """
        """
        while True:
            if self.coordinator.coordinator_id is None:
                try:
                    # If the node has the highest ID possible in the network (given by the network.config file)
                    # then it knows it is the coordinator, given the 'bully rule'
                    if self.network_id == self.maxID:
                        self.declare_coordinator(2)
                    else:
                        self.client_socket.send_string("ELECTION")
                        request: str = self.client_socket.recv_string()
                # If the recv_string() times out, then we know self is the highest node in the election
                # and it becomes the coordinator
                except:
                    self.declare_coordinator(2)

# ----------------------------------------------------------------------------------------------------------------------

# TODO
def check_input(input: Tuple[str, int, int, int]) -> bool:
    # TODO
    # pattern = re.compile('')
    return True

def main() -> None:

    if len(sys.argv) != 5:
        cprint("WRONG NUMBER OF ARGUMENTS", 'red')
        cprint("{} were given, but 4 is needed".format(len(sys.argv) - 1), 'red')
        print("The first argument should be the ip address e.g. 127.0.0.1")
        print("The second- and third argument should be the client- and server port respectively e.g. 9000 9001")
        print("The fourth argument should be the unique unsigned integer id of the node being started e.g 2")
        cprint("NOTE all four arguments MUST match one of the lines in the file network.config", 'red')
        sys.exit(1)

    host_ip: str = str(sys.argv[1])
    client_port: int = int(sys.argv[2])
    server_port: int = int(sys.argv[3])
    network_id: int  = int(sys.argv[4])

    if not check_input((host_ip, client_port, server_port, network_id)):
        cprint("INVALID INPUT", 'red')
        # TODO
        sys.exit(1)

    node: Node = Node(host_ip, client_port, server_port, network_id)
    try:
        node.run()
    # when hitting Ctrl+C
    # FIXME does not enter
    except KeyboardInterrupt:
        node.disconnect()

if __name__ == "__main__":
    main()
