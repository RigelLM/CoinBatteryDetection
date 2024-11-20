import cv2
from sklearn.cluster import DBSCAN
import numpy as np

inside_radius = 17

green_threshold = 52

percent_threshold_half = 0.6237513873473918

percent_threshold_third = 0.41583425823159453

def circle_from_frame(frame, minR, maxR):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=maxR * 1.5, param1=50, param2=30, minRadius=minR, maxRadius=maxR)

    if circles is not None:
        target = circles[0][0]
        target = np.uint16(np.around(target))

        mask = np.zeros(frame.shape[:2], dtype=np.uint8)

        cv2.circle(mask, (target[0], target[1]), inside_radius, 255, -1)

        return frame[mask > 0]
    else:
        return None

def visualize_circle(frame, minR, maxR):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=maxR * 1.5, param1=50, param2=30, minRadius=minR, maxRadius=maxR)

    if circles is not None:
        target = circles[0][0]
        target = np.uint16(np.around(target))

        mask = np.zeros(frame.shape[:2], dtype=np.uint8)

        cv2.circle(mask, (target[0], target[1]), inside_radius, 255, -1)

        return cv2.bitwise_and(frame, frame, mask=mask)
    else:
        return None

def detect_twice(array):
    occurrence = 0
    frame_array = np.array(array).reshape(-1, 1)

    dbscan = DBSCAN(eps=1, min_samples=2)


    if len(frame_array) > 0:
        clusters = set(dbscan.fit_predict(frame_array))

        if -1 in clusters:
            clusters.remove(-1)

        occurrence = len(clusters)

    return occurrence

def detect_metal(video_path):
    target_frames = []
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    while cap.isOpened():

        ret, frame = cap.read()

        if not ret:
            break

        frame = frame[:240, :]

        pixels = circle_from_frame(frame, 10, 25)

        p = visualize_circle(frame, 10, 25)

        if pixels is not None:
            green_values = 255 - pixels[:, 1] # (B=0, G=1, R=2)

            target_pixels = green_values[green_values > green_threshold]

            if len(target_pixels) / len(green_values) > percent_threshold_third:
                target_frames.append(frame_count)
                cv2.imshow("target", p)
                cv2.waitKey(0)
        frame_count += 1

    cap.release()
    return target_frames