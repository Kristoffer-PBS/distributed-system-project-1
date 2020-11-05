#ifndef _NETWORK_H_
#define _NETWORK_H_

#include <iostream>
#include <memory>
#include <vector>
#include <random>
#include <thread>
#include <chrono>


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

    public:
        Network(int n) : _size(n) {
            for (int i = 0; i < n; i++) {
                vector_of_nodes.push_back(make_shared<Node>(i));
                // vector_of_nodes.push_back(new Node(i));
            }

            // hack
            for (int i = 0; i < n; i++) {
                vector_of_nodes[i]->attach_connections(vector_of_nodes);
            }
        }

        void tick() {
            for (auto& node : vector_of_nodes) {
                // probably don't have to break here
                if (!node->check_coordinator()) {
                    break;
                }
            }
        }

        void run() {
            for (auto& node : vector_of_nodes) {
                node->print_references();
                // cout << node->get_id() << " ";
            }
            cout << endl;
        }


};


#endif // _NETWORK_H_