import zmq
import time
import parse # TODO
import sys
import threading
from threading import Thread
from termcolor import cprint

from typing import Any, Dict, List

from enum import Enum, unique

@unique
class State(Enum):
    Coordinator = 1
    Normal = 2

    def __str__(self) -> str:
        return "in state: {}".format(self.name)


class Node:
    class Info:
        """
        Nested subclass of the Node class, used to create better structure, and avoid the anti-pattern
        of not using structured types to relate related data.
        """
        ip: str
        client_port: str
        server_port: str
        id: int

        def __init__(self, ip: str, client_port: str, server_port: str, id: int) -> None:
            self.id = id
            self.ip = ip
            self.client_port = client_port
            self.server_port = server_port

    # ------------------------------------------------------------------------------------------------------------------

    """
    sd
        methods:
            is_coordinator() -> Bool:
            run() -> None:
            run_client() -> None:
            run_server() -> None:
    """
    coordinator_id: int
    maxID: int
    node_id: int
    number_of_connections: int
    process_ip: str
    process_server_port: int
    process_client_port: int
    # TODO change to proper type
    nodes: List[Info]



    def __init__(self, process_ip: str, server_port: int, client_port: int, node_id: int) -> None:
        config_file = open("nodes.config", 'r')
        input = config_file.readlines()
        n = int(input[0])
        self.processes = []
        self.maxID = 0
        self.id: int = id
        self.coordinator_id: int = -1
        self.process_port2 = process_port2

        self.nodes = []

        for i in range(1, n + 1):
            line = parse.parse('{} {} {} {}', input[i])
            self.maxID = max(self.maxID, int(line[3]))
            self.nodes.append(self.Info(
                ip=line[0],
                server_port=line[1],
                client_port=line[2],
                id=int(line[3])
                ))


        self.process_ip = process_ip
        self.server_port = server_port
        self.client_port = client_port
        self.node_id = node_id
        self.coordinator_id = -1


    # ------------------------------------------------------------------------------------------------------------------

    def clock_tick(self, process=None) -> None:
        """
        main loop
        """
        if process is State.Coordinator:
            while int(self.coordinator_id) == int(self.node_id):
                self.clock_socket.send_string("alive {} {} {}".format(self.process_ip, self.process_server_port, self.node_id))
                time.sleep(1)
        else:
            while True:
                try:
                    coordinator_clock_tick = self.clock_socket2.recv_string()
                    request = parse.parse("alive {} {} {}".format(coordinator_clock_tick))
                    if (int(request[0] > self.node_id)):
                        cprint("coordinator {}".format(coordinator_clock_tick), 'green')
                        self.update_coordinator(str(request[0]), str(request[1]), int(request[2]))
                except:
                    if not self.is_coordinator():
                        cprint("Coordinator is down, starting election\n", 'red')
                        self.coordinator_id = -1

    # ------------------------------------------------------------------------------------------------------------------

    def is_coordinator(self) -> bool:
        """
        Return true, if the node instance is the coordinator in the network, and false if not.
        """
        return self.coordinator_id == self.node_id

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

        self.server_socket = self.context.socket(zmq.REP)
        self.server_socket.bind("tcp://{}:{}".format(self.process_ip, self.process_server_port))

        self.client_socket = self.context.socket(zmq.REQ)
        self.client_socket.setsocketopt(zmq.RECVTIMEO, TIMEOUT)
        self.connect_to_higher_ids()

        self.clock_context = zmq.Context()
        self.clock_socket = self.clock_context.socket(zmq.PUB)
        self.clock_socket.bind("tcp://{}:{}".format(self.process_ip, self.process_client_port))

    # ------------------------------------------------------------------------------------------------------------------
    def connect_all(self) -> None:
        """

        """
        for node in self.nodes:

            if node["id"] != self.node_id:
                self.


    # ------------------------------------------------------------------------------------------------------------------
    def connect_to_network(self) -> None:
        """
        """
        for p in self.processes:
            if int(p['id'] != int(self.node_id)):
                pass


    # ------------------------------------------------------------------------------------------------------------------

    def connect_to_higher_ids(self):
        pass

    # ------------------------------------------------------------------------------------------------------------------
    def declare_coordinator(self) -> None:
        cprint("[{}:{}] is the new coordinator.".format(self.process_ip, self.process_server_port), 'blue')
        self.update_coordinator(self.process_ip, self.process_server_port, self.node_id)
        coordinator_clock_thread: Thread = threading.Thread(target=self.clock_tick, args=["COORDINATOR"])
        coordinator_clock_thread.start()

    # ------------------------------------------------------------------------------------------------------------------
    def disconnect(self) -> None:
        for node in self.nodes:
            self.client_socket.disconnect("tcp://{}:{}".format(node["ip"], node["port"][1]))


    # ------------------------------------------------------------------------------------------------------------------
    def system_clock(self) -> None:
        pass

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
                    if self.node_id == self.maxID:
                        self.declare_coordinator()
                    else:
                        self.client_socket.send_string("ELECTION")
                        request: str = self.client_socket.recv_string()
                except:
                    self.declare_coordinator()


    # ------------------------------------------------------------------------------------------------------------------
    def update_coordinator(self, process_ip: str, server_port: int, node_id: int) -> None:
        self.coordinator_ip   = process_ip
        self.coordinator_port = server_port
        self.coordinator_id   = node_id


    # ------------------------------------------------------------------------------------------------------------------
    def run(self) -> None:
        """
        Spin up the node
        """
        self.establish_connection(2000)


        # TODO do we need the args=[]
        system_clock_thread: Thread = threading.Thread(target=self.system_clock, args=[])
        system_clock_thread.start()

        server_thread: Thread = threading.Thread(target=self.run_server, args=[])
        server_thread.start()

        client_thread: Thread = threading.Thread(target=self.run_client, args=[])
        client_thread.start()

# ----------------------------------------------------------------------------------------------------------------------

def main() -> None:
    ip: str = str(sys.argv[1])
    server_port: int = int(sys.argv[2])
    client_port: int = int(sys.argv[3])
    node_id: int = int(sys.argv[4])

    node: Node = Node(ip, server_port, client_port, node_id)

    node.run()

if __name__ == "__main__":
    main()