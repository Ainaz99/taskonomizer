#!/usr/bin/env bash

# Passed arguments : model_path {args}*

current_path=${PWD}
model_path=$1
base_path=$(basename $model_path)

cd $model_path

# Clear the directory if it exists
rm -rf segment_unsup2d

# Make it if it doesn't exist
mkdir -p segment_unsup2d

# Get additional arguments
args="${@:2}"

# Generate segment 2D images

docker run --rm -v $current_path:/app/ \
                -v $model_path:/$base_path \
                ainaz99/multi-label-data:latest /bin/bash -c \
                "blender -b --enable-autoexec -noaudio --python /app/scripts/create_segmentation_2d_images.py \
                 -- MODEL_PATH=/$base_path $args"
