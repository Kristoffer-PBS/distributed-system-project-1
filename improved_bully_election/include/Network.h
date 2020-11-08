#ifndef NETWORK2_H
#define NETWORK2_H

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
        struct Node {
            int id;
            int coordinator_id;
            bool halted;
            bool active;
            bool election_flag;

            Node(int id, int coordinator_id) : id(id), coordinator_id(coordinator_id) {
                active = true;
                halted = false;
                election_flag = false;
            }
        };

        vector<Node> nodes;
        int active_nodes = 0;
        int coordinator_id;
        Rng rng_engine;

        // DONE
        void halt_network();
        // DONE
        void improved_bully_election(int node);
        // DONE
        void declare_new_coordinator(int node);

        void deactivate_coordinator();
        // DONE
        void tick();

    public:
        // DONE
        Network(int n);
        // DONE
        void print_network_topology();
        // DONE
        void run(std::size_t time);
};

#endif // NETWORK2_H