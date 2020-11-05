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

        std::vector<std::shared_ptr<Node>> vector_of_nodes;
        // std::vector<Node*> vector_of_nodes;

        int id;
        int coordinator_id = -1;
        int _size;

    public:
        Node(int id, std::vector<std::shared_ptr<Node>> vec) : id(id), vector_of_nodes(vec) {
            _size = vector_of_nodes.size();
        }
        Node(int id) : id(id) {
        }

        void attach_connections(vector<shared_ptr<Node>>& vec) {
        // void attach_connections(vector<Node*>& vec) {
            // for (int i = 0; i < vec.size(); i++) {
            //     vector_of_nodes.push_back(vec[i]);
            // }

            for (auto node : vec) {
                vector_of_nodes.push_back(node);
            }

            // vector_of_nodes = vec;
            _size = vector_of_nodes.size();
        }

        void activate() {
            this->active = true;
            _size += 1;
        }

        bool check_coordinator() {
            coordinator_id = 2;
            bool b = this->vector_of_nodes[coordinator_id]->active;

            return b;
        }

        void deactivate() {
            this->active = false;
            _size -= 1;
        }

        void improved_election() {

        }

        void declare_new_coordinator() {
            std::cout << "node " << id << " is the new coordinator" << std::endl;

            // update the other
            for (auto node : vector_of_nodes) {
                node->coordinator_id = id;
            }

            // update self
            coordinator_id = id;
        }

        int get_id() { return id; }

        void print_references() {
            for (auto& node : vector_of_nodes) {
                cout << node->get_id() << " ";
            }
            cout << endl;
        }


};


#endif // _NODE_H_



