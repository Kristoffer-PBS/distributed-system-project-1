
#include <unistd.h>  // for sleep

#include <chrono>
#include <thread>
#include <iostream>
#include <random>
#include "Network.h"
#include "Node.h"


int main(int argc, char* argv[]) {

    Network nw(8);

    nw.run(100);

    return 0;
}