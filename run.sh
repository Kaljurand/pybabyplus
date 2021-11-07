#!/bin/bash

fileid=$1
filename="babyplus_data_export"
curl -L -o ${filename}.zip "https://drive.google.com/u/0/uc?export=download&id=${fileid}"

unzip ${filename}.zip
cat ${filename}.json | ./babyplus.py
cp ${filename}.xlsx ~/Desktop/
