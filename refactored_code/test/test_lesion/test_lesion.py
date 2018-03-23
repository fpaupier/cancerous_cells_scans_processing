import os
import sys
import numpy as np
from skimage.external import tifffile

from refactored_code.Lesion import getWords
from refactored_code.Lesion import makeTifFromPile
from refactored_code.Lesion import getTifMasks

dir_path = os.path.dirname(os.path.realpath(__file__))
sample_pile_folder = os.path.join(dir_path, 'sample_pile')
sample_lesion_folder = os.path.join(dir_path, 'sample_lesion')

class TestLesion(object):

    def test_getWords(self):
        sample_text = "image dimension is 128 128"
        expected_output = ["image", "dimension", "is", "128", "128"]
        assert expected_output == getWords(sample_text)

    def test_makeTifFromPile(self):
        # /!\
        #
        # Dummy test case to complete
        # This test doesn't really test anything against a ground truth but just run the makeTifFromPile function
        #
        # /!\

        # Process a pile of mask
        list_pileFiles = []
        for dirpath, dirnames, fileNames in os.walk(sample_pile_folder):
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
        fileIndex = num_file - 1
        for pileFile in list_pileFiles:
            with open(pileFile, mode='r', encoding='utf-8') as tifFile:
                tifFile.readline()  # junk line
                tifFile.readline()  # second line is shape of the dcm pile
                tifFile.readline()  # 3 lines of junk data
                for rowIndex in range(xShape):
                    for colIndex in range(yShape):
                        val = tifFile.read(1)
                        while val != '0' and val != '1':
                            val = tifFile.read(1)
                        mask_array[fileIndex, rowIndex, colIndex] = int(val)
                fileIndex = fileIndex - 1

        pathToLesion = os.path.abspath(os.path.join(sample_pile_folder, os.pardir))
        pathToTifMask = os.path.join(pathToLesion, 'sample.tif')
        tifffile.imsave(pathToTifMask, mask_array)

        tifToTest = makeTifFromPile(sample_pile_folder)
        imageToTest = tifffile.imread(tifToTest)

        # Compare the two ndarray
        assert np.array_equal(imageToTest, mask_array)

        # Delete test data
        os.remove(pathToTifMask)
        os.remove(os.path.join(pathToLesion, "_non-standard-mask.tif"))

    def test_getTifMasks(self):
        pathTo25Mask = os.path.join(sample_lesion_folder, '25.tif')
        pathTo40Mask = os.path.join(sample_lesion_folder, '40.tif')
        pathToKmeanMask = os.path.join(sample_lesion_folder, 'kmean.tif')

        (ExpectedPathToKmeanMask, expectedPathTo40Mask, expectedPathTo25Mask) = getTifMasks(sample_lesion_folder)

        assert (ExpectedPathToKmeanMask, expectedPathTo40Mask, expectedPathTo25Mask) == \
               (pathToKmeanMask, pathTo40Mask, pathTo25Mask)

        # Delete test data
        os.remove(pathTo25Mask)
        os.remove(pathTo40Mask)

    def test_getMajorityVoteMask(self):
        pass

    def test_Patient(selfself):
        pass