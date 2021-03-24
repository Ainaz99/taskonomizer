project_path=/scratch-data/ainaz/multi-label-data
file_path=$project_path/scripts/create_semantic_images_3DSceneGraph.py
sceneGraph_path=/scratch-data/ainaz/3DSceneGraph_medium/automated_graph
taskonomy_path=/taskonomy-data/taskonomydata
taskonomy_v2_path=/scratch-data/ainaz/taskonomydata_v2

# Passed arguments :  with  {args}*
if [ $# -ge 2 ]; then
  args="${@:2}"
else
  args=""
fi


# list of models in the tiny Gibson split
tiny_models='Allensville Beechwood Benevolence Coffeen Collierville Corozal
Cosmos Darden Forkland Hanson Hiteman Ihlen Klickitat Lakeville Leonardo
Lindenwood Markleeville Marstons McDade Merom Mifflinburg Muleshoe Newfields
Noxapater Onaga Pinesdale Pomaria Ranchester Shelbyville Stockman Tolstoy Uvalda Wainscott Wiconisco Woodbine'

models='Broseley Bautista Cottonport Duarte Frankfort German Goffs Goodyear Maugansville Neibert Neshkoro Sweatman Thrall
Victorville Willow Winooski'

# list of models in the medium Gibson split
medium_models='Adairsville Airport Albertville Anaheim Ancor Andover Annona
Arkansaw Athens Bautista Bohemia Bonesteel Bonnie Brinnon Broseley Brown Browntown
 Byers Castor Cauthron Chilhowie Churchton Clairton Cochranton Cottonport Couderay
 Cousins Darrtown Donaldson Duarte Eagan Edson Emmaus Frankfort German Globe Goffs
 Goodfield Goodwine Goodyear Gravelly Hainesburg Helton Highspire Hildebran Hillsdale
 Hominy Hordville Hortense Irvine Kemblesville Kobuk Losantville Lynchburg Maida Marland
 Martinville Maugansville Micanopy Musicks Natural Neibert Neshkoro Newcomb Nuevo Oyens
 Pablo Pamelia Parole Pearce Pittsburg Poipu Potterville Readsboro Rockport Rogue Rosser
 Sands Scioto Shelbiana Silas Soldier Southfield Springerville Stilwell Sugarville Sunshine
 Sussex Sweatman Swisshome Swormville Thrall Tilghmanton Timberon Tokeland Touhy Tyler
 Victorville Waipahu Wando Westfield Willow Wilseyville Winooski Wyldwood'


my_model='German'
#iterate over models. Choose: tiny_models for tiny split or medium_models for medium split


for model in $models; do
    echo "___________ Building : $model ___________"
    model_lower=$(tr '[A-Z]' '[a-z]' <<< $model)
#    point_tar_file="${model_lower}_point_info.tar"
#    point_file="${model_lower}_point_info"
#    tar -xf $taskonomy_path/$point_tar_file -C $taskonomy_v2_path/points
#    mv $taskonomy_v2_path/points/point_info $taskonomy_v2_path/points/$point_file
    blender -b --enable-autoexec -noaudio --python $file_path -- MODEL_NAME=$model CAMERA_POSE_FILE='camera_poses.csv'
done

