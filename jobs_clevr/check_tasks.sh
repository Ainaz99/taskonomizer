#!/usr/bin/env bash

splits=('simple/train' 'simple/val' 'simple/test' 'complex/train' 'complex/val' 'complex/test')
# splits=('complex/train')

counts=(10000 1000 1000 50000 5000 5000)
tasks=('rgb' 'normal' 'reshading' 'depth_euclidean' 'depth_zbuffer' 'edge_occlusion' 'edge_texture' \
'keypoints2d' 'keypoints3d' 'segment_unsup2d' 'segment_unsup25d' 'principal_curvature' 'semantic')

base_path='/scratch-data/ainaz/clevr-taskonomized/clevr-taskonomy-'
save_base_path='/home/ainaz/Desktop/clevr/check/'

for i in {3..5}; do
    echo "${splits[$i]}"
    rm -rf $save_base_path"${splits[$i]}"
    mkdir $save_base_path"${splits[$i]}"
    for j in {0..2}; do
        point=$((RANDOM % ${counts[$i]}))
        echo $point
        for task in "${tasks[@]}"; do
            img_path=$base_path"${splits[$i]}/$task/point_${point}_view_0_domain_${task}.png"
            save_path=$save_base_path"${splits[$i]}/point_${point}_view_0_domain_${task}.png"
            kubectl cp ae-pod1:$img_path $save_path
        done
    done
done