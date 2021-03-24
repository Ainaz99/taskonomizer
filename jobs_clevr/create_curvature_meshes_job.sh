#!/usr/bin/env bash

# Passed arguments : model_path {args}*

SCRIPT_PATH=${PWD}/scripts
model_path=$1

cd $model_path

# Get additional arguments
args="${@:2}"

# Generate curvature images

for i in {0..50000}
do
    python $SCRIPT_PATH/create_curvature_meshes.py -- MODEL_PATH=$model_path POINT=$i $args
done