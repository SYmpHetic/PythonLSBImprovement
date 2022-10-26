import cv2
import numpy as np

def add_noise_Guass(img, mean=0, var=0.01):  # 添加高斯噪声
    img = np.array(img / 255, dtype=float)
    noise = np.random.normal(mean, var ** 0.5, img.shape)
    out_img = img + noise
    if out_img.min() < 0:
        low_clip = -1
    else:
        low_clip = 0
        out_img = np.clip(out_img, low_clip, 1.0)
        out_img = np.uint8(out_img * 255)
    return out_img


img1 = cv2.imread('lena_color_LSB.bmp')  # 使用opencv获取的图片， 图片的类型为numpy.array
out_img = add_noise_Guass(img1)
cv2.imshow("img", out_img)
cv2.waitKey(0)
# 在添加噪声的过程中，图像被归一化，直接保存时会出现全黑的问题，所以在这里要恢复图像，out_img * 255
cv2.imwrite('lena_LSB_guass.bmp', out_img * 255)
