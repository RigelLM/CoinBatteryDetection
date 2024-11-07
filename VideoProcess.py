import os

import cv2

# Function to process a single video
def process_video(input_path, output_path):
    MW_pos = [350, 345]
    MW_size = [480, 285]

    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (MW_size[0], MW_size[1]))

    while cap.isOpened():
        ret, frame = cap.read()
        if frame is None:
            break
        if ret:
            MW = frame[MW_pos[0]:MW_pos[0] + MW_size[1], MW_pos[1]:MW_pos[1] + MW_size[0]]
            MW = cv2.resize(MW, (MW_size[0], MW_size[1]))
            out.write(MW)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    out.release()


def get_frames(input_path):
    frames = []
    MW_pos = [350, 345]
    MW_size = [480, 285]

    cap = cv2.VideoCapture(input_path)

    while cap.isOpened():
        ret, frame = cap.read()
        if frame is None:
            break
        if ret:
            MW = frame[MW_pos[0]:MW_pos[0] + MW_size[1], MW_pos[1]:MW_pos[1] + MW_size[0]]
            MW = cv2.resize(MW, (MW_size[0], MW_size[1]))

            frames.append(MW)

    cap.release()
    return frames
