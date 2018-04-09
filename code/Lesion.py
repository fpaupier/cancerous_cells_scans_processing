# coding=utf-8

###
# Lesion.py -
# This file contains the definition of class Lesion used to process patients lesions (mask and features
# values associated to a lesion. Lesion.py also implements handy function to process the building of a mask (combining
# pile of file, majority vote, etc.
#
# Author : François Paupier - francois.paupier@gmail.com
#
# Created on : 16/02/2018
###

import numpy as np
import os
import re
from skimage.external import tifffile
import SimpleITK as sitk
from skimage import io
import collections


# --------------------------
# Lesion class definition
# --------------------------

class Lesion:

    def __init__(self, ref, masksPath):
        ''' Provide ref number as string "lx", where x is the number of the lesion, masksPath is the path to the folder
        containing the masks '''
        self.ref = ref
        self.mask = getMajorityVoteMask(masksPath)
        self.dict_features = collections.OrderedDict()  # Expected features are in the .yaml parameter file


# --------------------------
# Set of functions used handle binary mask creation
# --------------------------

def getWords(text):
    '''From a text input as a string, get the words separated by a space and return it as a list of strings'''
    return re.compile('\w+').findall(text)

def change_name(list_pileFiles):
    """change names of files to permit to open the files in the good order"""
    for k in range(len(list_pileFiles)):
        if list_pileFiles[k][-2]=='_':
            new=list(list_pileFiles[k][0:-1])
            new.append('0')
            new.append('0')
            new.append(list_pileFiles[k][-1])
            new_name = "".join(new)
            os.rename(list_pileFiles[k],new_name)    
    
        if list_pileFiles[k][-3]=='_':
            new=list(list_pileFiles[k][0:-2])
            new.append('0')
            new.append(list_pileFiles[k][-2])
            new.append(list_pileFiles[k][-1])
    
            new_name = "".join(new) 
            os.rename(list_pileFiles[k],new_name)  

def makeTifFromPile(pathToPile):
    '''Takes an absolute path containing a pile of masks, compute the resulting .tif mask and
     output the path to the created .tif mask'''
    list_pileFiles = []
    for dirpath, dirnames, fileNames in os.walk(pathToPile):
        for fileName in fileNames:
            if not fileName.startswith('.'):
                list_pileFiles.append(os.path.join(dirpath, fileName))
    change_name(list_pileFiles)
    
    list_pileFiles = []
    for dirpath, dirnames, fileNames in os.walk(pathToPile):
        for fileName in fileNames:
            if not fileName.startswith('.'):
                list_pileFiles.append(os.path.join(dirpath, fileName))
                
    first_file = list_pileFiles[0]
    # get the shape of the image
    with open(first_file, mode='r', encoding='utf-8') as tifFile:
        tifFile.readline()  # first line is junk data
        shapeLocalMask = getWords(tifFile.readline())  # second line of raw tif is shape of the dcm pile
        xShape = int(shapeLocalMask[0])
        yShape = int(shapeLocalMask[1])

    num_file = len(list_pileFiles)
    mask_array = np.zeros((num_file, xShape, yShape))
    fileIndex = 0
    # Run through the files of the pile
    for pileFile in list_pileFiles:
        with open(pileFile, mode='r', encoding='utf-8') as tifFile:
            tifFile.readline()  # junk line
            tifFile.readline()  # second line is shape of the dcm pile
            tifFile.readline()  # third line is junk data
            # Run through rows and columns of the file
            for rowIndex in range(xShape):
                for colIndex in range(yShape):
                    val = tifFile.read(1)
                    # Takes only 0 and 1 values (removes spaces)
                    while val != '0' and val != '1':
                        val = tifFile.read(1)
                    mask_array[fileIndex, rowIndex, colIndex] = int(val)
            fileIndex = fileIndex + 1 
            
    pathToLesion = os.path.abspath(os.path.join(pathToPile, os.pardir))

    pathToTifMask = os.path.join(pathToLesion, '_non-standard-mask.tif') # In case not 2.5 or 40 mask (non nominal path)
    if '2.5' in pathToPile:
        pathToTifMask = os.path.join(pathToLesion, '25.tif')
    if '40' in pathToPile:
        pathToTifMask = os.path.join(pathToLesion, '40.tif')

    # Warning : check why the size (in bytes) of the saved mask is up to 10 times the size of the 2.5 or 40 masks
    tifffile.imsave(pathToTifMask, mask_array)
    return pathToTifMask


