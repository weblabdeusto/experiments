#!/bin/bash

user_folder=$1
uploads_folder="$2/app/static/uploads/"

ruta="$uploads_folder$user_folder/*"
echo ${ruta}
rm -r $2/app/workspace/src/*
cp ${ruta} $2/app/workspace/src/
