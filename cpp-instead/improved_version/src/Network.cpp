#include "Network.h"
#include "utilities.h"


Network::Network(int n) : _size(n) {
    for (int i = 0; i < n; i++) {
        vector_of_nodes.push_back(make_shared<Node>(i));
    }

    // hack
    for (int i = 0; i < n; i++) {
        vector_of_nodes[i]->attach_connections(vector_of_nodes);
    }

    vector_of_nodes[n - 1]->declare_new_coordinator();
}



vector<int> Network::random_sequence(int start, int end) {
    vector<int> output;

    for (int i = 0; i < end - start; i++) {
        output.push_back(i);
    }

    int count = 0;

    while (count < end - start) {
        int first  = std::uniform_int_distribution<>(start, end - 1)(rng_engine);
        int second = std::uniform_int_distribution<>(start, end - 1)(rng_engine);

        if (start == end) {
            continue;
        }

        std::swap(output[first], output[second]);
        count += 1;
    }

    return output;
}

int Network::random_number(int start, int end) {
    return std::uniform_int_distribution<>(start, end)(rng_engine);
}




void Network::tick() {
    // generate a random sequence of numbers, used to index the vector_of_nodes
    vector<int> seq = random_sequence(0, vector_of_nodes.size() - 1);

    // iterate through and make each node check if the coordinator is up
    for (int i : seq) {
        cout << i << endl;
        if (!vector_of_nodes[i]->check_coordinator()) {
            string msg = "Coordinator is down starting election!";
            cout << print_green(msg) << endl;
            // cout << "\x1b[35;5;31m" << "Coordinator is down starting election!" << "\033[0m" << std::endl;
            // Halt the other nodes, so that they won't start an
            // election. NOTE this is 'irrelevant' in this dummy implementation
            // as all the code execution is sequential
            vector_of_nodes[i]->halt_network();
            vector_of_nodes[i]->improved_election();
        }
    }

    // at every cycle there is a 20% change for a node to be deactivated
    int rand_num = random_number(0, vector_of_nodes.size() -1);
    int chance = random_number(0, 10000);
    if (chance % 5 == 1) {
        cout << "\x1b[35;5;33m" << "deactivating node: " << rand_num << "\033[0m" << endl;
        vector_of_nodes[rand_num]->deactivate();
    }

    // and a 20% for one being deactivated. This is to try and simulate the
    rand_num = random_number(0, vector_of_nodes.size() - 1);
    chance = random_number(0, 10000);
    if (chance % 5 == 1) {
        cout << "\x1b[35;5;33m" << "activaring node: " << rand_num << "\033[0m" << endl;
        vector_of_nodes[rand_num]->activate();
    }
}



void Network::print_network_topology() {
    int col = vector_of_nodes.size();

}

void Network::run(size_t time_units) {
    for (int i = 0; i < time_units; i++) {
        cout << "tick " << i << endl;
        tick();
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
}