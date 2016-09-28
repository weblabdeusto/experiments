#!/bin/bash

gunicorn --worker-class eventlet -w 1 app:app -b 0.0.0.0:8000
