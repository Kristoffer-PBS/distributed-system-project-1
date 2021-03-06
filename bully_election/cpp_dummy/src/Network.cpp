#include "../include/Network.h"


Network::Network(int n) : active_nodes(n) {
    for (int i = 0; i < n; i++) {
        nodes.push_back(Node(i, n - 1));
    }

    coordinator_id = n - 1;
}

void Network::declare_new_coordinator(int node, int total_messages_sent) {
    total_messages_sent = 0;
    // The coordinator messages sent back.
    total_messages_sent += node;

    coordinator_id = node;
    // TODO
    nodes[node].active = true;

    for (int i = 0; i < nodes.size(); i++) {
        nodes[i].coordinator_id = node;
        nodes[i].halted = false;
        nodes[i].election_flag = false;
        nodes[i].election_is_over = true;

        nodes[i].election_count = 0;
        total_messages_sent += nodes[i].messages_sent + nodes[i].messages_received;
        nodes[i].messages_sent = 0;
        nodes[i].messages_received = 0;
    }


    cout << print_yellow("node " + std::to_string(nodes[node].id) + " is the new coordinator") << endl;
    cout << print_cyan("A TOTAL OF " + std::to_string(total_messages_sent) + " WERE SENT THIS ELECTION") << "\n\n";
}

void Network::halt_network() {
    for (auto& node : nodes) {
        // used to avoid needless election due to sequential emulation
        node.prev_coordinator_id = node.coordinator_id;
        node.halted = true;
        node.election_is_over = false;
    }
}


void Network::print_network_topology() {

    // 1. compute the number of digits needed to properly, align all ids in the network
    int width = 0;
    int tmp = nodes.size() - 1;

    while (tmp != 0) {
        width++;
        tmp /= 10;
    }

    // 2. print the top border
    cout << "╭";
    for (int i = 1; i < (width + 2 + 1) * nodes.size(); i++) {
        if (i % (width + 2 + 1) == 0) {
            cout << "┬";
        }
        else {
            cout << "─";
        }
    }
    cout << "╮" << "\n";

    // 3. iterate through the number of Nodes, and print their id with a matching color representing, their
    // state: normal(green), red(deactivated), yellow(coordinator).
    for (int j = 0; j < nodes.size(); j++) {
        cout << "│";

        string color;

        if (nodes[j].active) {
            color = "\x1b[32m"; // green
            if (coordinator_id == nodes[j].id) {
                color = "\x1b[33m"; // yellow
            }
        }
        else {
            color = "\x1b[31m"; // red
        }

        cout << " " << color << std::setw(width) << nodes[j].id << "\033[0m" << " ";
    }

    cout << "│" << endl;

    // 4. print the bottom border.
    cout << "╰";

    for (int i = 1; i < (width + 2 + 1) * nodes.size(); i++) {
        if (i % (width + 2 + 1) == 0) {
            cout << "┴";
        }
        else {
            cout << "─";
        }
    }

    cout << "╯" << endl;
    cout << "\n\n";
}

// used to simulate and get some empirical data
// int node is the id, of the node holding the election.
void Network::bully_election(int node, int accumelated_sum) {

    int messages_sent     = 0;
    int messages_received = 0;
    nodes[node].messages_sent     = 0;
    nodes[node].messages_received = 0;


    vector<int> next_electioners;

    // only check nodes with an higher id than self.
    for (int i = nodes[node].id + 1; i < nodes.size(); i++) {
        messages_sent += 1;
        nodes[node].messages_sent += 1;

        // if not participated then insert
        // scheduled to be in an election

        // update the variable storing the id, of the node responding to the election msg with the
        // highest id.
        if(nodes[i].active) {
            messages_received += 1;
            nodes[node].messages_received += 1;
                // cout << print_cyan("election count for " + to_string(i) + " is " + to_string(nodes[i].election_count)) << endl;

            if (nodes[i].election_count == 0) {
                next_electioners.push_back(i);
                nodes[i].election_count += 1;
            }
        }
    }

    cout << "Node " << print_blue(std::to_string(nodes[node].id))
         << " has sent " << print_magenta(std::to_string(nodes.size() - 1 - nodes[node].id))
         << " messages this election"
         << " and received " << print_magenta(std::to_string(messages_received)) << " replies"
         << endl;

    // declare self coordinator
    if (messages_received == 0) {
        declare_new_coordinator(node, accumelated_sum + messages_sent + messages_received);
    }
    else {
        for (int id : next_electioners) {
            bully_election(id, accumelated_sum + messages_sent + messages_received);
        }
    }
}

void Network::tick() {
    // generate a random sequence of numbers, used to index the nodes
    vector<int> seq = rng_engine.random_sequence(0, nodes.size() - 1);


    // iterate through and make each node check if the coordinator is up
    for (int i : seq) {
        // if the node is not the coordinator, and is not halted because
        // of an ongoing election, then it can check up on the coordinator.
        if (coordinator_id != nodes[i].id && !nodes[i].halted) {

            // if the coordinator is discovered to not be active, then the network is halted
            // and and election is started by the node which discovered it.
            if (!nodes[coordinator_id].active) {

                cout << "Node " << print_green(std::to_string(nodes[i].id)) << " has discovered ";
                cout << "that the coordinator " << print_yellow(std::to_string(coordinator_id));
                cout << " is down\n" << print_yellow("starting election") << endl;

                halt_network();
                bully_election(i, 0);
            }
        }
    }

    // at every cycle there is a 33% change for a node to be deactivated
    int rand_num = rng_engine.random_number(0, nodes.size() -1);
    int chance = rng_engine.random_number(0, 100);

    if (chance % 3 == 1 && nodes[rand_num].active) {
        cout << print_red("deactivating node: " + std::to_string(rand_num)) << endl;
        nodes[rand_num].active = false;
    }

    // and a 50% for one being deactivated. This is to try and simulate the
    rand_num = rng_engine.random_number(0, nodes.size() - 1);
    chance   = rng_engine.random_number(0, 100);

    if (chance % 2 == 1 && !nodes[rand_num].active) {
        cout << print_green("activating node: " + std::to_string(rand_num)) << endl;
        nodes[rand_num].active = true;
        cout << "Node " << print_blue(std::to_string(rand_num)) << " does not know who the coordinator is";
        cout << " and has to start an election to find out.\n"  << endl;
        // start election when waking up again
        bully_election(nodes[rand_num].id, 0);
    }
}

void Network::deactivate_coordinator() {
    cout << print_red("deactivating the coordinator " + std::to_string(coordinator_id)) << endl;
    nodes[coordinator_id].active = false;
}

// Simple simulation to run
void Network::run(std::size_t time_units) {

    for (int i = 0; i < time_units; i++) {
        cout << "tick " << i << endl;
        print_network_topology();
        tick();
        if (i % 10 == 0) {
            deactivate_coordinator();
        }

        std::this_thread::sleep_for(std::chrono::seconds(1));
        std::cin.get();
    }
}
