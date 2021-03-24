#!/usr/bin/env bash

# Passed arguments : model_path {args}*

# SCRIPT_PATH=${PWD}/scripts

current_path=${PWD}
model_path=$1
base_path=$(basename $model_path)

cd $model_path

# Clear the directory if it exists
rm -rf semantic

# Make it if it doesn't exist
mkdir -p semantic

# Get additional arguments
args="${@:2}"

# Generate semantic segmentation images

# blender -b --enable-autoexec -noaudio --python $SCRIPT_PATH/create_semantic_images_replica.py -- \
# MODEL_PATH=$model_path MODEL_FILE=mesh_semantic.ply $args

docker run --rm -v $current_path:/app/ \
                -v $model_path:/$base_path \
                ainaz99/multi-label-data:latest /bin/bash -c \
                "blender -b --enable-autoexec -noaudio --python /app/scripts/create_semantic_images_replica.py \
                 -- MODEL_PATH=/$base_path MODEL_FILE=mesh_semantic.ply $args"