def getTifMasks(masksPath):
    '''Return path toward the KMean, 40 and 2.5 mask respectively in this order'''
    list_files = [file for file in os.listdir(masksPath) if os.path.isfile(os.path.join(masksPath, file))]
    mask40Name = '40.tif'
    mask25Name = '25.tif'
    pathToKmeanMask = os.path.join(masksPath, "kmean.tif") # The kmean tiff mask is always already computed in our data
    # Checks if the 40 and 2.5 tiff masks are already computed. If not, they are computed
    if mask40Name in list_files:
        pathTo40Mask = os.path.join(masksPath, mask40Name)
    else:
        pathTo40Mask = makeTifFromPile(os.path.join(masksPath, "40"))
    if mask25Name in list_files:
        pathTo25Mask = os.path.join(masksPath, mask25Name)
    else:
        pathTo25Mask = makeTifFromPile(os.path.join(masksPath, '2.5'))
    return(pathToKmeanMask, pathTo40Mask, pathTo25Mask)


def setToSize(mask, imageDims):
    '''Set an array mask to the adapted size imageDims. This function is useful when the number of slices of the mask
    is not the same as the number of slices in the Dicom image'''
    
    i = 0
    while imageDims[2] < mask.shape[2]:  # The third dimension is the one concerned
        # Alternatively remove the first or the last slice until the size is correct
        if i % 2 == 0:
            mask = mask[:, :, 1:mask.shape[2]]
            i = i+1
        else:
            mask = mask[:, :, 0:mask.shape[2]-1]
            i = i+1
    return mask

def label_choice(mask,label):
    '''choise if label is 255 or 1'''
    indice=np.where(mask!=0.0)
    mask[indice]=label
    return mask

def getMajorityVoteMask(masksPath):
    '''Compute the average mask based on the majority vote method for a lesion. Masks used to compute resulting masks 
    are Kmean mask, 2.5 mask and 40% mask. The masks should be in the same path. The resulting tif mask is saved under 
    the masksPath directory under the name 'majority.tif' '''

    # Import the 3 masks
    (pathToKmeanMask, pathTo40Mask, pathTo25Mask) = getTifMasks(masksPath)
    # Transposed matrices are taken because the masks axis are reversed compared to dicom images axis
    mkmean = io.imread(pathToKmeanMask).T
    m25 = io.imread(pathTo25Mask).T
    m40 = io.imread(pathTo40Mask).T

    m25 = label_choice(m25,1.0)
    m40 = label_choice(m40,1.0)
    mkmean= label_choice(mkmean,1.0)

    # Parameters
    thresh = 0.33  # threshold value for accepting a voxel as belonging in the resulting majority vote mask
    nbMethods = 3  # Number of methods used (40%, 2.5 and kmean)

    # Dimensions
    imageDims = mkmean.shape

    # TODO: For some patients the masks provided have wrong dimensions. In such a case only the 40mask (which is supposed to
    # provide the correct features once combined with the patient scan. This is purely arbitrary and shall be
    # changed in favor of a more robust solution.
    masksAreSameSize = mkmean.shape == m25.shape == m40.shape

    # Initialize resulting matrix
    mMajority = np.zeros(imageDims)
    if masksAreSameSize:
#       sum_mask = m40 + m25 + mkmean
#       sum_mask = np.divide(sum_mask, nbMethods)
#       mMajority[sum_mask >= thresh] = 1  # Vectorized method
        mMajority = m40  # to compare with Thomas' features
    else:
#       mMajority[mkmean >= 1] = 1
        mMajority = setToSize(m40, imageDims)
    mMajority_tran=mMajority.T #used for the tiff save
    sITK_mask = sitk.GetImageFromArray(mMajority)
    
    majorityTiffPath = os.path.join(masksPath, "majority.tif")
    tifffile.imsave(majorityTiffPath, mMajority_tran)

    mMajority255=label_choice(mMajority_tran,255) #use to register with 255 label and permit to open with ImageJ
    majorityTiffPath2 = os.path.join(masksPath, "majority255.tif")
    tifffile.imsave(majorityTiffPath2, mMajority255)
    
    return sITK_mask