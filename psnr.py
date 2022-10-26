# psnr 不可感性 峰值信噪比  划重点：PSNR值越大，就代表失真越少，两个图像（I II 和 K KK）越相似。
# PSNR高于40dB说明图像质量极好（即非常接近原始图像），
# 在30—40dB通常表示图像质量是好的（即失真可以察觉但可以接受），
# 在20—30dB说明图像质量差；而PSNR低于20dB图像不可接受
import numpy as np
import cv2
import math

def psnr(img_1, img_2):
    mse = np.mean((img_1 / 1.0 - img_2 / 1.0) ** 2)
    if mse < 1.0e-10:
        return 100
    return 10 * math.log10(255.0 ** 2 / mse)

if __name__ == "__main__":
    img1 = cv2.imread("lena_color_basic.bmp")
    img2 = cv2.imread("lena_color.bmp")
    print('psnr：{}'.format(psnr(img1, img2)))