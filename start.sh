#!/bin/bash

cd scripts && sudo ./clean_conf-orch.sh
cd .. && sudo python3 start_gunicorn.py