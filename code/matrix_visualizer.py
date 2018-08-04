# coding=utf-8

###
# matrix_visualizer.py -
# This file contains code to generate and visualize sample matrix and features being used in PET scans features
# extraction to help the understanding of the glcm, glrlm, glszm being used in the extraction pipe
#
# Patient.py also implements handy function to pre process a pile of dicom image e.g. conversion to SUV
#
# Author : François Paupier - francois.paupier@gmail.com
#
# Created on : 30/03/2018
###

import numpy as np
import matplotlib.pyplot as plt

# Reference matrix used to compute the other matrix features
I = np.array([[1, 2, 5, 2, 3],
              [3, 2, 1, 3, 1],
              [1, 3, 5, 5, 2],
              [1, 1, 1, 1, 2],
              [1, 2, 4, 3, 5]
              ])

# GLC, GLRL and GLSZ matrix are hand written (examples from pyradiomics'doc)
glcm = np.array([[6, 4, 3, 0, 0],
                 [4, 0, 2, 1, 3],
                 [3, 2, 0, 1, 2],
                 [0, 1, 1, 0, 0],
                 [0, 3, 2, 0, 2]

                 ])

glrlm = np.array([[1, 0, 1, 0, 0],
                  [3, 0, 1, 0, 0],
                  [4, 1, 1, 0, 0],
                  [1, 1, 0, 0, 0],
                  [3, 0, 0, 0, 0]

                  ])

glszm = np.array([[0, 0, 0, 1, 0],
                  [1, 0, 0, 0, 1],
                  [1, 0, 1, 0, 1],
                  [1, 1, 0, 0, 0],
                  [3, 0, 0, 0, 0]

                  ])

#
# Sample feature calculation : SAGLE from GSLZ matrix
#
(nRow, nCol) = glszm.shape
Nz = nRow * nCol
sagle_num = 0
for rowIndex in range(nRow):
    for colIndex in range(nCol):
        sagle_num = sagle_num + glszm[rowIndex, colIndex] / ((1 + rowIndex) ** 2 * (1 + colIndex) ** 2)
print('SAGLE value :  %0.03F' % sagle_num)

#
# Display reference and other matrix of interests
#
plt.figure(1)
plt.subplot(141)
plt.imshow(I)
plt.title('Reference')
plt.subplot(142)
plt.imshow(glcm)
plt.title('GLC Matrix')
plt.subplot(143)
plt.imshow(glrlm)
plt.title('GLRL Matrix')
plt.subplot(144)
plt.imshow(glszm)
plt.title('GLSZ Matrix')
plt.show()
