project_path=/scratch-data/ainaz/multi-label-data
file_path=$project_path/scripts/create_semantic_cubemap_3DSceneGraph.py
sceneGraph_path=/scratch-data/ainaz/3DSceneGraph_tiny/automated_graph
taskonomy_path=/scratch-data/ainaz/taskonomydata_v2/tiny_split


# list of models in the tiny Gibson split
tiny_models='Allensville Beechwood Benevolence Coffeen Collierville Corozal
Cosmos Darden Forkland Hanson Hiteman Ihlen Klickitat Lakeville Leonardo
Lindenwood Markleeville Marstons McDade Merom Mifflinburg Muleshoe Newfields
Noxapater Onaga Pinesdale Pomaria Ranchester Shelbyville Stockman Tolstoy Uvalda Wainscott Wiconisco Woodbine'
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

my_model='Allensville'
#iterate over models. Choose: tiny_models for tiny split or medium_models for medium split
for model in $tiny_models; do
    echo "___________ Building : $model ___________"
    python3  $file_path --model $model \
                    --sceneGraph_data_path $sceneGraph_path \
                    --taskonomy_data_path $taskonomy_path
done
