#!/usr/bin/env bash

# Passed arguments : model_path {args}*

SCRIPT_PATH=${PWD}/scripts
model_path=$1

cd $model_path

# Clear the directory if it exists
# rm -rf normal

# Make it if it doesn't exist
# mkdir -p normal

# Get additional arguments
args="${@:2}"

# Generate normal images

for i in {0..50000}
do
   FILE=normal/point_${i}_view_0_domain_normal.png
   if test -f "$FILE"; then
      continue
   fi
   echo "$FILE does not exist. Point : ${i}"
   blender -b --enable-autoexec -noaudio --python $SCRIPT_PATH/create_normal_images.py -- \
   MODEL_PATH=$model_path POINT=$i $args
done

