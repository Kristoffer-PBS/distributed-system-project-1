# distributed-system-project-1
repo for project 1 in distributed systems 2020 about leader election algorithms 



## Asumptions
* Each process has an unique ID
* Processes know each other's process ID
* Processes do not know which ones are currently alive
* Each process can compare IDs (e.g. to find the highest)
* All processes can intercommunicate
* A failed process is always detectable
* Any process can initiate an election
* Upon failure recovery, the process knows it failed 