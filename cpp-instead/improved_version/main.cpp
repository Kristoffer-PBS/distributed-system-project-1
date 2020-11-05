
#include <unistd.h>  // for sleep

#include <chrono>
#include <thread>
#include <iostream>
#include <random>
#include "Network.h"


int main(int argc, char* argv[]) {
    Network nw(6);

    nw.run();

    // usleep(3);
    // std::this_thread::sleep_for(2);

    nw.tick();

    return 0;
}