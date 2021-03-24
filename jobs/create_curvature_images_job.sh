#!/usr/bin/env bash

# Passed arguments : model_path {args}*

current_path=${PWD}
model_path=$1
base_path=$(basename $model_path)

cd $model_path

# Clear the directory if it exists
rm -rf principal_curvature

# Make it if it doesn't exist
mkdir -p principal_curvature

# Get additional arguments
args="${@:2}"

# Generate curvature images

docker run --rm -v $current_path:/app/ \
                -v $model_path:/$base_path \
                ainaz99/multi-label-data:latest /bin/bash -c \
                "blender -b --enable-autoexec -noaudio --python /app/scripts/create_curvature_images.py \
                 -- MODEL_PATH=/$base_path MODEL_FILE=point_10_view_0_domain_obj.obj $args"
