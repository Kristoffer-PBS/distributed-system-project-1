#pragma once
// #ifndef _UTILITIES_H_
// #define _UTILITIES_H_

#include <string>

using namespace std;

string print_red(string str) {
    return "\x1b[35;5;31m" + str + "\033[0m";
}

string print_green(string str) {
    return "\x1b[35;5;32m" + str + "\033[0m";
}

string print_yellow(string str) {
    return "\x1b[35;5;33m" + str + "\033[0m";
}

// #endif // _UTILITIES_H_