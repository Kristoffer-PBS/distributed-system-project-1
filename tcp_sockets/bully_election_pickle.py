import zmq
import time
import parse  # TODO
import sys
import threading
from threading import Thread
from termcolor import cprint

import re  # regular expressions
from typing import Any, Dict, List, Tuple, Optional
import inspect  # debug information
from enum import Enum, unique
import pickle
from pickle import dump, loads
import json

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
        host_ip:        str
        publisher_port: int
        server_port:    int
        network_id:     int

        def __init__(self, host_ip: str, publisher_port: int, server_port: int, network_id: int) -> None:
            self.host_ip = host_ip
            self.publisher_port = publisher_port
            self.server_port = server_port
            self.network_id = network_id

    # ------------------------------------------------------------------------------------------------------------------

    class Coordinator:
        """
        Collect information about the coordinator into a struct, to relate data.
        """
        coordinator_ip:   Optional[str]
        coordinator_port: Optional[int]
        coordinator_id:   Optional[int]

        def __init__(self, coordinator_ip: str = None, coordinator_port: int = None, coordinator_id: int = None):
            self.coordinator_ip = coordinator_ip
            self.coordinator_port = coordinator_port
            self.coordinator_id = coordinator_id

        def __str__(self) -> str:
            return f"coordinator {self.coordinator_ip} {self.coordinator_port} {self.coordinator_id}"

        def update(self, host_ip: str, server_port: int, network_id: int) -> None:
            """
            Updates self information about which node is the coordinator in the network.
            args:
                @host_ip: str     --
                @server_port: int --
                @network_id: int  --
            """
            self.coordinator_ip = host_ip
            self.coordinator_port = server_port
            self.coordinator_id = network_id

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
            return f"in state: {self.name}"
    # ------------------------------------------------------------------------------------------------------------------

    """
        methods:
            is_coordinator() -> Bool:
            run() -> None:
            run_client() -> None:
            run_server() -> None:
    """
    host_ip: str
    publisher_port: int
    server_port: int
    network_id: int
    number_of_connections: int
    coordinator: Coordinator
    # TODO change to proper type
    nodes: List[Info]

    def __init__(self, host_ip: str, publisher_port: int, server_port: int, network_id: int) -> None:
        """
        Constructor method.
        args:
            @host_ip: str --
            @server_port: int --
            @publisher_port: int --
            @network_id: int --
        """
        self.host_ip = host_ip
        self.publisher_port = publisher_port
        self.publisher_port = publisher_port
        self.server_port = server_port
        self.network_id = network_id

        self.coordinator = self.Coordinator()

        self.clients = []
        self.nodes = []
        self.number_of_nodes: int = 0

        # Use an with clause to automatically handle the relase of the file handle ressource when scope ends
        with open("network.config", 'r') as network_config:
            for line in network_config:
                line = line.strip()  # strip newline character \n
                # split the line by whitespace
                (host_ip, publisher_port, server_port, network_id) = line.split()
                # print(f"{host_ip}, {publisher_port}, {server_port}, {id}")
                self.nodes.append(self.Info(
                    host_ip=host_ip,
                    publisher_port=int(publisher_port),
                    server_port=int(server_port),
                    network_id=int(network_id)
                ))
                self.number_of_nodes += 1

        # cprint(f"maxid is {self.number_of_nodes}", 'magenta')

    # ------------------------------------------------------------------------------------------------------------------
    # TODO maybe not the best name
    # FIXME could be called check instead
    def check_network(self, state: str) -> None:
        """
        """

        # if state is self.State.Normal:
        if state == "NORMAL":
            while True:
                try:
                    coordinator_msg = self.subscriber_socket.recv_string()
                    # request = parse.parse("UP {} {} {}", coordinator_msg)
                    (_, host_ip, publisher_port, network_id) = coordinator_msg.split()
                    if int(network_id) > self.network_id:
                        cprint(f"Coordinator {host_ip}:{publisher_port} {network_id} is UP", 'green')
                        self.coordinator.update(host_ip, int(publisher_port), int(network_id))

                except:
                # except zmq.ZMQError as e:
                    if self.coordinator.coordinator_id != self.network_id:
                        cprint("Coordinator is down, an election will be started\n", 'red')
                        self.coordinator.coordinator_id = None

        # elif state is self.State.Coordinator:
        elif state == "COORDINATOR":
            while self.coordinator.coordinator_id == self.network_id:
                # TODO are we sure about the self.publisher_port
                # self.publisher_socket.send_string(b"UP {} {} {} {}".)

                msg: str = f"UP "
                self.publisher_socket.send_string(f"UP {self.host_ip} {self.publisher_port} {self.network_id}")
                cprint(f"I am the coordinator: {self.network_id}", 'yellow')
                time.sleep(2)

    # ------------------------------------------------------------------------------------------------------------------
    def declare_new_coordinator(self, msg_count: int) -> None:
        """
        """
        cprint(f"[{self.host_ip}:{self.server_port}] is the new coordinator", 'green')
        self.coordinator.update(self.host_ip, self.server_port, self.network_id)

        cprint(f"A total of {msg_count} messages were send this election", 'magenta')

        # Create a coordinator publisher thread
        coordinator_publisher_thread: Thread = threading.Thread(target=self.check_network, args=["COORDINATOR"])
        coordinator_publisher_thread.start()

    # ------------------------------------------------------------------------------------------------------------------
    # TODO i dont think this method is even used
    # def disconnect(self) -> None:
    #     """
    #     When a node is shutdown i.e. when Ctrl+c is pressed on the keyboard, then this method is called
    #     in an except block, which ensures that the node 'gently' disconnects from its connection
    #     to the other nodes in the network.
    #     """
    #     for node in self.nodes:
    #         # self.client_socket.disconnect("tcp://{}:{}".format(node.ip, node.server_port))
    #         # self.client_socket.disconnect("tcp://{}:{}".format(node.ip, node.publisher_port))
    #         self.client_socket.disconnect(f"tcp://{node.host_ip}:{node.server_port}")
    #         # print("FOOFOFOFOFOF")
    #         get_line_info()

    # ------------------------------------------------------------------------------------------------------------------
    def establish_connection(self, timeout_limit: int) -> None:
        """
        Set up the zeromq runtime context.
        Create a zmq reply socket, for the server socket, and a zmq request socket, for the client socket
        args:
            @TIMEOUT: int -- The time (in milliseconds) the client socket, should wait before trowing
                             an exception to indicate, that the node being requested is down.
        """
        self.REQ_REP_context = zmq.Context()

        # create a list of client sockets for all nodes with an greater network_id than self
        for node in self.nodes:
            if node.network_id > self.network_id:
                client_socket = self.REQ_REP_context.socket(zmq.REQ)
                # set the timeout duration to TIMEOUT
                client_socket.setsockopt(zmq.RCVTIMEO, timeout_limit)
                client_socket.connect(
                    f"tcp://{node.host_ip}:{node.server_port}")
                self.clients.append(client_socket)

        # create a reply socket for the server port
        self.server_socket = self.REQ_REP_context.socket(zmq.REP)
        self.server_socket.bind(f"tcp://{self.host_ip}:{self.server_port}")

        self.PUB_SUB_context = zmq.Context()

        self.publisher_socket = self.PUB_SUB_context.socket(zmq.PUB)
        self.publisher_socket.bind(
            f"tcp://{self.host_ip}:{self.publisher_port}")

        self.subscriber_socket = self.PUB_SUB_context.socket(zmq.SUB)
        # set the timeout duration to timeout_limit
        self.subscriber_socket.setsockopt(zmq.RCVTIMEO, timeout_limit)

        # in zeroMQ a subscriber can subscribe to multiple topics, and the published messages are
        # just interleaved instead. Therefore we can assign create one subscriber, which
        # is subscriped to multiple topics. One for each node in the system.
        for node in self.nodes:
            if node.network_id != self.network_id:
                self.subscriber_socket.connect(
                    f"tcp://{node.host_ip}:{node.publisher_port}")

        # By subscribing to "" (an empty subscription), the subscriber will get everything
        # published on the topic/port (every single topic from publisher)
        self.subscriber_socket.subscribe("")

    # ------------------------------------------------------------------------------------------------------------------
    def is_coordinator(self) -> bool:
        """
        Return true, if the node instance is the coordinator in the network, and false if not.
        """
        return self.coordinator.coordinator_id == self.network_id

    # ------------------------------------------------------------------------------------------------------------------
    def run(self, timeout_limit: int) -> None:
        """
        Spin up the node
        """
        self.establish_connection(timeout_limit)

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
            # Wait for next request from client, request are only send when an election is hold initiated
            get_line_info()
            request = self.server_socket.recv_pyobj()
            if request["msg_type"] == "ELECTION":
                msg = {"msg_type": "OK",
                       "node": {
                           "host_ip": self.host_ip,
                           "publisher_port": self.publisher_port,
                           "server_port": self.server_port,
                           "network_id": self.network_id,
                       },
                       "args": None
                       }

                self.server_socket.send_pyobj(msg)  # send message back
                self.election()  # hold own election

    # ------------------------------------------------------------------------------------------------------------------
    # TODO
    def election(self) -> None:
        """
        Have a list of clients instead of 1 client being connected to multiple servers.
        Its hard to reason about
        """
        # use the count to verify if self is the highest node alive, and
        # to print the number of messages sent.
        count: int = 0
        # msg_count: int = 0
        msg_count: int = self.number_of_nodes - self.network_id
        for client in self.clients:
            get_line_info()
            try:
                msg = {"msg_type": "ELECTION",
                       "node": {
                           "host_ip": self.host_ip,
                           "publisher_port": self.publisher_port,
                           "server_port": self.server_port,
                           "network_id": self.network_id,
                       },
                       "args": self.number_of_nodes - self.network_id
                       }

                client.send_pyobj(msg)

                # client.send_string("ELECTION") # MAYBE ADD DATA ABOUT WHO send the message
                # use pickle to serialize the message object pickle.dump(msg)
                reply = client.recv_pyobj()
                if reply["args"] is not None:
                    get_line_info()
                    msg_count += reply["args"]
                count += 1
            except:
                pass

        if count == 0:
            self.declare_new_coordinator(msg_count)
        else:
            pass
            # do nothing there are higher nodes in the system

    # ------------------------------------------------------------------------------------------------------------------
    def run_client(self) -> None:
        """
        The coordinator is set to none when selfs subscriber does not register the heart-beat from th
        the coordinator, this is used as an indication to start an election.
        """
        while True:
            if self.coordinator.coordinator_id is None:
                self.election()

