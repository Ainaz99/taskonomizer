from PIL import Image, ImageChops
import os
import numpy as np
import cv2
from matplotlib.image import imread
from shutil import copyfile

tasks = ['normal', 'reshading', 'edge_texture', 'edge_occlusion', 'keypoints2d', 'keypoints3d', 'depth_euclidean', 'depth_zbuffer', 'segment_unsup2d', 'segment_unsup25d']

for task_name in tasks:
    print("______ task name : {} ____".format(task_name))
    # my_path = os.path.join('/scratch-data/ainaz/Onaga/mine', task_name)
    my_path = os.path.join('/home/ainaz/Desktop/EPFL/multi-label-data/test_model/8BCmnUrojRt', task_name)
    # orig_path = os.path.join('/scratch-data/ainaz/Onaga/', task_name)
    orig_path = os.path.join('/home/ainaz/Desktop/EPFL/multi-label-data/test_model/8BCmnUrojRt/onaga_taskonomy_orig/', task_name)
    # diff_path = os.path.join(orig_path, '..', task_name + '_diff')

    # if not os.path.exists(diff_path):
    #     os.makedirs(diff_path)


    avg_pixel_val_diff = 0
    max_pixel_val_diff = 0
    avg_num_of_different_pixels = 0

    for i, img_name in enumerate(os.listdir(my_path)):
        if img_name not in os.listdir(orig_path):
            print("!! {} : {} not in original folder.".format(i, img_name))
            continue
        mine = cv2.imread(my_path + '/' + img_name, -1)
        orig = cv2.imread(orig_path + '/' + img_name, -1)
        diff = cv2.absdiff(mine, orig)
        if i == 1:
            print(mine.dtype, orig.dtype)

        # cv2.imwrite(os.path.join(diff_path, img_name), 200 * (diff > 0))
        # print(img_name)
        # if i < 5:
        #     print(mine.dtype, orig.dtype)
        #     print("mine : max = {}, mean = {}, shape = {}".format(mine.max(), mine.mean(), mine.shape))
        #     print("orig : max = {}, mean = {}, shape = {}".format(orig.max(), orig.mean(), orig.shape))


        ###### statistics
        mean_pixel_val_diff = diff.mean()
        num_of_different_pixels = len(diff[np.nonzero(diff)])

        avg_pixel_val_diff += mean_pixel_val_diff
        avg_num_of_different_pixels += num_of_different_pixels
        max_pixel_val_diff = max(max_pixel_val_diff, diff.max())

        # if i < 5:
        #     print(i, " : diff = ", diff[np.nonzero(diff)], " - sum = ", diff.sum(),
        #         " - avg = ", mean_pixel_val_diff, " - max = ", diff.max())

    print("Avg pixel value difference for {} images : {}".format(i + 1, avg_pixel_val_diff / (i + 1)))
    print("Avg number of different pixels for {} images : {}".format(i + 1, avg_num_of_different_pixels / (i + 1)))
    print("Max pixel value difference for {} images : {}".format(i + 1, max_pixel_val_diff))

############################## Save image
# rgb_orig_path = os.path.join(os.getcwd(), '..', 'test_model', '8BCmnUrojRt', 'onaga_taskonomy_orig', 'rgb')
# rgb_mine_path = os.path.join(os.getcwd(), '..', 'test_model', '8BCmnUrojRt', 'rgb')
# rgb_diff_path = os.path.join(os.getcwd(), '..', 'test_model', '8BCmnUrojRt', 'onaga_taskonomy_orig', 'rgb_diff')
# curv_orig_path = os.path.join(os.getcwd(), '..', 'test_model', '8BCmnUrojRt', 'onaga_taskonomy_orig',
#                               'principal_curvature')
# curv_mine_path = os.path.join(os.getcwd(), '..', 'test_model', '8BCmnUrojRt', 'principal_curvature')
# curv_diff_path = os.path.join(os.getcwd(), '..', 'test_model', '8BCmnUrojRt', 'onaga_taskonomy_orig',
#                               'principal_curvature_diff')
# save_path = os.path.join(os.getcwd(), os.getcwd(), '..', 'test_model', '8BCmnUrojRt', 'onaga_taskonomy_orig', 'viz')
#
#
# for i, rgb_name in enumerate(os.listdir(rgb_mine_path)):
#     rgb_orig = cv2.imread(rgb_orig_path + '/' + rgb_name)
#     rgb_mine = cv2.imread(rgb_mine_path + '/' + rgb_name)
#     rgb_diff = cv2.imread(rgb_diff_path + '/' + rgb_name)
#     rgb = np.concatenate([rgb_orig, rgb_mine, rgb_diff], axis=1)
#     name = rgb_name[:-8]
#
#     curv_name = name + '_principal_curvature.png'
#     if curv_name not in os.listdir(curv_mine_path):
#         continue
#     print("!!!!! ", rgb_name, curv_name, name)
#     curv_orig = cv2.imread(os.path.join(curv_orig_path, curv_name))
#     curv_mine = cv2.imread(os.path.join(curv_mine_path, curv_name))
#     curv_diff = cv2.imread(os.path.join(curv_diff_path, curv_name))
#     curv = np.concatenate([curv_orig, curv_mine, curv_diff], axis=1)
#
#     img = np.concatenate([rgb, curv], axis=0)
#     cv2.imwrite(os.path.join(save_path, name + '.png'), img)
#
############################################### Replica


