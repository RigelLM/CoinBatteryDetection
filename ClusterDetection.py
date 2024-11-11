import cv2
import numpy as np
from sklearn.cluster import DBSCAN
import math


def radius_from_area(size):
    return math.sqrt(size / math.pi)


# apply dbscan algorithm to a single frame, getting clusters' information
# return a dictionary with length 0 if no cluster detected
def detect_clusters_in_frame(low_hsv, high_hsv, frame, eps=5, min_samples=10, min_cluster_size=500):
    # Convert the image to HSV for better color separation
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Generate masks for red and blue
    hsv_mask = cv2.inRange(rgb_frame, low_hsv, high_hsv)

    # Get coordinates of red and blue pixels
    points = np.column_stack(np.where(hsv_mask > 0))

    cluster_info = {}

    # Perform clustering only if there are enough pixels
    if len(points) > 0:
        labels = DBSCAN(eps=eps, min_samples=min_samples).fit(points).labels_
        cluster_info = get_cluster_info(points, labels, min_cluster_size)

    return cluster_info


# Extract valid clusters' info from
def get_cluster_info(points, labels, min_cluster_size):
    clusters = {}
    for label in np.unique(labels):
        if label == -1:  # Noise points
            continue
        cluster_points = points[labels == label]

        # Check cluster size, keep clusters only if it's larger than the minimum cluster size
        if len(cluster_points) >= min_cluster_size:
            # Get the x, y coordinates of the cluster center
            avg_location = cluster_points.mean(axis=0)
            clusters[label] = {
                'size': len(cluster_points),
                'location': (int(avg_location[1]), int(avg_location[0]))  # (x, y)
            }
    return clusters


