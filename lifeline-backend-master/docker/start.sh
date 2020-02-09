#!/bin/bash

set -e

# while ! (timeout 3 bash -c "</dev/tcp/${DB_HOST}/${DB_PORT}") &> /dev/null;
# do
#     echo waiting for PostgreSQL to start...;
#     sleep 3;
# done;

./m makemigrations --merge  --no-input --traceback
./m migrate  --no-input --traceback
./m collectstatic --no-input --traceback
# ./m runserver 0.0.0.0:8000
