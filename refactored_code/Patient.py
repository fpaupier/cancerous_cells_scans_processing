# coding=utf-8

###
# Patient.py -
# This file contains the definition of class Patient used to handle patients scans, store their lesions
# and survival time.
# Patient.py also implements handy function to pre process a pile of dicom image e.g. conversion to SUV
#
# Author : François Paupier - francois.paupier@gmail.com
#
# Created on : 16/02/2018
###

import numpy as np
import dicom
import os
import SimpleITK as sitk
import dicom_numpy


# --------------------------
# Patient class definition
# --------------------------


class Patient:

    def __init__(self, ref, PATH_TO_DATA, list_lesions=[]):
        '''Provide ref number of the patient as a string "xxx-xxx", image is simpleITK type'''
        self.ref = ref
        self.list_lesions = list_lesions
        dcmDirectory = os.path.join(PATH_TO_DATA, ref, "dcm")
        self.image = dcmToSimpleITK(dcmDirectory)


# --------------------------
# Set of functions used to pre process dcm slice
# --------------------------

def isSliceUnitSUV(dcmSlice):
    '''Take a dcm slice in input and returns true if the voxels are expressed in SUV - Standardized uptake value.
    Return false otherwise.'''

    # 00541001 corresponds to the tag index of the voxel unit in the dcm file
    units = dcmSlice[0x00541001].value.lower()
    unitIsSUV = "suv" in units

    if unitIsSUV:
        return True
    else:
        return False


def setSliceUnitToSUV(pathToDcmSlice):
    '''Take an absolute path to a dcm file and change its dicom tag related to units [0054,1001] to 'suv' and save the
     dcm.'''
    dcmSlice = dicom.read_file(pathToDcmSlice)
    dcmSlice[0x00541001].value = 'suv'
    dcmSlice.save_as(pathToDcmSlice)


def multiplySlice(scalar, pathToDcmSlice):
    '''Take a scalar value and the absolute path of a dcm slice.
    Multiply all pixels in the slice per the scalar value and save the slice under the same slice name.
    Warning : saving erase the original data for the new multiplied ones.'''

    dcmSlice = dicom.read_file(pathToDcmSlice)

    for n, val in enumerate(dcmSlice.pixel_array.flat):
        dcmSlice.pixel_array.flat[n] = scalar * dcmSlice.pixel_array.flat[n]

    dcmSlice.PixelData = dcmSlice.pixel_array.tostring()
    dcmSlice.save_as(pathToDcmSlice)


def convertToSUV(dcmDirectory):
    '''Convert the voxels from a pile of dcm file to the SUV unit - logic inherited from Thomas'
    Fiji macro MacroBqtToSUV.ijm
    Warning 1: This function assumes the patient mass' (tag [0010,1030] in the dicom) is correctly set.
    Warning 2: No sanity check is done on the delay between injection and acquisition to see if belongs
    to the range of EANM guidelines'''

    # WARNING : Code to rewrite : currently the output dcm files are integers values only

    # Get the pile of dcm slices
    list_dcmFiles = []
    for directory, subDirectory, list_dcmFileNames in os.walk(dcmDirectory):
        for fileName in list_dcmFileNames:
            if '.dcm' in fileName.lower():  # check whether file is a dicom
                list_dcmFiles.append(os.path.join(directory, fileName))
    list_dcmSlices = [dicom.read_file(sliceFile) for sliceFile in list_dcmFiles]

    # Choose the first slice to check for voxel unit
    dcmSlice = list_dcmSlices[0]

    # If the slice is already in SUV we assume all the dcm pile for a same patient is in SUV, otherwise we convert
    if not isSliceUnitSUV(dcmSlice):

        # Compute the suvFactor
        manufacturer = dcmSlice[0x00080070].value.lower()
        manufacturerIsPhilips = "philips" in manufacturer

        units = dcmSlice[0x00541001].value.lower()
        unitIsNotBqml = "bqml" not in units

        if manufacturerIsPhilips and unitIsNotBqml:
            suvFactor = float(dcmSlice[0x70531000].value)
        else:
            for sliceIndex, localDcmSlice in enumerate(list_dcmSlices):
                rescaleSlope = float(dcmSlice[0x00281053].value)
                localDcmSlicePath = os.path.join(dcmDirectory, list_dcmFiles[sliceIndex])
                multiplySlice(rescaleSlope, localDcmSlicePath)

            # Get infos from the patient dcm tags
            acquisitionHour = int(dcmSlice[0x00080031].value[0:2])
            acquisitionMinute = int(dcmSlice[0x00080031].value[2:4])
            injectionHour = int(dcmSlice[0x00540016].value[0][0x00181072].value[0:2])
            injectionMinute = int(dcmSlice[0x00540016].value[0][0x00181072].value[2:4])

            deltaHour = acquisitionHour - injectionHour
            deltaMinute = acquisitionMinute - injectionMinute

            if (deltaMinute < 0):
                deltaMinute = 60 + deltaMinute
                deltaHour = deltaHour - 1

            decayFactor = np.exp(-np.log(2) * ((60 * deltaHour) + deltaMinute) / 109.8)

            radioNuclideTotalDose = float(dcmSlice[0x00540016].value[0][0x00181074].value)
            correctedActivity = decayFactor * radioNuclideTotalDose

            patientMass = float(dcmSlice[0x00101030].value)
            suvFactor = (patientMass * 1000) / correctedActivity

        # All slices are multiplied per the same suv factor. We assume it's a constant for a patient
        for sliceIndex, localDcmSlice in enumerate(list_dcmSlices):
            localDcmSlicePath = os.path.join(dcmDirectory, list_dcmFiles[sliceIndex])
            multiplySlice(suvFactor, localDcmSlicePath)
            setSliceUnitToSUV(localDcmSlicePath)




def dcmToSimpleITK(dcmDirectory):
    '''Return a simple ITK image from a pile of dcm files'''
    list_dcmFiles = []
    for directory, subDirectory, list_dcmFileNames in os.walk(dcmDirectory):
        for dcmFile in list_dcmFileNames:
            if '.dcm' in dcmFile.lower():
                list_dcmFiles.append(os.path.join(directory, dcmFile))
    dcmImage = [dicom.read_file(dcmSliceFile) for dcmSliceFile in list_dcmFiles]
    voxel_ndarray, ijk_to_xyz = dicom_numpy.combine_slices(dcmImage)
    sITK_image = sitk.GetImageFromArray(voxel_ndarray)
    return (sITK_image)