# save_path = '/home/ainaz/Desktop/all'
#
# l = ['point_0_view_0_domain_', 'point_0_view_1_domain_', 'point_1_view_0_domain_', 'point_1_view_1_domain_',
#      'point_1_view_2_domain_', 'point_3_view_0_domain_', 'point_3_view_1_domain_', 'point_9_view_1_domain_']
#
# for i, img_name in enumerate(l):
#     normal = cv2.imread(os.path.join(save_path, img_name + 'normal.png'))
#     rgb = cv2.imread(os.path.join(save_path, img_name + 'rgb.png'))
#     key = cv2.imread(os.path.join(save_path, img_name + 'keypoints3d.png'))
#     semantic = cv2.imread(os.path.join(save_path, img_name + 'semantic.png'))
#
#     # row1 = np.concatenate([normal, reshade], axis=1)
#     name = img_name[:-1]
#
#     # row2 = np.concatenate([key, semantic], axis=1)
#
#     img = np.concatenate([normal, rgb], axis=0)
#     img = 0.9 * rgb + 0.1 * normal
#     cv2.imwrite(os.path.join(save_path, name + '.png'), img)

##############################################

# path = '/home/ainaz/Desktop/ap2'
# copy_path = '/home/ainaz/Desktop/ap2_copy'
# count = 0
# for img_name in os.listdir(path):
#     # if img_name.__contains__('view_20') or img_name.__contains__('view_19') or img_name.__contains__('view_18')\
#     #         or img_name.__contains__('view_17') or img_name.__contains__('view_16') or img_name.__contains__('view_15')\
#     #         or img_name.__contains__('view_14') or img_name.__contains__('view_13') or img_name.__contains__('view_12')\
#     #         or img_name.__contains__('view_11') or img_name.__contains__('view_21') or img_name.__contains__('view_22'):
#     #     continue
#     # if img_name.startswith('point_9') or img_name.startswith('point_8') or img_name.startswith('point_7') or img_name.startswith('point_6') or img_name.startswith('point_5') or img_name.startswith('point_4') or img_name.startswith('point_3'):
#     #     continue
#     # if img_name.startswith('point_25') or img_name.startswith('point_26') or img_name.startswith('point_27') or img_name.startswith('point_28') or img_name.startswith('point_29'):
#     #     continue
#     #
#     # if img_name.startswith('point_16') or img_name.startswith('point_17') or img_name.startswith('point_18') or img_name.startswith('point_19'):
#     #     continue

#     if img_name.endswith('rgb.png'):
#         # name = img_name[:-12]
#         # print("!!!!! ", name)
#         # rgb_name = name + 'rgb.png'
#         # normal_name = name + 'normal.png'
#         # if rgb_name in os.listdir(path) and normal_name in os.listdir(path):
#         #     count += 1
#         #     src = os.path.join(path, img_name)
#         #     dst = os.path.join(copy_path, img_name)
#         #     copyfile(src, dst)
#         #
#         #     src = os.path.join(path, rgb_name)
#         #     dst = os.path.join(copy_path, rgb_name)
#         #     copyfile(src, dst)
#         #
#         #     src = os.path.join(path, normal_name)
#         #     dst = os.path.join(copy_path, normal_name)
#         #     copyfile(src, dst)

#         src = os.path.join(path, img_name)
#         dst = os.path.join(copy_path, img_name)
#         copyfile(src, dst)

# print(count)


