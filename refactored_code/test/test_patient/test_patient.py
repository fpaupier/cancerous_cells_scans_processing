import os
import pydicom
import SimpleITK as sitk
import dicom_numpy
import numpy as np
import math

from pydicom.data import get_testdata_files

from refactored_code.Patient import Patient
from refactored_code.Patient import isSliceUnitSUV
from refactored_code.Patient import setSliceUnitToSUV
from refactored_code.Patient import dcmToSimpleITK
from refactored_code.Patient import convertToSUV
from refactored_code.Patient import initializePatientImage

dir_path = os.path.dirname(os.path.realpath(__file__))
sample_dicom_folder = os.path.join(dir_path, 'sample_dicom')
sample_patient_folder = os.path.join(dir_path, 'sample_data')
sample_dicom_slice = os.path.join(sample_dicom_folder, 'A_sample.dcm')



class TestPatient(object):

    def test_isSliceUnitSUV(self):

        # Load sample dicom file from pydicom test database
        filename = get_testdata_files('rtplan.dcm')[0]
        ds = pydicom.dcmread(filename)

        # Negative test case
        # Add a tag for the unit and set it to bqml
        ds.add_new(0x00541001, 'CS', 'bqml')
        assert (isSliceUnitSUV(ds) is False)

        # Positive test case
        # Change the unit tag to SUV
        ds[0x00541001].value = 'SUV'
        assert isSliceUnitSUV(ds)


    def test_setSliceUnitToSUV(self):

        # Load a sample dcm and set a non suv value.
        filename = get_testdata_files('rtplan.dcm')[0]
        ds = pydicom.dcmread(filename)
        ds.add_new(0x00541001, 'CS', 'bqml')

        # Save a temporary test dicom
        ds.save_as('rtplan_bqml_unit.dcm')


        bqml_ds = pydicom.dcmread('rtplan_bqml_unit.dcm')
        assert(isSliceUnitSUV(bqml_ds) is False)

        # Change the unit from bqml to suv
        setSliceUnitToSUV('rtplan_bqml_unit.dcm')

        # Reload the dcm to check for it's unit
        suv_ds = pydicom.dcmread('rtplan_bqml_unit.dcm')
        assert isSliceUnitSUV(suv_ds)

        # Clear the test data
        os.remove('rtplan_bqml_unit.dcm')


    def test_dcmToSimpleITK(self):
        dcmFiles = []
        for (dirPath, subDirs, fileNames) in os.walk(sample_dicom_folder):
            for fileName in fileNames:
                if not fileName.startswith('.'):
                    dcmFiles.append(os.path.join(sample_dicom_folder, fileName))
        datasets = [pydicom.dcmread(dcmSliceFile) for dcmSliceFile in dcmFiles]
        dicomAsArray, ijk_to_xyz = dicom_numpy.combine_slices(datasets)
        sITK_image = sitk.GetImageFromArray(dicomAsArray)
        assert (sITK_image == dcmToSimpleITK(sample_dicom_folder))


    def test_dcmRescaleSlope(self):
        """Check if the dicom_numpy.combine_slices method properly handle the multiplication of each dcm slice per the
        rescale slope."""
        dcmIndex = 0
        for (dirName, subDirs, fileNames) in os.walk(sample_dicom_folder):
            fileNames.sort()
            nbSlices = len(fileNames)
            for fileName in fileNames:
                if '.dcm' in fileName:
                    ds = pydicom.dcmread(os.path.join(sample_dicom_folder,fileName))
                    voxels = ds.pixel_array.astype('float32')

                    # Compute the scaled 2D array
                    rescaleSlope = float(ds[0x00281053].value)
                    scaledVoxels = rescaleSlope * voxels

                    # Add the 2D array to the 3D array
                    if dcmIndex == 0 :
                        (nbRow, nbCol) = voxels.shape
                        voxels_ndarray = np.zeros((nbRow, nbCol, nbSlices))

                    voxels_ndarray[:, :, dcmIndex] = scaledVoxels.T
                    dcmIndex = dcmIndex + 1

        nd_arrayToTest = sitk.GetArrayFromImage(dcmToSimpleITK(sample_dicom_folder)).astype('float32')

        # Check for each coefficient that the two values are equal
        for rowId in range(nbRow):
            for colId in range(nbCol):
                for sliceId in range(dcmIndex):
                    assert math.isclose(nd_arrayToTest[rowId, colId, sliceId],
                                        voxels_ndarray[rowId, colId, sliceId],
                                        rel_tol=1e-9)
    def test_convertToSUV(self):
        # /!\
        #
        # Dummy test case to complete
        #
        # /!\

        # Get simple ITK image rescaled
        sitkImage = dcmToSimpleITK(sample_dicom_folder)

        # Compute SUV factor
        imageSUV = convertToSUV(sample_dicom_folder, sitkImage)
        pixelData = sitk.GetArrayFromImage(imageSUV)

        # Multiply slices per SUV factor

        # Compare to the output of convertToSUV method and assert voxels have the same value

        pass

    def test_initializePatientImage(self):
        # /!\
        #
        # Dummy test case to complete
        #
        # /!\

        image = initializePatientImage(sample_dicom_folder)
        pass

    def test_Patient(self):
        # /!\
        #
        # Dummy test case to complete
        #
        # /!\

        # Instantiate a test patient
        list_patients = []
        for refPatient in os.listdir(sample_patient_folder):
            if not refPatient.startswith('.'):
                patient = Patient(refPatient, sample_patient_folder)

        pass