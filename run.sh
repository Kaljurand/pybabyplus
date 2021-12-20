#!/bin/bash

# TODO: convert this to Python

fileid=$1
filename="babyplus_data_export"
curl -L -o ${filename}.zip "https://drive.google.com/u/0/uc?export=download&id=${fileid}"

unzip -p babyplus_data_export.zip babyplus_data_export.json | jq | ./babyplus.py - | tee out.txt

cp ${filename}.xlsx ~/Desktop/
