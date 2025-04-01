#!/bin/bash
# start.sh

python3 post_server/p_db.py &

python3 post_server/post_server.py

# wait