import pymeshlab as ml
import os

from load_settings import settings


scriptpath = os.path.dirname(__file__)
basepath = settings.MODEL_PATH

def main():
    if settings.CLEVR:
        settings.MODEL_FILE = 'point_{}_view_{}_domain_obj.ply'.format(settings.POINT, 0)
        model_fpath = os.path.join(basepath, 'ply', settings.MODEL_FILE)
        os.makedirs(os.path.join(basepath, 'curvature_meshes'), exist_ok=True)
        k1_fpath = os.path.join(basepath, 'curvature_meshes', settings.MODEL_FILE).replace(".", "_k1.")
        k2_fpath = os.path.join(basepath, 'curvature_meshes', settings.MODEL_FILE).replace(".", "_k2.")
        
    else:
        model_fpath = os.path.join(basepath, settings.MODEL_FILE)
        k1_fpath = model_fpath.replace(".", "_k1.").replace("obj", "ply")
        k2_fpath = model_fpath.replace(".", "_k2.").replace("obj", "ply")


    ms = ml.MeshSet()

    # K1 Curvature
    ms.load_new_mesh(model_fpath) 
    # ms.apply_filter('re_compute_face_normals')
    # ms.apply_filter('re_compute_per_polygon_face_normals') 
    # ms.apply_filter('re_orient_all_faces_coherentely')
    print("normals recomputed...")
    ms.apply_filter('normalize_face_normals')
    ms.apply_filter('normalize_vertex_normals')
    ms.apply_filter('colorize_curvature_apss', 
                    filterscale=settings.FILTER_SCALE, 
                    maxprojectioniters=settings.MAX_PROJ_ITERS,
                    curvaturetype='K1')

    # ms.load_filter_script(os.path.join(scriptpath, settings.K1_MESHLAB_SCRIPT))
    # ms.apply_filter_script()

    ms.save_current_mesh(k1_fpath)

    # K2 Curvature
    ms.load_new_mesh(model_fpath)
    # ms.apply_filter('re_compute_face_normals')
    # ms.apply_filter('re_compute_per_polygon_face_normals') 
    # ms.apply_filter('re_orient_all_faces_coherentely')
    print("normals recomputed...")
    ms.apply_filter('normalize_face_normals')
    ms.apply_filter('normalize_vertex_normals')
    ms.apply_filter('colorize_curvature_apss', 
                    filterscale=settings.FILTER_SCALE, 
                    maxprojectioniters=settings.MAX_PROJ_ITERS,
                    curvaturetype='K2')

    # ms.load_filter_script(os.path.join(scriptpath, settings.K2_MESHLAB_SCRIPT))
    # ms.apply_filter_script()

    ms.save_current_mesh(k2_fpath)
    

if __name__ == "__main__":
    
    main()