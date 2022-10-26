import random
import cv2
import numpy as np
import Arnold

def messageToBinary(message):
  if type(message) == str:
    return ''.join([ format(ord(i), "08b") for i in message ])
  elif type(message) == bytes or type(message) == np.ndarray:
    return [ format(i, "08b") for i in message ]
  elif type(message) == int or type(message) == np.uint8:
    return format(message, "08b")
  else:
    raise TypeError("Input type not supported")


# Function to hide the secret message into the image

def hideData(image, secret_message):
    n_bytes = image.shape[0] * image.shape[1] * 3 // 8
    # print("Maximum bytes to encode:", n_bytes)
    if len(secret_message) > n_bytes:
        raise ValueError("Error encountered insufficient bytes, need bigger image or less data !!")
    secret_message += "#####"
    data_index = 0
    binary_secret_msg = messageToBinary(secret_message)

    data_len = len(binary_secret_msg)
    for values in image:
        for pixel in values:
            r, g, b = messageToBinary(pixel)
            if data_index < data_len:
                pixel[0] = int(r[:-1] + binary_secret_msg[data_index], 2)
                data_index += 1
            if data_index < data_len:
                pixel[1] = int(g[:-1] + binary_secret_msg[data_index], 2)
                data_index += 1
            if data_index < data_len:
                pixel[2] = int(b[:-1] + binary_secret_msg[data_index], 2)
                data_index += 1
            if data_index >= data_len:
                break

    return image

def showData(image):

  binary_data = ""
  for values in image:
      for pixel in values:
          r, g, b = messageToBinary(pixel)
          binary_data += r[-1]
          binary_data += g[-1]
          binary_data += b[-1]
  all_bytes = [ binary_data[i: i+8] for i in range(0, len(binary_data), 8) ]
  decoded_data = ""
  for byte in all_bytes:
      decoded_data += chr(int(byte, 2))
      if decoded_data[-5:] == "#####":
          break
  #print(decoded_data)
  return decoded_data[:-5]


def encode_text():
    image_name = input("Enter image name(with extension): ")
    image = cv2.imread(image_name)  # Read the input image using OpenCV-Python.

    print("The shape of the image is: ", image.shape)  # check the shape of image to calculate the number of bytes in it
    # print("The original image is as shown below: ")
    # resized_image = cv2.resize(image, (500, 500))  # resize the image as per your requirement
    # cv2.imshow('window_name', resized_image)  # display the image
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    data = input("Enter data to be encoded : ")
    if (len(data) == 0):
        raise ValueError('Data is empty')

    filename = input("Enter the name of new encoded image(with extension): ")
    encoded_image = hideData(image, data)
    cv2.imwrite(filename, encoded_image)


def decode_text():
    image_name = input("Enter the name of the steganographed image that you want to decode (with extension) :")
    image = cv2.imread(image_name)
    # print("The Steganographed image is as shown below: ")
    # resized_image = cv2.resize(image, (500, 500))  # resize the original image as per your requirement
    # cv2.imshow('', resized_image)  # display the Steganographed image
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    text = showData(image)
    return text


#--------------------encode binary image------------------
def BinaryImg(imgPath, size=None, flag='binary'):
    imgRow = cv2.imread(imgPath)
    if size != None: # 调整图像尺寸
        imgRow= cv2.resize(imgRow,size)
    size = imgRow.shape
    imgGray = cv2.cvtColor(imgRow, cv2.COLOR_RGB2GRAY) # 转换颜色空间为灰度
    imgName = imgPath[:-3].split('.')[0] # 获取图像原始名称
    if flag == 'gray': # 生成灰度图
        cv2.imwrite('{}_gray.bmp'.format(imgName), imgGray)
        print('Gray image generated!')
    else: # 生成二值图
        ret, imgBinary = cv2.threshold(imgGray, 127, 255, cv2.THRESH_BINARY)
        prop = int(size[0]*size[1]/(1920*1080)*100) # 以载体图像为512x512，算生成的水印大小占载体图的百分比
        cv2.imwrite('{}_binary{}.bmp'.format(imgName, prop), imgBinary)
        print('Binary image generated!')
        print('threshold:{}'.format(ret)) # 输出转换阈值


def genEmbedBinStream(imgEmbed):
    rowScale = imgEmbed.shape[0]
    columnScale = imgEmbed.shape[1]
    binStreamList = []
    for i in range(rowScale):
        for j in range(columnScale):
            if imgEmbed.item(i, j) != 0:
                imgEmbed.itemset((i, j), 1)
            binStreamList.append(imgEmbed.item(i, j))
    return binStreamList


def genRandEmbedZone(imgCover,imgEmbed):
    binStreamScale = len(genEmbedBinStream(imgEmbed))
    rowScale = imgCover.shape[0]
    columnScale = imgCover.shape[1]
    rgbScale = 3
    zone = []
    for i in range(rowScale):
        for j in range(columnScale):
            for k in range(rgbScale):
                zone.append(list([i,j,k]))
    return random.sample(zone, binStreamScale)


