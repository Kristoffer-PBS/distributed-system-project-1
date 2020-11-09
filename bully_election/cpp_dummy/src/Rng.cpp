#include "../include/Rng.h"

int Rng::random_number(int start, int end) {
    return std::uniform_int_distribution<int>(start, end)(rng_engine);
}

vector<int> Rng::random_sequence(int start, int end) {

    vector<int> output;

    for (int i = 0; i < end - start; i++) {
        output.push_back(i);
    }

    int count = 0;

    while (count < end - start) {
        int first  = std::uniform_int_distribution<int>(start, end - 1)(rng_engine);
        int second = std::uniform_int_distribution<int>(start, end - 1)(rng_engine);

        if (start == end) {
            continue;
        }

        std::swap(output[first], output[second]);
        count += 1;
    }

    return output;
}
