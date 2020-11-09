#ifndef NETWORK_H
#define NETWORK_H

#include <chrono>
#include <iostream>
#include <iomanip>
#include <thread>
#include <vector>

#include "Rng.h"
#include "utilities.h"

using namespace std;

class Test;

class Network {
    friend class Test;

    private:
        // Struct representing the data describing a node in the network
        struct Node {
            int id;
            int coordinator_id;
            int prev_coordinator_id;
            bool halted;
            bool active;
            bool election_flag;
            bool election_is_over;

            int election_count;

            int messages_sent;
            int messages_received;



            Node(int id, int coordinator_id) : id(id), coordinator_id(coordinator_id), prev_coordinator_id(coordinator_id) {
                active = true;
                halted = false;
                election_flag = false;
                election_is_over = true;
                election_count = 0;
                messages_sent = 0;
                messages_received = 0;
            }
        };

        vector<Node> nodes;  // the network has a vector of Nodes
        int active_nodes = 0;
        int coordinator_id;
        int election_stack_count = 0;
        Rng rng_engine;  // random number generator

        void halt_network();
        void bully_election(int node, int accumelated_sum);
        void declare_new_coordinator(int node, int total_messages_sent);
        void deactivate_coordinator();
        void tick();

    public:
        Network(int n);
        void print_network_topology();
        void run(std::size_t time);
};

#endif // NETWORK_H
