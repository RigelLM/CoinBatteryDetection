import cv2

import numpy as np

# x, y
# Upper left corner
MW_pos = [345, 350]
MW_size = [480, 285]

# Function to crop a video
# Return an array of frames if output is not None, else save the frames as a mp4 file to output and return None
def crop_video(input, output=None):

    cap = cv2.VideoCapture(input)

    if output:
        fps = cap.get(cv2.CAP_PROP_FPS)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output, fourcc, fps, (MW_size[0], MW_size[1]))
    else:
        frames = []

    while cap.isOpened():
        ret, frame = cap.read()
        if frame is None:
            break
        if ret:
            # y, x
            MW = frame[MW_pos[1]:MW_pos[1] + MW_size[1], MW_pos[0]:MW_pos[0] + MW_size[0]]
            MW = cv2.resize(MW, (MW_size[0], MW_size[1]))

            if output:
                out.write(MW)
            else:
                frames.append(MW)

    cap.release()

    if output:
        out.release()
        return None
    else:
        return frames

# Determine if the sensor display is on
# Receive pixel array or an image file path
def check_display(input):

    if isinstance(input, str):
        image = cv2.imread(input)
    else:
        image = input

    threshold = 50

    if image is None:
        print("Display image not found")
    else:
        MW = image[MW_pos[1]:MW_pos[1] + MW_size[1], MW_pos[0]:MW_pos[0] + MW_size[0]]
        MW = cv2.resize(MW, (MW_size[0], MW_size[1]))

        cv2.imwrite('1.jpg', MW)

        gray_image = cv2.cvtColor(MW, cv2.COLOR_BGR2GRAY)

        average_brightness = np.mean(gray_image)

        if average_brightness < threshold:
            return False
        else:
            return True

# Get the first frame of a video
# Return an array of pixels if output is not None, else save the image as a file to output and return None
def get_first_frame(input, output=None):
    cap = cv2.VideoCapture(input)

    while cap.isOpened():
        ret, frame = cap.read()
        if frame is None:
            break
        if ret:
            # y, x
            if output is None:
                return frame
            else:
                cv2.imwrite(output, frame)
                return None
            break
    cap.release()