#!/bin/bash

CURDIR=$PWD

cd ../venv/socket

#pwd
source bin/activate socket
cd $CURDIR
#pwd

echo "Calling pylint ..."
pylint ccc_server --msg-template="{msg}: {msg_id}:{abspath}:{line}:" --max-line-length=120 --disable=W1202