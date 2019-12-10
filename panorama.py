import sys
import cv2
import numpy as np

if __name__=='__main__':
    # Create SIFT object
    sift = cv2.xfeatures2d.SIFT_create()

    # Create Flann Matcher Object
    flann = cv2.FlannBasedMatcher(dict(algorithm = 0, trees = 5), dict(checks = 50))

    # Gets list of image files from arguments
    files = sys.argv[1:]

    # Read all the images
    images = []
    for file in files:
        image = cv2.imread(file, 1)
        # image = cv2.resize(image, (0,0), None, 0.25, 0.25)
        images.append(image)

    # Initially, the panorama consists of the first image...
    current = images[0]
    # ... then, other images are progressively added.
    for i in range(1,len(images)):
        # Extract keypoints in the current panorama using SIFT
        current_keypoints, current_descriptors = sift.detectAndCompute(current, None)
        # Extract keypoints in the next image to be added using SIFT
        next_keypoints, next_descriptors = sift.detectAndCompute(images[i], None)

        # Finds matches between the current panorama and the next image using the
        # FLANN Matcher
        matches = flann.knnMatch(current_descriptors, next_descriptors, k=2)

        # Filter out bad matches using Lowe's ratio test
        good_matches = []
        for m1,m2 in matches:
            if m1.distance < 0.7*m2.distance:
                good_matches.append(m1)

        # Generates points to be used on finding the homography
        current_points = np.float32([current_keypoints[good_match.queryIdx].pt for \
                                     good_match in good_matches]).reshape(-1,1,2)
        next_points = np.float32([next_keypoints[good_match.trainIdx].pt for \
                                  good_match in good_matches]).reshape(-1,1,2)

        # Find homography between the two images
        M, mask = cv2.findHomography(next_points,current_points, cv2.RANSAC, 5.0)

        # Finds the translation needed to apply over the orignal image using the
        # homography matrix
        rows_current, cols_current = current.shape[:2]
        rows_next, cols_next = images[i].shape[:2]
        list_of_points_current = np.float32([[0,0], [0,rows_current], \
                                             [cols_current,rows_current],\
                                             [cols_current,0]]).reshape(-1,1,2)
        temp_points = np.float32([[0,0], [0,rows_next], [cols_next,rows_next], \
                                  [cols_next,0]]).reshape(-1,1,2)
        list_of_points_next = cv2.perspectiveTransform(temp_points, M)
        list_of_points = np.concatenate((list_of_points_current, list_of_points_next), axis=0)
        [x_min, y_min] = np.int32(list_of_points.min(axis=0).ravel() - 0.5)
        [x_max, y_max] = np.int32(list_of_points.max(axis=0).ravel() + 0.5)
        translation_dist = [-x_min, -y_min]
        M_translation = np.array([[1, 0, translation_dist[0]], \
                                  [0, 1, translation_dist[1]], [0,0,1]])

        # Adds perspective to the next image
        result = cv2.warpPerspective(images[i], M_translation.dot(M), \
                                     (x_max-x_min, y_max-y_min))

        # Place original image over the next image with perspective applied
        for i in range(translation_dist[1],rows_current+translation_dist[1]):
            for j in range(translation_dist[0],cols_current+translation_dist[0]):
                if all(current[i-translation_dist[1],j-translation_dist[0]] != [0,0,0]):
                    result[i,j] = current[i-translation_dist[1],j-translation_dist[0]]
        current = result

    # When no more images are left to add...
    # ... removes black background
    current = cv2.cvtColor(current, cv2.COLOR_RGB2RGBA)
    current[np.all(current == [0, 0, 0, 255], axis=2)] = [0, 0, 0, 0]
    # ... export the final result
    cv2.imwrite("panorama.png", current)