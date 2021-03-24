#!/usr/bin/env bash

# Passed arguments : model_path {args}*

SCRIPT_PATH=${PWD}/scripts
model_path=$1

cd $model_path

# Clear the directory if it exists
# rm -rf depth_euclidean

# Make it if it doesn't
# mkdir -p depth_euclidean

# Get additional arguments
args="${@:2}"

# Generate depth euclidean images
for i in {0..50000}
do
    FILE=depth_euclidean/point_${i}_view_0_domain_depth_euclidean.png
    if test -f "$FILE"; then
        continue
    fi
    echo "$FILE does not exist. Point : ${i}"
    blender -b --enable-autoexec -noaudio --python $SCRIPT_PATH/create_depth_euclidean_images.py -- \
    MODEL_PATH=$model_path POINT=$i $args
done

