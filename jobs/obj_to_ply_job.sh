#!/usr/bin/env bash

# Passed arguments : model_path {args}*

current_path=${PWD}
model_path=$1
base_path=$(basename $model_path)

cd $model_path

# Get additional arguments
args="${@:2}"

# Generate glb from obj
docker run --rm -v $current_path:/app/ \
                -v $model_path:/$base_path \
                ainaz99/multi-label-data:latest /bin/bash -c \
                "blender -b --enable-autoexec -noaudio --python /app/scripts/obj_to_ply.py -- \
                MODEL_PATH=/$base_path MODEL_FILE=scene.obj $args"
