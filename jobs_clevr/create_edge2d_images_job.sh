#!/usr/bin/env bash

# Passed arguments : model_path {args}*

SCRIPT_PATH=${PWD}/scripts
model_path=$1

cd $model_path

# Clear the directory if it exists
rm -rf edge_texture

# Make it if it doesn't exist
mkdir -p edge_texture

# Get additional arguments
args="${@:2}"

# Generate 2D edge images

for i in {0..50000}
do
    blender -b --enable-autoexec -noaudio --python $SCRIPT_PATH/create_edge_2d_images.py -- \
    MODEL_PATH=$model_path POINT=$i $args
done

