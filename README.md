# Panoramic Image Stitcher

This project demonstrates a method to stitch multiple images with overlapping sections into a panoramic one using the OpenCV library in Python. The developed algorithm is based on the SIFT feature extraction.

## Usage

	python panorama.py demo/in1.jpg demo/in2.jpg demo/in3.jpg

## Methodology

The panoramic image building process consists of five main steps: feature extraction using SIFT, feature matching between two images, elimination of bad matches, homography finding and stitching. The process is then repeated to add more images to the panorama. The following three pictures will be used as an example.

![](https://raw.githubusercontent.com/guilhermetiaki/panorama/master/demo/in.jpg)

To avoid too much information, steps will be illustrated using small sections of the first two pictures.

![](https://raw.githubusercontent.com/guilhermetiaki/panorama/master/demo/1-slices.jpg)

The first major step, features detection is performed using the SIFT algorithm, proposed by Lowe, and implemented by the SIFT class in OpenCV.

![](https://raw.githubusercontent.com/guilhermetiaki/panorama/master/demo/2-keypoints.jpg)
Keypoints found by the algorithm

Following to the matching process. The keypoint match is done using the FLANN - Fast Library for Approximate Nearest Neighbors – matcher, proposed by Muja. As suggested in its name, this algorithm provides an approximation. While it does not provide optimal matches, it performs faster than brute force. In OpenCV, this algorithm is implemented by the FlannBasedMatcher class.

![](https://raw.githubusercontent.com/guilhermetiaki/panorama/master/demo/3-matches.jpg)
Result of the matching process.

As many of the returned matches are false matches, they must be filtered. The left side of the last image, as well as the right side of the right image, do not overlap, and therefore ideally shouldn’t have any matches. Moreover, both images have approximately the same orientation, therefore diagonal matches also shouldn’t exist. Matches filtering can be performed using the ratio test proposed by Lowe. Virtually all matches in the left side of the left image were eliminated. A few false matches remained on the right side of the right image and some diagonal ones. However, as the matches are now concentrated in the middle of the image, the filtering process was overall satisfactory.

![](https://raw.githubusercontent.com/guilhermetiaki/panorama/master/demo/4-filtered.jpg)
Result of the matches filtering.

To stitch the images, the difference in the angle of the camera when taking the pictures must be compensated. The angle of the camera can be determined by trying to overlap the keypoints. The angle should be so that the sum of the distance between matching keypoints is minimized. This algorithm is implemented in OpenCV by the findHomography function.

![](https://raw.githubusercontent.com/guilhermetiaki/panorama/master/demo/5-perspective.jpg)
Result of applying the homography found to the left image.

To stitch the two images together we simply use the homoraphy matrix to find the translation of the right image and place it over the left image.

![](https://raw.githubusercontent.com/guilhermetiaki/panorama/master/demo/6-stitch.jpg)
Result of the translation

## Results

Applying all the steps described above to the original three images yields the results shown in figure 8. The homography found was able to perfectly match the objects in the scene in the seam between the images. The angle of the side images allows the panorama to look continuous and undistorted.

![](https://raw.githubusercontent.com/guilhermetiaki/panorama/master/demo/out.jpg)

