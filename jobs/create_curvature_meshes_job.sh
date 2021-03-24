#!/usr/bin/env bash

# Passed arguments : model_path {args}*

current_path=${PWD}
model_path=$1
base_path=$(basename $model_path)

cd $model_path


# Get additional arguments
args="${@:2}"

# Generate curvature images

# docker run --rm -v $current_path:/app/ \
#                 -v $model_path:/$base_path \
#                 ainaz99/multi-label-data:latest /bin/bash -c \
#                 "python /app/scripts/create_curvature_meshes.py \
#                  -- MODEL_PATH=/$base_path $args"

docker run --rm -v $current_path:/app/ \
                -v $model_path:/$base_path \
                ainaz99/multi-label-data:latest /bin/bash -c \
                "python /app/scripts/create_curvature_meshes.py \
                 -- MODEL_PATH=/$base_path MODEL_FILE=point_2_view_0_domain_obj.obj $args"
