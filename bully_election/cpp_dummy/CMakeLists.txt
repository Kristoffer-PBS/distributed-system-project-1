cmake_minimum_required(VERSION 3.0)
project(improved_bully_election_algorithm_dummy)

set(CMAKE_CXX_STANDARD 17)

add_executable(improved_bully_election_algorithm_dummy
    src/main.cpp
    src/Network.cpp   include/Network.h
    src/Rng.cpp       include/Rng.h
    src/utilities.cpp include/utilities.h
)
