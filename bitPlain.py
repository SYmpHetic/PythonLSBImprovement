import cv2
import numpy as np

a = cv2.imread("lena_color_text.bmp", -1)
x, y, z = a.shape
b = np.zeros((x, y, 8), dtype=np.uint8)
for i in range(8):
    b[:, :, i] = 2 ** i
temp = np.zeros((x, y, 3), dtype=np.uint8)
for i in range(1):
    temp[:, :, 0] = cv2.bitwise_and(a[:, :, 0], b[:, :, i])
    temp[:, :, 1] = cv2.bitwise_and(a[:, :, 1], b[:, :, i])
    temp[:, :, 2] = cv2.bitwise_and(a[:, :, 2], b[:, :, i])
    m = temp[:, :] > 0
    temp[m] = 255
    cv2.imshow(str(i), temp)
    cv2.imwrite("./bitplain/{}".format(i)+"LSB_text.bmp",temp)
cv2.waitKey()
cv2.destroyAllWindows()
