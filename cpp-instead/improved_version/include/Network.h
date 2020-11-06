#ifndef _NETWORK_H_
#define _NETWORK_H_

#include <iostream>
#include <iomanip>
#include <memory>
#include <vector>
#include <random>
#include <thread>
#include <chrono>
#include <set>

// generate random numbers at random times, and use them to index i.e. random_num % vec.size() into
// the array, and deactivate a node to simulate it being down. and then check behaviour, when
// a node discovers it is down.

#include "Node.h"

using namespace std;


class Network {
    private:
        int _size = 0;

        vector<shared_ptr<Node>> vector_of_nodes;
        // vector<Node*> vector_of_nodes;

        std::mt19937 rng_engine {std::chrono::high_resolution_clock::now().time_since_epoch().count()};

        vector<int> random_sequence(int start, int end);

        int random_number(int start, int end);

    public:
        explicit Network(int n);

        void print_network_topology();

        void tick();

        void run(size_t time_units);
};


#endif // _NETWORK_H_