def visualize_clusters(color, image, clusters):
    # Draw clusters on the image
    for cluster_id, info in clusters.items():
        size = info['size']
        location = info['location']
        # Draw a circle at the cluster center
        color_ = (0, 0, 0)
        if color == 'red':
            color_ = (0, 0, 255)
        elif color == 'blue':
            color_ = (255, 0, 0)
        cv2.circle(image, location, int(radius_from_area(size)), color_, 2)
        # Annotate the cluster size
        cv2.putText(image, f'Size: {size}', (location[0] + 15, location[1]),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_, 2)

    # Display the result
    cv2.imshow('Cluster Visualization', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# Apply cluster algorithm to the whole video, with frames array as input
# Do not have to read video file in this func
def detect_frame_array(frames=[], r_eps=5, b_eps=5, r_samples=10, b_samples=10, r_size=120, b_size=200, a_eps=1,
                       a_samples=2):
    # Define RGB ranges for red and blue
    lower_red = np.array([158, 75, 75])
    upper_red = np.array([235, 123, 139])

    lower_blue = np.array([0, 61, 165])
    upper_blue = np.array([105, 194, 235])

    metal_frame = []
    ferrous_frame = []

    # Number of frames in total
    frame_count = len(frames)

    for frame in frames:
        # Clustering red pixels
        red_clusters = detect_clusters_in_frame(lower_red, upper_red, frame, eps=r_eps, min_samples=r_samples,
                                                min_cluster_size=r_size)

        for label, info in red_clusters.items():
            y = info['location'][1]
            # Get red clusters which appear in the top band area of the frame
            if y <= 240:
                # Discard clusters which appear in both ends of video
                if frame_count >= 5 & frame_count <= 80:
                    metal_frame.append(frame_count)

        # if red_clusters:
        #    print(f"Red Clusters: {red_clusters}, frame: {frame_count}")
        #    visualize_clusters('red', frame, red_clusters)

        # Clustering blue pixels
        blue_clusters = detect_clusters_in_frame(lower_blue, upper_blue, frame, eps=b_eps, min_samples=b_samples,
                                                 min_cluster_size=b_size)

        for label, info in blue_clusters.items():
            x = info['location'][0]
            y = info['location'][1]
            # Get blue clusters which appear in the right_bottom corner of the frame
            if y >= 240 & x >= 140:
                # Discard clusters which appear in both ends of video
                if frame_count >= 5 & frame_count <= 80:
                    ferrous_frame.append(frame_count)

        # if blue_clusters:
        #    print(f"Blue Clusters: {blue_clusters}, frame: {frame_count}")
        #    visualize_clusters('blue', frame, blue_clusters)

    # Apply cluster algorithm to the frame index array to see if clusters appear twice through the video
    metal_frame_array = np.array(metal_frame).reshape(-1, 1)
    ferrous_frame_array = np.array(ferrous_frame).reshape(-1, 1)

    dbscan = DBSCAN(eps=a_eps, min_samples=a_samples)

    metal_occurrence = ferrous_occurrence = 0

    if len(metal_frame_array) > 0:
        metal_clusters = set(dbscan.fit_predict(metal_frame_array))

        if -1 in metal_clusters:
            metal_clusters.remove(-1)

        metal_occurrence = len(metal_clusters)

    if len(ferrous_frame_array) > 0:
        ferrous_clusters = set(dbscan.fit_predict(ferrous_frame_array))

        if -1 in ferrous_clusters:
            ferrous_clusters.remove(-1)

        ferrous_occurrence = len(ferrous_clusters)

    if metal_occurrence >= 2:
        if ferrous_occurrence >= 2:
            return 'Battery'
        else:
            return 'Metal'
    else:
        return 'Empty'


# Apply cluster algorithm to the whole video, with file path as input
# Reading video file in this func
def detect(video_path, r_eps=5, b_eps=5, r_samples=10, b_samples=10, r_size=120, b_size=200, a_eps=1,
           a_samples=2):
    # Define RGB ranges for red and blue
    lower_red = np.array([158, 89, 90])
    upper_red = np.array([235, 123, 139])

    lower_blue = np.array([0, 61, 165])
    upper_blue = np.array([105, 194, 235])

    metal_frame = []
    ferrous_frame = []

    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    while cap.isOpened():

        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1

        red_clusters = detect_clusters_in_frame(lower_red, upper_red, frame, eps=r_eps, min_samples=r_samples,
                                                min_cluster_size=r_size)

        for label, info in red_clusters.items():
            y = info['location'][1]
            if y <= 240:
                if frame_count >= 5 & frame_count <= 80:
                    metal_frame.append(frame_count)

        if red_clusters:
            print(f"Red Clusters: {red_clusters}, frame: {frame_count}")
            visualize_clusters('red', frame, red_clusters)
        #

        blue_clusters = detect_clusters_in_frame(lower_blue, upper_blue, frame, eps=b_eps, min_samples=b_samples,
                                                 min_cluster_size=b_size)

        for label, info in blue_clusters.items():
            x = info['location'][0]
            y = info['location'][1]
            if y >= 240 & x >= 140:
                if frame_count >= 5 & frame_count <= 80:
                    ferrous_frame.append(frame_count)

        if blue_clusters:
            print(f"Blue Clusters: {blue_clusters}, frame: {frame_count}")
            visualize_clusters('blue', frame, blue_clusters)

    metal_frame_array = np.array(metal_frame).reshape(-1, 1)
    ferrous_frame_array = np.array(ferrous_frame).reshape(-1, 1)

    dbscan = DBSCAN(eps=a_eps, min_samples=a_samples)

    metal_occurrence = ferrous_occurrence = 0

    if len(metal_frame_array) > 0:
        metal_clusters = set(dbscan.fit_predict(metal_frame_array))

        if -1 in metal_clusters:
            metal_clusters.remove(-1)

        metal_occurrence = len(metal_clusters)

    if len(ferrous_frame_array) > 0:
        ferrous_clusters = set(dbscan.fit_predict(ferrous_frame_array))

        if -1 in ferrous_clusters:
            ferrous_clusters.remove(-1)

        ferrous_occurrence = len(ferrous_clusters)

    cap.release()

    if metal_occurrence >= 2:
        if ferrous_occurrence >= 2:
            return 'Battery'
        else:
            return 'Metal'
    else:
        return 'Empty'
