# test 1
# import cv2

# image =cv2.imread('input.jpg')

# cv2.imshow('hello world',image)

# cv2.waitKey()

# cv2.destroyAllWindows()

# test 2

# import cv2
# #importing numpy
# import numpy as np
# image=cv2.imread('input.jpg')
# cv2.imshow('hello_world', image)
# #shape function is very much useful when we are looking at a dimensions of an array, it returns a tuple which gives a dimension of an image
# print(image.shape)
# cv2.waitKey()
# cv2.destroyAllWindows()

# print('Height of image:',(image.shape[0],'pixels'))
# print('Width of image:',(image.shape[1],'pixels'))

# cv2.imwrite('output.jpg',image)
# cv2.imwrite('output.png',image)


# test 3

# import cv2
# grey_image=cv2.imread('input.jpg',0)
# cv2.imshow('grayscale',grey_image)
# cv2.waitKey()
# cv2.destroyAllWindows()

# test 4

import cv2
import numpy as np
image=cv2.imread('input.jpg')
print(image.shape)
cv2.imshow('original', image)
cv2.waitKey()
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
cv2.imshow('grayscale', gray_image)
print(gray_image.shape)
cv2.waitKey()
cv2.destroyALLWindows()