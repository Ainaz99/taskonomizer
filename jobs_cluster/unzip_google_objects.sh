#!/usr/bin/env bash

##### unzip files
# cd zip
# for file in *.zip
# do  
#     directory="../unzip/${file%.zip}"
#     echo "$directory"
#     unzip "$file" -d "$directory"
# done
#####


##### move to habitat/data/objects and create json files
# obj_path="/scratch-data/ainaz/habitat-sim/data/objects/google_objects"
# cd ../unzip
# for file in *
# do  
#     mkdir -p "$obj_path/$file"
#     cp -r "$file/meshes/model.obj" "$obj_path/$file/$file.obj"
#     cp -r "$file/meshes/model.mtl" "$obj_path/$file/model.mtl"
#     cp -r "$file/materials/textures/texture.png" "$obj_path/$file/texture.png"

#     obj_file="$file.obj"
#     jq -n --arg obj_file "${obj_file}" \
#         '{"render mesh": $obj_file, "collision mesh": $obj_file, "mass": 0.5}' > \
#         "$obj_path/$file/$file.phys_properties.json"

# done
######

###### add objects to default.phys_scene_config.json
# {
#     "physics simulator": "bullet",
#     "timestep": 0.008,
#     "gravity": [0,-9.8,0],
#     "friction coefficient": 0.4,
#     "restitution coefficient": 0.1,
#     "rigid object paths":[
#         "objects/banana",
#         "objects/chefcan",
#         "objects/cheezit"
#     ]
# }

cd unzip

objs="objects/banana objects/chefcan objects/cheezit"

for file in *
do  
    objs+=" objects/google_objects/$file"

done

jq -n --arg objs "${objs}"\
    '{ "physics simulator": "bullet", "timestep": 0.01, "gravity": [0,-9.8,0], "friction coefficient": 0.6, "restitution coefficient": 0.1, "rigid object paths": $objs | split(" ") }' > \
        "../../habitat-sim/data/default.phys_scene_config.json"
######


###### save the list of all objects as json
# cd unzip
all_objs="chefcan cheezit"
for file in *
do  
    all_objs+=" $file"

done
jq -n --arg objs "${all_objs}"\
    '$objs | split(" ")' > "../list_of_objects.json"
######




