#include "../include/utilities.h"

string print_red(const string& str) {
    return "\x1b[35;5;31m" + str + "\033[0m";
}

string print_green(const string& str) {
    return "\x1b[35;5;32m" + str + "\033[0m";
}

string print_yellow(const string& str) {
    return "\x1b[35;5;33m" + str + "\033[0m";
}

string print_blue(const string& str) {
    return "\x1b[35;5;34m" + str + "\033[0m";
}

string print_magenta(const string& str) {
    return "\x1b[35;5;35m" + str + "\033[0m";
}
string print_cyan(const string& str) {
    return "\x1b[35;5;36m" + str + "\033[0m";
}