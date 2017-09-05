#!/bin/bash

cd scripts && ./clean_conf-orch.sh
cd .. && sudo python3 start_gunicorn.py
