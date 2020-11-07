#include "../include/utilities.h"
#include "../include/Network.h"


int main(int argc, char *argv[]) {

    if (argc != 2) {
        cout << print_red("invalid number of arguments " + std::to_string(argc) + " were given, but 1 is needed") << endl;
        return 1;
    }

    Network nw(std::atoi(argv[1]));

    nw.run(100);

    return 0;
}
