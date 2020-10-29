#!/usr/bin/env bash

set -e

if [ ! -e "server.config" ]; then
    echo "the server.config was not found in the current directory"
    exit 1
fi

NODE_COUNT=$(wc --lines server.config | awk '{print $1}')

cat server.config | while read line; do
    # python bully_election.py $line
    echo $line
done
