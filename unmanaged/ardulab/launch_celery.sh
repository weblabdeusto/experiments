#!/bin/bash

celery worker -A app.celery --loglevel=info --concurrency=1
