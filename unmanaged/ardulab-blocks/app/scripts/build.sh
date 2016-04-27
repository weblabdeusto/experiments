#!/bin/bash
# build arduino project

cd $2/app/workspace
#rm .build/uno/firmware.hex
#rm .build/uno/firmware.elf
rm -r .build
ino build -m $1

