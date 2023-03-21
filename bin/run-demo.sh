#!/usr/bin/env bash
poetry run python -m ocppdemo &
sleep 3
poetry run python client.py
