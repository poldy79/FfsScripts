#!/bin/bash
git -C $1 pull > /dev/null
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

$DIR/update_peers.py --repo $1

