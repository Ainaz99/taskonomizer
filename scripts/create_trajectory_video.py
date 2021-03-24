import cv2
import os
from load_settings import settings
from PIL import Image

TASK = 'normal'

basepath = settings.MODEL_PATH
image_folder = os.path.join(basepath, TASK)

video_name = os.path.join(basepath, f'video_{TASK}.mkv')

# images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
points = []
for img in os.listdir(image_folder):
    points.append(int(img.split('_')[1]))

# images.sort()
# images = images[1:]
points.sort()
points = points[1:]
frame = cv2.imread(os.path.join(image_folder, f'point_{points[0]}_view_0_domain_{TASK}.png'))
height, width, layers = frame.shape

video = cv2.VideoWriter(video_name, 0, 1, (width, height))

for point in points:
    # print(f'point_{point}_view_0_domain_{TASK}.png')
    print(point)
    video.write(cv2.imread(os.path.join(image_folder, f'point_{point}_view_0_domain_{TASK}.png')))

cv2.destroyAllWindows()
video.release()
