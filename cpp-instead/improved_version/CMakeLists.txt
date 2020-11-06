cmake_minimum_required(VERSION 3.0)

project(improved_bully_election_dummy)

include_directories(${PROJECT_SOURCE_DIR})

add_executable(src/main.cpp)
add_executable(src/Network.cpp)
add_executable(src/Node.cpp)

# add_executable(app main.cpp Network.cpp Node.cpp)