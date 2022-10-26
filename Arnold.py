import numpy as np
import cv2

def arnold(img):
    r, c = img.shape
    p = np.zeros((r, c), np.uint8)
    a = 1
    b = 1
    for i in range(r):
        for j in range(c):
            x = (i + b * j) % r
            y = (a * i + (a * b + 1) * j) % c
            p[x, y] = img[i, j]
    return p

def dearnold(img):
    r, c = img.shape
    p = np.zeros((r, c), np.uint8)
    a = 1
    b = 1
    for i in range(r):
        for j in range(c):
            x = ((a * b + 1) * i - b * j) % r
            y = (-a * i + j) % c
            p[x, y] = img[i, j]
    return p

def arnold_time(image, times):
    for i in range(times):
        image = arnold(image)
    return image

def dearnold_time(image, times):
    for i in range(times):
        image = dearnold(image)
    return image


img=cv2.imread("a.bmp", cv2.IMREAD_GRAYSCALE)
img=arnold_time(img, 10)
cv2.imwrite("a_arnold.bmp", img)