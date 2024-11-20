import os
import sys

import CircleDetection

if len(sys.argv) > 1:
    folder_path = str(sys.argv[1])

for root, dirs, files in os.walk(folder_path):
    for file in files:
        if file.lower().endswith('.mp4'):
            video_path = os.path.join(root, file)

            result = CircleDetection.detect_metal(video_path)

            print(video_path)
            print(result)
            print(CircleDetection.detect_twice(result))