# ----------------------------------------------------------------------------------------------------------------------

# TODO
def check_input(input: Tuple[str, int, int, int]) -> bool:
    # pattern = re.compile('')
    return True


def main() -> None:

    if len(sys.argv) != 5:
        cprint("WRONG NUMBER OF ARGUMENTS", 'red')
        cprint("{} were given, but 4 is needed".format(len(sys.argv) - 1), 'red')
        print("The first argument should be the host_ip address e.g. 127.0.0.1")
        print("The second- and third argument should be the client- and server port respectively e.g. 9000 9001")
        print("The fourth argument should be the unique unsigned integer id of the node being started e.g 2")
        cprint(
            "NOTE all four arguments MUST match one of the lines in the file network.config", 'red')
        sys.exit(1)

    host_ip: str = str(sys.argv[1])
    publisher_port: int = int(sys.argv[2])
    server_port: int = int(sys.argv[3])
    network_id: int = int(sys.argv[4])

    timeout_limit: int = 2500

    if not check_input((host_ip, publisher_port, server_port, network_id)):
        cprint("INVALID INPUT", 'red')
        # TODO
        sys.exit(1)

    node: Node = Node(host_ip, publisher_port, server_port, network_id)
    try:
        node.run(timeout_limit)
    # when hitting Ctrl+C
    # FIXME does not enter
    except KeyboardInterrupt:
        node.disconnect()


if __name__ == "__main__":
    main()
