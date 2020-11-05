import zmq
import time
# import parse  # TODO
import sys
import threading
from threading import Thread
from termcolor import cprint

from typing import Any, Dict, List, Tuple, Optional
import inspect  # debug information
from enum import Enum, unique
import pickle
from pickle import dump, loads


def get_line_info() -> None:
    """
    Helper function for debug purposes.
    """
    print(inspect.stack()[1][1], ":", inspect.stack()
          [1][2], ":", inspect.stack()[1][3])


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

        def __init__(self, coordinator_ip: str = None, coordinator_port: int = None, coordinator_id: int = None) -> None:
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
        self.server_port = server_port
        self.network_id = network_id

        # TODO
        self.ongoing_election: bool = False

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

        # TEST
        assert(self.number_of_nodes == 8)

    # ------------------------------------------------------------------------------------------------------------------
    def check_network(self, state: str) -> None:
        """
        If self is not the coordinator i.e. NORMAL then run an infinite loop, where the publisher
        topic is repeatedetly listened to using self.subscriber_port. If no msg is received within the
        timeout_limit of the socket, then we can assume the coordinator is down, and we can start an election.

        If self is the coordinator, then a loop is executed as long as self.network_id == self.coordinator.coordinator_id
        In this loop a simple msg is constructed, and published, on this nodes publisher topic.
        """
        if state == "NORMAL":
            while True:
                try:
                    # TODO maybe inser the self.ongoing_election here
                    # check if a msg is published on the coordinator topic, and print the received
                    # identifiers of the publisher, if it is up.
                    coordinator_msg = self.subscriber_socket.recv_string()
                    (_, host_ip, publisher_port, network_id) = coordinator_msg.split()
                    print(f"{host_ip} {publisher_port} {network_id}")

                    # Check if the one announcing coordinatorship actually has a higher ID than self
                    if int(network_id) > self.network_id:
                        cprint(f"Coordinator {host_ip}:{publisher_port} {network_id} is UP", 'green')
                        self.coordinator.update(host_ip, int(publisher_port), int(network_id))

                except:
                    # TEST second condition is nesecary
                    # if self.coordinator.coordinator_id != self.network_id:
                    if self.coordinator.coordinator_id != self.network_id and not self.ongoing_election:
                        cprint("Coordinator is down, an election will be started\n", 'red')
                        self.coordinator.coordinator_id = None

        elif state == "COORDINATOR":
            # The while condition is used to terminate the thread when a node with a higher ID, has
            # entered the network.
            while self.coordinator.coordinator_id == self.network_id:

                msg: str = f"UP {self.host_ip} {self.publisher_port} {self.network_id}"
                self.publisher_socket.send_string(msg)
                cprint(f"I am the coordinator: {self.network_id}", 'yellow')
                time.sleep(2)

    # ------------------------------------------------------------------------------------------------------------------
    def declare_new_coordinator(self, msg_count: int) -> None:
        """
        The winner of the election gets to call this method.
        It will print out a message clarifying who the winner of the election is,
        and how many messages were sent during the election.

        The new coordinator will then create a publisher thread, runnning the method
        self.check_network("COORDINATOR"), which updates the other nodes in the network
        about who the coordinator is. This publisher thread will run until, this node
        crashes/deactivates or when, a new node with an higher ID than self, joins
        the network, and take on the responsibility of being coordinator.
        """
        cprint(f"[{self.host_ip}:{self.server_port}] is the new coordinator", 'green')
        self.coordinator.update(self.host_ip, self.server_port, self.network_id)

        cprint(f"A total of {msg_count} messages were send this election", 'magenta')

        # Create a coordinator publisher thread
        self.publisher_thread = threading.Thread(target=self.check_network, args=["COORDINATOR"])
        self.publisher_thread.start()
        # coordinator_publisher_thread: Thread = threading.Thread(target=self.check_network, args=["COORDINATOR"])
        # coordinator_publisher_thread.start()

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

    # ------------------------------------------------------------------------------------------------------------------
    def establish_connection(self, timeout_limit: int) -> None:
        """
        Set up the zeromq runtime context.
        Create a zmq reply socket, for the server socket, and a list of zmq request sockets, for the client sockets
        which will be connected to the server sockets of all the higher nodes in the network.
        Then create a publisher socket, used to broadcast (heartbeat) when the node is the coordinator,
        and a subscriber socket, which subscribes to the other nodes publishers, and is used
        to communicate who the publisher is.
        args:
            @TIMEOUT: int -- The time (in milliseconds) the client socket, should wait before trowing
                             an exception to indicate, that the node being requested is down.
        """
        # Create a zeroMQ context for the client-server pair sockets to communicate in.
        # self.REQ_REP_context = zmq.Context()
        self.context = zmq.Context()

        # create a list of client sockets for all nodes with a greater network_id than self.
        for node in self.nodes:
            if node.network_id > self.network_id:
                # client_socket = self.REQ_REP_context.socket(zmq.REQ)
                client_socket = self.context.socket(zmq.REQ)
                # set the timeout duration to timeout_limit
                client_socket.setsockopt(zmq.RCVTIMEO, timeout_limit)
                client_socket.connect(f"tcp://{node.host_ip}:{node.server_port}")
                self.clients.append(client_socket)

        # create a reply socket for the server port
        # self.server_socket = self.REQ_REP_context.socket(zmq.REP)
        self.server_socket = self.context.socket(zmq.REP)
        self.server_socket.bind(f"tcp://{self.host_ip}:{self.server_port}")

        # Create a zeroMQ context for the publish- and subscribe socket to communicate in.
        # self.PUB_SUB_context = zmq.Context()

        # self.publisher_socket = self.PUB_SUB_context.socket(zmq.PUB)
        self.publisher_socket = self.context.socket(zmq.PUB)
        self.publisher_socket.bind(f"tcp://{self.host_ip}:{self.publisher_port}")

        # self.subscriber_socket = self.PUB_SUB_context.socket(zmq.SUB)
        self.subscriber_socket = self.context.socket(zmq.SUB)
        # set the timeout duration to timeout_limit
        self.subscriber_socket.setsockopt(zmq.RCVTIMEO, timeout_limit)

        # in zeroMQ a subscriber can subscribe to multiple topics, and the published messages are
        # just interleaved instead. Therefore we can create one subscriber, which
        # is subscriped to multiple topics. One for each node in the system.
        for node in self.nodes:
            if node.network_id != self.network_id:
                self.subscriber_socket.connect(f"tcp://{node.host_ip}:{node.publisher_port}")

        # By subscribing to "" (an empty subscription), the subscriber will get everything
        # published on the topic/port (every single topic from publisher)
        self.subscriber_socket.subscribe("")



    # ------------------------------------------------------------------------------------------------------------------
    # TODO
    def election(self) -> None:
        """
        Have a list of clients instead of 1 client being connected to multiple servers.
        Its hard to reason about
        """
        # use the count to verify if self is the highest node alive, and
        # to print the number of messages sent.
        self.ongoing_election = True

        count: int = 0
        # msg_count: int = 0
        msg_count: int = self.number_of_nodes - self.network_id
        for idx, client in enumerate(self.clients):
            print(f"Sending election message to {idx}")
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
                print(reply)

                # TODO
                # if reply["msg_type"] == "OK":

                if reply["args"] is not None:
                    get_line_info()
                    msg_count += reply["args"]
                count += 1
            except:
                print(f"No response received from {idx}")
                # pass

        # cprint(f"count is {count}", "magenta")
        if count == 0:
            self.declare_new_coordinator(msg_count)

        # do nothing there are higher nodes in the system
        self.ongoing_election = False

    # ------------------------------------------------------------------------------------------------------------------
    def is_coordinator(self) -> bool:
        """
        Return true, if the node instance is the coordinator in the network, and false if not.
        """
        return self.coordinator.coordinator_id == self.network_id

    # ------------------------------------------------------------------------------------------------------------------
    def run(self, timeout_limit: int) -> None:
        """
        Start the node by first setting up and establishing connections with the rest of the network,
        and then a create a separate thread, for the client, server and publisher socket, where
        the publisher socket, at first is started as a "NORMAL" node.
        """
        self.establish_connection(timeout_limit)

        self.server_thread: Thread = threading.Thread(target=self.run_server, args=[])
        self.server_thread.start()

        self.client_thread: Thread = threading.Thread(target=self.run_client, args=[])
        self.client_thread.start()

        self.publisher_thread: Thread = threading.Thread(target=self.check_network, args=["NORMAL"])
        self.publisher_thread.start()

    # ------------------------------------------------------------------------------------------------------------------
    def run_server(self) -> None:
        """
        """
        while True:
            # Wait for next request from client, request are only send when an election is hold initiated
            request = self.server_socket.recv_pyobj()
            if request["msg_type"] == "ELECTION":
                msg = {"msg_type": "OK",
                       "node": {
                           "host_ip": self.host_ip,
                           "publisher_port": self.publisher_port,
                           "server_port": self.server_port,
                           "network_id": self.network_id,
                       },
                       "args": self.number_of_nodes - self.network_id
                       }
                try:
                    self.server_socket.send_pyobj(msg)  # send message back
                    if not self.ongoing_election:
                        self.election()  # hold own election
                except:
                    pass

    # ------------------------------------------------------------------------------------------------------------------
    def run_client(self) -> None:
        """
        The coordinator is set to none when selfs subscriber does not register the heart-beat from
        the coordinator, this is used as an indication to start an election.
        """
        while True:
            # TEST the second condition added
            if self.coordinator.coordinator_id is None and not self.ongoing_election:
                self.election()

# ----------------------------------------------------------------------------------------------------------------------
def main() -> None:

    if len(sys.argv) != 5:
        cprint("WRONG NUMBER OF ARGUMENTS", 'red')
        cprint("{} were given, but 4 is needed".format(len(sys.argv) - 1), 'red')
        print("The first argument should be the host_ip address e.g. 127.0.0.1")
        print("The second- and third argument should be the client- and server port respectively e.g. 9000 9001")
        print("The fourth argument should be the unique unsigned integer id of the node being started e.g 2")
        cprint("NOTE all four arguments MUST match one of the lines in the file network.config", 'red')
        sys.exit(1)

    host_ip: str = str(sys.argv[1])
    publisher_port: int = int(sys.argv[2])
    server_port: int = int(sys.argv[3])
    network_id: int = int(sys.argv[4])

    timeout_limit: int = 2500

    node: Node = Node(host_ip, publisher_port, server_port, network_id)
    try:
        node.run(timeout_limit)
    # when hitting Ctrl+C
    except KeyboardInterrupt:
        node.disconnect()


if __name__ == "__main__":
    main()
