import cv2
import os
import numpy as np

# path = '/home/ainaz/Desktop/CARLA/episode_0000'
path = '/scratch-data/ainaz/carla_outputs/episode_0000'

os.makedirs(os.path.join(path, 'all'))

for i, img_name in enumerate(os.listdir(os.path.join(path, 'rgb'))):
    name = img_name[:-7]
    rgb = cv2.imread(os.path.join(path, 'rgb', img_name))
    semantic = cv2.imread(os.path.join(path, 'semantic', name + 'semantic.png'))
    depth_zbuffer = cv2.imread(os.path.join(path, 'depth_zbuffer', name + 'depth_zbuffer.png'))
    segment_unsup2d = cv2.imread(os.path.join(path, 'segment_unsup2d', name + 'segment_unsup2d.png'))
    keypoints3d = cv2.imread(os.path.join(path, 'keypoints3d', name + 'keypoints3d.png'))
    edge_texture = cv2.imread(os.path.join(path, 'edge_texture', name + 'edge_texture.png'))
    edge_occlusion = cv2.imread(os.path.join(path, 'edge_occlusion', name + 'edge_occlusion.png'))
    keypoints2d = cv2.imread(os.path.join(path, 'keypoints2d', name + 'keypoints2d.png'))

    row1 = np.concatenate([rgb, semantic, depth_zbuffer, segment_unsup2d], axis=1)
    row2 = np.concatenate([keypoints3d, edge_texture, edge_occlusion, keypoints2d], axis=1)
    all = np.concatenate([row1, row2], axis=0)
    cv2.imwrite(os.path.join(path, 'all', img_name[:-15] + '.png'), all)


video_name = os.path.join(path, 'video.mkv')
# image_folder = path
image_folder = os.path.join(path, 'all')

images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
images.sort()
images = images[1:]
frame = cv2.imread(os.path.join(image_folder, images[0]))
height, width, layers = frame.shape

video = cv2.VideoWriter(video_name, 0, 1, (width, height))

for image in images:
    print(image)
    video.write(cv2.imread(os.path.join(image_folder, image)))

cv2.destroyAllWindows()
video.release()