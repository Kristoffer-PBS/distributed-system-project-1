#ifndef RNG_H
#define RNG_H

#include <chrono>
#include <random>
#include <vector>

using namespace std;

// Random number generator class
class Rng {
    public:
    Rng() {}
    vector<int> random_sequence(int start, int end);
    int random_number(int start, int end);

    private:
        std::mt19937 rng_engine { std::chrono::high_resolution_clock::now().time_since_epoch().count() };
};

#endif // RNG_H
