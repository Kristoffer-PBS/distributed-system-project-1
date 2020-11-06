#ifndef _NODE_H_
#define _NODE_H_

#include <vector>
#include <iostream>
#include <memory>

using namespace std;

class Node {
    private:
        enum class State {
            Normal,
            Coordinator,
            Halted
        };


        bool active = true;
        bool election_is_on = false;
        // bool halt = true;

        std::vector<std::shared_ptr<Node>> vector_of_nodes;
        // std::vector<Node*> vector_of_nodes;

        int id;
        // int coordinator_id = -1;
        int coordinator_id = 2;
        int _size;

    public:
        // Node(int id, std::vector<std::shared_ptr<Node>> vec) : id(id), vector_of_nodes(vec) {
        //     _size = vector_of_nodes.size();
        // }

        Node(int id);

        void attach_connections(vector<shared_ptr<Node>>& vec);

        void activate();

        void deactivate();

        bool check_coordinator();

        void improved_election();

        void declare_new_coordinator();

        void halt() { this->election_is_on = true; }
        void unhalt() { this->election_is_on = false; }

        void halt_network();

        bool is_ok() { return this->active; }

        int get_id() { return id; }

        void print_references();

};


#endif // _NODE_H_