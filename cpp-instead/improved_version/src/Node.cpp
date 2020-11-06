#include "Node.h"
#include "utilities.h"

Node::Node(int id) : id(id) {}


void Node::attach_connections(vector<shared_ptr<Node>>& vec) {
    for (auto& node : vec) {
        vector_of_nodes.push_back(node);
    }

    _size = vector_of_nodes.size();
}

bool Node::check_coordinator() {
    // if (coordinator_id == -1) {
    //     return false;
    // }
    return vector_of_nodes[coordinator_id]->is_ok();
}

void Node::activate() {
    this->active = true;
    _size += 1;
}

// FIXME
void Node::deactivate() {
    this->active = false;
    _size -= 1;
}

void Node::improved_election() {
    int count = 0;
    int highest_id = this->id + 1;

    // only check nodes with an higher id than self.
    for (int i = this->id; i < vector_of_nodes.size(); i++) {
        if(vector_of_nodes[i]->is_ok()) {
            highest_id = std::max(highest_id, i);
            count += 1;
        }
    }

    // declare self coordinator
    if (count == 0) {
        declare_new_coordinator();
    }
    // else inform the highest responding node to hold an election
    else {
        vector_of_nodes[highest_id]->improved_election();
    }
}



void Node::declare_new_coordinator() {
    std::cout << "\x1b[35;5;32m" << "node " << id << " is the new coordinator" << "\033[0m" << std::endl;

    // update the other
    for (auto& node : vector_of_nodes) {
        node->coordinator_id = id;
        node->unhalt();
    }

    // TODO this should not be nesecasry
    // update self
    // coordinator_id = id;
    // this->unhalt();
}


void Node::print_references() {
    for (auto& node : vector_of_nodes) {
        cout << node->get_id() << " ";
    }
    cout << endl;
}


void Node::halt_network() {
    for (auto& node : vector_of_nodes) {
        if (node->get_id() != this->id) {
            node->halt();
        }
    }
}