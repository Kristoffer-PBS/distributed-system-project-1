#include "../include/utilities.h"
#include "../include/Network.h"


int main(int argc, char *argv[]) {

    if (argc != 2) {
        cout << print_red("invalid number of arguments " + std::to_string(argc) + " were given, but 1 is needed") << endl;
        return 1;
    }
    
    int number_of_nodes = std::atoi(argv[1]);

    if (number_of_nodes < 0) {
        cout << print_red("number of nodes cannot be negative") << endl;
        return 1;
    }

    Network nw(number_of_nodes);

    nw.run(100);

    return 0;
}
