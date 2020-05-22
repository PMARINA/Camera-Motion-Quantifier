import math
import os

import cv2
import imutils as imutils
import numpy as np

window_title = "The Input Image"
input_image = "input.jpg"
input_video = "small_horizontal_ruler.MP4"
output_image = os.path.basename(__file__)[:-len(".py")] + ".jpg"
output_video = os.path.basename(__file__)[:-len(".py")] + ".MP4"
HORIZONTAL = 0
VERTICAL = 1
num_frames = 848
num_matches = 50


def read_image(file_name=input_image):
    img = cv2.imread(file_name)
    return img


def get_video(file_name=input_video):
    video = cv2.VideoCapture(file_name)
    return video


def display_image(img, window_title=window_title):
    cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)
    cv2.imshow(window_title, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return


def grayscale(img):
    grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # =6, BGR and not RGB because of how cv2 returns images
    return grayscale


def save_to_disk(img, filename=output_image):
    cv2.imwrite(filename, img)


def get_dimensions_hw(img):
    return img.shape[0:2]


def get_middle_pixels_hw(img, new_height, new_width):
    input_img_h, input_img_w = get_dimensions_hw(img)
    if new_height > input_img_h:
        raise ValueError(
            "Requested new height (" + str(new_height) + ") is greater than image height (" + str(input_img_h) + ").")
    if new_width > input_img_w:
        raise ValueError(
            "Requested new width (" + str(new_width) + ") is greater than image width (" + str(input_img_w) + ").")
    middle_h = round(input_img_h / 2)
    half_new_height = round(new_height / 2)
    middle_w = round(input_img_w / 2)
    half_new_width = round(new_width / 2)
    middle_pixels = img[middle_h - half_new_height:middle_h + half_new_height,
                    middle_w - half_new_width:middle_w + half_new_width]
    return middle_pixels


def set_periodic_pixel(img, frequency, direction, new_pixel):
    h, w = get_dimensions_hw(img)
    img = np.array(img, copy=True)
    if direction == HORIZONTAL:
        for i in range(0, h):
            for j in range(0, w, frequency):
                img[i][j] = new_pixel
    elif direction == VERTICAL:
        for i in range(0, h, frequency):
            for j in range(0, w):
                img[i][j] = new_pixel
    return img


def flip(img, direction):
    h, w = get_dimensions_hw(img)
    flipped = np.array(img, copy=True)
    if direction == HORIZONTAL:
        for i in range(h):
            for j in range(w):
                flipped[i][j] = img[i][w - j - 1]
    elif direction == VERTICAL:
        for i in range(h):
            for j in range(w):
                flipped[i][j] = img[h - i - 1][j]
    return flipped


def ineff_show_side_by_side(img1, img2):
    h1, w1 = get_dimensions_hw(img1)
    h2, w2 = get_dimensions_hw(img2)
    side_by_side = np.zeros([max(h1, h2), w1 + w2, 3], np.uint8)
    for i in range(h1):
        for j in range(w1):
            side_by_side[i][j] = img1[i][j]
    for i in range(h2):
        for j in range(w2):
            side_by_side[i][j + w1] = img2[i][j]
    return side_by_side


def combine_horizontally(img1, img2):
    return np.concatenate((img1, img2), axis=1)


def get_copy(img):
    return np.array(img, copy=True)


def histogram_equalize(img):
    copy = get_copy(img)
    copy = cv2.cvtColor(img, cv2.COLOR_BGR2YCR_CB)
    y, cr, cb = cv2.split(copy)
    cv2.equalizeHist(y, y)
    copy = cv2.merge((y, cr, cb))
    copy = cv2.cvtColor(copy, cv2.COLOR_YCR_CB2BGR)
    return copy


def detect_orb_keypoints(img):
    copy = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    orb = cv2.ORB_create()
    points, des = orb.detectAndCompute(copy, None)  # img, mask for exclusion/inclusion zone of image
    return points, des


def match_kd(p1, d1, p2, d2):
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, True)
    m = matcher.match(d1, d2)
    m = sorted(m, key=lambda x: x.distance)
    return m


def gaussian_blur(img, k=3, a=0):
    return cv2.GaussianBlur(img, (k, k), a)


if __name__ == "__main__":
    video = get_video()
    frames = []
    keypoints_and_descriptors = []
    equalized = []
    img = None
    stringer = ""
    half_height = half_width = 0
    for i in range(int(video.get(cv2.CAP_PROP_FRAME_COUNT))):
        ret, img = video.read()
        if ret and np.shape(img) != ():
            img = gaussian_blur(img, 5)
            his = histogram_equalize(img)
            equalized.append(his)
            keypoints_and_descriptors.append(detect_orb_keypoints(his))
            if i > 0:
                m = match_kd(keypoints_and_descriptors[0][0], keypoints_and_descriptors[0][1],
                             keypoints_and_descriptors[1][0], keypoints_and_descriptors[1][1])[:num_matches]
                outpoints = []
                for match in m:
                    idx1 = match.trainIdx
                    idx2 = match.queryIdx
                    x1, y1 = keypoints_and_descriptors[0][0][idx2].pt
                    x2, y2 = keypoints_and_descriptors[1][0][idx1].pt
                    outpoints.append(((int(x1), int(y1)), (int(x2), int(y2))))
                dx = 0
                dy = 0
                dtheta = 0
                for (p1, p2) in outpoints:
                    dx += p1[0] - p2[0]
                    dy += p1[1] - p2[1]
                    theta1 = math.atan2(p1[1] - half_height, p1[0] - half_width)
                    theta2 = math.atan2(p2[1] - half_height, p2[0] - half_width)
                    dtheta += theta1 - theta2
                dx = dx / float(num_matches)
                dy = dy / float(num_matches)
                dtheta = dtheta / float(num_matches)
                equalized[1] = imutils.rotate_bound(equalized[1], dtheta * 180 / math.pi)
                keypoints_and_descriptors[1] = detect_orb_keypoints(equalized[1])
                m = match_kd(keypoints_and_descriptors[0][0], keypoints_and_descriptors[0][1],
                             keypoints_and_descriptors[1][0], keypoints_and_descriptors[1][1])[:num_matches]
                outpoints = []
                for match in m:
                    idx1 = match.trainIdx
                    idx2 = match.queryIdx
                    x1, y1 = keypoints_and_descriptors[0][0][idx2].pt
                    x2, y2 = keypoints_and_descriptors[1][0][idx1].pt
                    outpoints.append(((int(x1), int(y1)), (int(x2), int(y2))))
                dx = 0
                dy = 0
                dtheta = 0
                for (p1, p2) in outpoints:
                    dx += p1[0] - p2[0]
                    dy += p1[1] - p2[1]
                    theta1 = math.atan2(p1[1] - half_height, p1[0] - half_width)
                    theta2 = math.atan2(p2[1] - half_height, p2[0] - half_width)
                    dtheta += theta1 - theta2
                dx = dx / float(num_matches)
                dy = dy / float(num_matches)
                dtheta = dtheta / float(num_matches)
                stringer += str(dx) + "\t" + str(dy) + "\t" + str(dtheta) + "\n"
                equalized.pop(0)
                keypoints_and_descriptors.pop(0)
            else:
                half_height, half_width = get_dimensions_hw(img)
                half_height = half_height / 2
                half_width = half_width / 2
    print(stringer)
