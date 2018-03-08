import os

from radiomics import featureextractor

from refactored_code.feature_extractor import run_extraction_pipe
from refactored_code.feature_extractor import extract_features

from refactored_code.Patient import Patient
from refactored_code.Lesion import Lesion

dir_path = os.path.dirname(os.path.realpath(__file__))
sample_data_folder = os.path.join(dir_path, 'sample_data')
extraction_params = os.path.join(dir_path, "extractionParams.yaml")


class Testfeature_extractor(object):

    def test_run_extraction_pipe(self):
        # /!\
        #
        # Dummy test case to complete
        #
        # /!\

        # list_patients = []
        # for refPatient in os.listdir(sample_data_folder):
        #     if not refPatient.startswith('.'):
        #         print("Processing patients %s ..." % refPatient)
        #         patient = Patient(refPatient, sample_data_folder)
        #         list_patients.append(patient)
        #         for directoryName in os.listdir(os.path.join(sample_data_folder, patient.ref)):
        #             if directoryName != 'dcm' and 'l' in directoryName:
        #                 print("   Processing lesion %s ..." % directoryName)
        #                 masksPath = os.path.join(sample_data_folder, refPatient, directoryName)
        #                 lesion = Lesion(directoryName, masksPath)
        #                 patient.list_lesions.append(lesion)
        #                 extract_features(extraction_params, lesion, patient.image)

        pass

    def test_extract_features(self):
        # /!\
        #
        # Dummy test case to complete
        #
        # /!\
        pass
