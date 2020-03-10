#!/bin/bash
git -C $1 fetch -q > /dev/null
git -C $1 pull -q > /dev/null
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

$DIR/update_peers.py --repo $1

