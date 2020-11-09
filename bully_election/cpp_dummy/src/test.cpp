#include <cassert>  // assert()
#include <chrono>
#include <iostream>

#include "../include/utilities.h"
#include "../include/Network.h"

using namespace std;

class Test {
    private:
        int number_of_tests = 5;
        int successful_tests;
        float time_spent;
        int nodes;
        // friend class Network;

        Network dummy;

    public:
        Test(int nodes) : dummy(nodes) , nodes(nodes) {}

        bool run_test_suite() {
            cout << print_yellow("=========================================================================") << endl;
            cout << "Running unit tests..." << endl;

            successful_tests = 0;
            cout << "Testing Network constructor...";
            if (test_constructor(nodes)) {
                successful_tests++;
                cout << print_green("    PASSED!") << endl;
            } else {
                cout << print_red("    FAILED!") << endl;
            }

            cout << "Testing halt_network() method...";
            if (test_halt_network()) {
                successful_tests++;
                cout << print_green("    PASSED!") << endl;
            } else {
                cout << print_red("    FAILED!") << endl;
            }

            cout << "Testing declare_coordinator() method...";
            if (test_declare_coordinator()) {
                successful_tests++;
                cout << print_green("    PASSED!") << endl;
            } else {
                cout << print_red("    FAILED!") << endl;
            }

            cout << "Testing deactivate_coordinator() method...";
            if (test_deactivate_coordinator()) {
                successful_tests++;
                cout << print_green("    PASSED!") << endl;
            } else {
                cout << print_red("    FAILED!") << endl;
            }

            cout << "Testing improved_bully_election() method...";
            if (test_improved_bully_election()) {
                successful_tests++;
                cout << print_green("    PASSED!") << endl;
            } else {
                cout << print_red("    FAILED!") << endl;
            }

            print_metrics();
        }

        bool test_constructor(int nodes) {
            Network nw(nodes);
            if (nw.coordinator_id != nodes -1 && nw.nodes.size() == nodes) {
                return false;
            }
            return true;
        }

        bool test_halt_network() {
            Network nw(nodes);
            nw.halt_network();

            for (auto& node : nw.nodes) {
                if (node.halted == false) {
                    return false;
                }
            }
            return true;
        }

        bool test_declare_coordinator() {
            Network nw(nodes);
            nw.declare_new_coordinator(6);
            if (nw.coordinator_id != 6) {
                return false;
            }
            return true;
        }

        bool test_deactivate_coordinator() {
            Network nw(nodes);
            nw.deactivate_coordinator();

            if (nw.nodes[nw.coordinator_id].active != false) {
                return false;
            }
            return true;
        }

        bool test_improved_bully_election() {
            Network nw(10);
            nw.deactivate_coordinator();

            nw.improved_bully_election(5);
            if (nw.coordinator_id != 8) {
                return false;
            }
            return true;
        }

        void print_metrics() {
            cout << "\n\n";


            float score = ((float) successful_tests /(float) number_of_tests) * 100;

            if (score == 100) {
                cout << print_green("all test were successful. Test score: " + std::to_string(score) + "%") << endl;
            }
            else if (score == 0) {
                cout << print_red("ALL TESTS FAILED!! Test score: " + std::to_string(score) + "%") << endl;
            }

            else {
                cout << print_red("not all tests were successful. Test score: " + std::to_string(score) + "%") << endl;
            }

            cout << "\n" << print_yellow("=========================================================================") << endl;
        }

};


int main() {

    Test test(10);

    test.run_test_suite();


    return 0;
}
