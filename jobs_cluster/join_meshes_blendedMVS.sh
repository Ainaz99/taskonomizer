#!/usr/bin/env bash

# Passed arguments : model_path {args}*

SCRIPT_PATH=${PWD}/scripts
model_path=$1

cd $model_path


# Get additional arguments
args="${@:2}"

blender -b --enable-autoexec -noaudio --python $SCRIPT_PATH/join_meshes_blendedMVS.py -- \
MODEL_PATH=$model_path $args
