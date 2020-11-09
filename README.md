# distributed-system-project-1
repository for project 1 in distributed systems 2020 about leader election algorithms.

The repository contains two directories  `bully_election` and  `improved_bully_election`, which contains a demo implementation for the original bully election algorithm, presented by Héctor García-Molina in 1982, and an improved version presented in the paper *Improved Bully Election Algorithm for Distributed Systems* by *P Beaulah Soundarabai et al.* in 2014 respectively. A copy of both articles can be found in the `litterature` directory.



## Build dependencies

The python implementation is tested with python version 3.7.0, but should be working with older versions of python. The communication between different process nodes are implemented using the [zeroMQ](https://zeromq.org/) messaging library. Most popular Linux distribution have the library files in their respective repositories. For example on Linux, it can be installed with the `apt` package manager using the following command:

```sh
sudo apt install libzmq3-dev
```

For other platforms please see the official documentation for zeroMQ for installation instructions.

The python dependencies are available in the python package index, and can be installed using the official dependency manager for python; `pip`. 

```sh
pip install zmq termcolor
```

When running the python file, you have to specify 4 command line arguments, which has to be one of the the lines `bully_election/network.config`:
1. The host_ip
2. the server port
3. the publisher port
4. the unique id used in the bully election

An example of how to start a node could be:
```sh
  python bully_election.py 127.0.0.1 9000 9001 1
```


The C++ implementation for the improved version do not use external libraries, and should   be able to be built with any C++ compiler supporting the 2011 ISO standard or later. Simply run the `improved_bully_election/CMakeLists.txt` in your preferred way. NOTE the executable invocation requires one unsigned integer argument specifying the number of nodes in the network. So if you use an IDE like Visual Studio or CLion and you get an error when building and running the project this is the reason why. Instead find the executable and run it like e.g  `./improved_bully_election_dummy 10`.



## Testing

The python implementation `bully_election/bully_election.py` has two unit tests, which can be tested using the python testing framework [pytest](https://docs.pytest.org/en/latest/) with the command:

```sh
pytest bully_election/bully_election.py
```

The C++ implementation in the `improved_bully_election` has an added executable target in the `CMakeLists.txt`, which produces an executable file `testing`, which run unit tests for this version and prints a metric score.



## Credits

Inspiration for how to implement the networking part of the code using the zeroMQ library was taken from this public repository [Bully_algorithm](https://github.com/AhmedEssamDakrory/Bully_Algorithm) from github user [AhmedEssamDakrory](https://github.com/AhmedEssamDakrory).



## Authors

-   Kristoffer Plagborg Bak Sørensen
-   Alexander Stæhr Johansen
-   Jeppe Stjernholm Schildt
-   Liulihan Kuang
