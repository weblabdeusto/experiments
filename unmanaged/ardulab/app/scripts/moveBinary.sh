#!/bin/bash

user_folder=$2
binary_folder="$4/app/static/binaries/"

ruta="$binary_folder$user_folder/"
echo $ruta

rm -r ${ruta}*
cp $4/app/workspace/.build/$1/firmware.hex ${ruta}/$3.hex
