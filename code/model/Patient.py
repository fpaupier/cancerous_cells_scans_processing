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
import pydicom
import os
import SimpleITK as sitk
import dicom_numpy


# --------------------------
# Patient class definition
# --------------------------


class Patient:

    def __init__(self, ref, PATH_TO_DATA):
        '''Provide ref number of the patient as a string "xxx-xxx", image is simpleITK type'''
        self.ref = ref
        self.list_lesions = []
        dcmDirectory = os.path.join(PATH_TO_DATA, ref, "dcm")
        self.image = initializePatientImage(dcmDirectory)


# --------------------------
# Set of functions used to pre process dcm slice
# --------------------------

def isSliceUnitSUV(dcmSlice):
    """Take a dcm slice in input and returns true if the voxels are expressed in SUV - Standardized uptake value.
    Return false otherwise."""

    # 00541001 corresponds to the tag index of the voxel unit in the dcm file
    units = dcmSlice[0x00541001].value.lower()
    unitIsSUV = "suv" in units

    if unitIsSUV:
        return True
    else:
        return False


def setSliceUnitToSUV(pathToDcmSlice):
    """Take an absolute path to a dcm file and change its dicom tag related to units [0054,1001] to 'suv' and save the
     dcm."""
    dcmSlice = pydicom.dcmread(pathToDcmSlice)
    dcmSlice[0x00541001].value = 'suv'
    dcmSlice.save_as(pathToDcmSlice)


def multiplySlice(scalar, pathToDcmSlice):
    """WARNING : Deprecated function. This function is no longer used in the extraction pipe and it's expected behavior
    is not sure to be verified. To delete.
    Take a scalar value and the absolute path of a dcm slice.
    Multiply all pixels in the slice per the scalar value and save the slice under the same slice name.
    Warning : saving erase the original data for the new multiplied ones."""

    dcmSlice = pydicom.dcmread(pathToDcmSlice)

    for n, val in enumerate(dcmSlice.pixel_array.flat):
        dcmSlice.pixel_array.flat[n] = scalar * dcmSlice.pixel_array.flat[n]

    # Warning: passing to string may change the value of the voxels.
    # To debug : try printing the values of a voxel, and its dtype, before and after the multiplication
    # and before / after the tostring() method (pretty sure this is buggy part)
    dcmSlice.PixelData = dcmSlice.pixel_array.tostring()
    dcmSlice.save_as(pathToDcmSlice)


def dcmToSimpleITK(dcmDirectory):
    """Return a simple ITK image from a pile of dcm files. The returned sITK image has been rescaled based on the
    value of the rescale slope on the dicom tag. Array-like data of the 3D image can be obtained with the
    GetArrayFromImage() method"""
    list_dcmFiles = []
    for directory, subDirectory, list_dcmFileNames in os.walk(dcmDirectory):
        for dcmFile in list_dcmFileNames:
            if '.dcm' in dcmFile.lower():
                list_dcmFiles.append(os.path.join(directory, dcmFile))
    dcmImage = [pydicom.dcmread(dcmSliceFile) for dcmSliceFile in list_dcmFiles]
    voxel_ndarray, ijk_to_xyz = dicom_numpy.combine_slices(dcmImage)    
    sITK_image = sitk.GetImageFromArray(voxel_ndarray)
    return (sITK_image)


def convertToSUV(dcmDirectory, sITKImage):
    """Return a new simple ITK image where the voxels have been converted to SUV.
    Converts the voxels data from a simple ITK image to SUV, based on the SUV factor found (or computed if not) in the
    matching dicom slices from the dcmDirectory. The dicom slices and input simple ITK image are not modified.

    Warning 1: This function assumes all the patient DCM tags used below are defined and set to their correct value.
    Warning 2: No sanity check is done on the delay between injection and acquisition to see if belongs
    to the range of EANM guidelines.
    Warning 3: This function assumes all the slices are in the same unit (e.g. all slices' voxels are in SUV).
    Warning 4: simple ITK image passed as input are assumed to have been rescaled properly with the matching rescale
    slope found in the dicom tag of the matching dicom file."""


    # Get the pile of dcm slices
    list_dcmFiles = []
    for directory, subDirectory, list_dcmFileNames in os.walk(dcmDirectory):
        for fileName in list_dcmFileNames:
            if '.dcm' in fileName.lower():  # check whether file is a dicom
                list_dcmFiles.append(os.path.join(directory, fileName))

    # Choose the first slice to check for voxel unit
    refDicomSlice = pydicom.dcmread(list_dcmFiles[0])

    # Compute the suvFactor
    manufacturer = refDicomSlice[0x00080070].value.lower()
    manufacturerIsPhilips = "philips" in manufacturer

    units = refDicomSlice[0x00541001].value.lower()
    unitIsNotBqml = "bqml" not in units

    # Philips machines have specific tags
    if manufacturerIsPhilips and unitIsNotBqml:
        suvFactor = float(refDicomSlice[0x70531000].value)

    else:
        # Get infos from the patient dcm tags
        acquisitionHour = int(refDicomSlice[0x00080031].value[0:2])
        acquisitionMinute = int(refDicomSlice[0x00080031].value[2:4])
        injectionHour = int(refDicomSlice[0x00540016].value[0][0x00181072].value[0:2])
        injectionMinute = int(refDicomSlice[0x00540016].value[0][0x00181072].value[2:4])

        deltaHour = acquisitionHour - injectionHour
        deltaMinute = acquisitionMinute - injectionMinute

        if (deltaMinute < 0):
            deltaMinute = 60 + deltaMinute
            deltaHour = deltaHour - 1

        # Computing of the suvFactor from bqml
        decayFactor = np.exp(-np.log(2) * ((60 * deltaHour) + deltaMinute) / 109.8)

        radioNuclideTotalDose = float(refDicomSlice[0x00540016].value[0][0x00181074].value)
        correctedActivity = decayFactor * radioNuclideTotalDose

        patientMass = float(refDicomSlice[0x00101030].value)
        suvFactor = (patientMass * 1000) / correctedActivity

    # All slices are multiplied per the same suv factor. We assume it's a constant for a patient
    voxels = sitk.GetArrayFromImage(sITKImage).astype('float32')
    SUVVoxels = suvFactor * voxels    
    SUVsITKImage = sitk.GetImageFromArray(SUVVoxels)

    return SUVsITKImage


def initializePatientImage(dcmDirectory):
    """From a dicom directory, output the rescaled and converted to SUV simple ITK image used to compute features"""

    # Compute the simple ITK image rescaled per the rescale slope
    rescaledImage = dcmToSimpleITK(dcmDirectory)

    list_dcmFiles = []
    for directory, subDirectory, list_dcmFileNames in os.walk(dcmDirectory):
        for fileName in list_dcmFileNames:
            if '.dcm' in fileName.lower():  # check whether file is a dicom
                list_dcmFiles.append(os.path.join(directory, fileName))

    # Choose the first slice to check for voxel unit
    refDicomSlice = pydicom.dcmread(list_dcmFiles[0])

    # If the slice is already in SUV we assume all the dcm pile for a same patient is in SUV, otherwise we convert
    if isSliceUnitSUV(refDicomSlice):
        print("   Patient's voxels value are already in SUV. No conversion needed.")
        return rescaledImage

    else:
        print("   Patient's voxels value are not in SUV.  Converting the patient's voxels in SUV ...")
        image3D = convertToSUV(dcmDirectory, rescaledImage)
        print("   Conversion to SUV done")
#        return image3D
        return rescaledImage