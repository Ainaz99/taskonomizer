#!/usr/bin/env bash

# Passed arguments : model_path {args}*

SCRIPT_PATH=${PWD}/scripts
model_path=$1

cd $model_path

# Clear the directory if it exists
rm -rf rgb

# Make it if it doesn't
mkdir -p rgb

# Get additional arguments
args="${@:2}"

# Generate rgb images

python3 $SCRIPT_PATH/create_rgb_images_replica_google_objects.py -- \
MODEL_PATH=$model_path $args