def LSBembedding(imgCover, binStreamList, key):
    '''
    LSB嵌入主函数，imgCoverPath为载体图像路径，imgEmbedPath为水印路径，
    embedZone为嵌入位置（由我写的算法自动生成），bitPlane用于指定嵌入的位平面，默认为1（LSB位）
    '''

    data_index = 0
    data_len = len(binStreamList)  # Find the length of data that needs to be hidden
    for position in key:
        binpixel = messageToBinary(imgCover[position[0]][position[1]][position[2]])
        imgCover[position[0]][position[1]][position[2]] = int(binpixel[:-1]+str(binStreamList[data_index]), 2)
        data_index += 1
    return imgCover

def LSBextract(imgCover, key, size):
    binStreamList = []
    for position in key:
        binpixel = messageToBinary(imgCover[position[0]][position[1]][position[2]])
        if (binpixel[-1] == '1'):
            binStreamList.append(255)
        else:
            binStreamList.append(0)
    imgEmbedMatrix = [binStreamList[i * size[0]:(i + 1) * size[0]] for i in range(size[1])]
    imgEmbed = np.array(imgEmbedMatrix, dtype=np.uint8)
    return imgEmbed


def savekey(key, filename, arnold_time):
    keyfile = open("./key/{}.lsbkey".format(filename), "w",)
    keyfile.write(str(arnold_time)+'\n')
    for i in key:
        keyfile.write(str(i))

def encodebinaryimage():
    #read img
    image_name_cover = input("Enter cover image name(with extension): ")
    image_cover = cv2.imread(image_name_cover)
    image_name_embed = input("Enter embed image name(with extension): ")
    image_embed = cv2.imread(image_name_embed, cv2.IMREAD_GRAYSCALE)

    # create arnold times and mess up
    arnold_time = random.randint(5, 10)
    image_embed = Arnold.arnold_time(image_embed, arnold_time)

    # transform into binary stream
    binStreamList = genEmbedBinStream(image_embed)
    if len(binStreamList) > image_cover.shape[0] * image_cover.shape[1]:
        print('Error encountered insufficient bytes, need bigger image or less data !!')
        return

    #create and save key and arnold time together
    key = genRandEmbedZone(image_cover, image_embed)
    savekey(key, image_name_cover, arnold_time)
    print("Key File generated")


    image_edited = LSBembedding(image_cover, binStreamList, key)
    image_name_output = input("Enter output image name(with extension):" )
    cv2.imwrite('{}'.format(image_name_output), image_edited)
    print('LSB Embeding done!')

def readkey(filename):
    keyfile = open("./key/{}".format(filename), "r")
    keyfilelist = keyfile.readlines()
    for lines in keyfilelist[1:]:
        lines1 = lines.replace('[', ',')
        lines2 = lines1.replace(']', '')
        lines3 = lines2.replace(' ','')
        lines4 = lines3.split(',')
        keylist = []
        j=0
        nums = []
        for i in range(1,len(lines4)):
            num = int(lines4[i])
            nums.append(num)
            j+=1
            if(j==3):
                j=0
                keylist.append(nums)
                nums=[]

    return keylist

def readtime(filename):
    keyfile = open("./key/{}".format(filename), "r")
    keyfilelist = keyfile.readlines()
    time = keyfilelist[0]
    time.replace('\n', '')
    time = int(time)
    return time


def decodebinaryimage():
    image_name_decode = input("Enter decode image name(with extension): ")
    image_decode = cv2.imread(image_name_decode)
    embed_size_1 = input("Enter embed image height:")
    embed_size_2 = input("Enter embed image width:")
    embed_size_1 = int(embed_size_1)
    embed_size_2 = int(embed_size_2)
    keyname = input("Enter key file name(with extension): ")
    arnold_time = readtime(keyname)
    key = readkey(keyname)
    image_embed = LSBextract(image_decode, key, [embed_size_1, embed_size_2])
    image_embed = Arnold.dearnold_time(image_embed, arnold_time)
    cv2.imwrite('img_extract.bmp', image_embed)

# Image Steganography
def Steganography():
    a = input("Image Steganography \n 1. Encode the data \n 2. Decode the data \n Your input is: ")
    userinput = int(a)
    if (userinput == 1):
        b = input("Encode the data \n 1. Encode text\n 2. Encode image(image must be binary)\n Your input is:")
        userinput = int(b)
        if(userinput == 1):
            print("\nEncoding....")
            encode_text()
        elif(userinput == 2):
            print("\nEncoding....")
            encodebinaryimage()
        else:
            raise Exception("Enter correct input")

    elif (userinput == 2):
        b = input("Decode the data \n 1.Decode text\n 2. Decode binary image\n Your input is:")
        userinput = int(b)
        if(userinput == 1):
            print("\nDecoding....")
            print("Decoded message is: " + decode_text())
        elif(userinput == 2):
            print("\nDecodeing....")
            decodebinaryimage()
    else:
        raise Exception("Enter correct input")


Steganography()  # encode image
