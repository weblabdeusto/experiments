#!/bin/bash

gunicorn --worker-class eventlet -w 2 app:app -b 0.0.0.0:8000
