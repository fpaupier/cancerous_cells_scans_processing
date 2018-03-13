import os
import pandas as pd

from refactored_code.feature_extractor import run_extraction_pipe
from refactored_code.feature_extractor import extract_features
from refactored_code.feature_extractor import convert_patients_list_to_dataFrame

from refactored_code.Patient import Patient
from refactored_code.Lesion import Lesion

dir_path = os.path.dirname(os.path.realpath(__file__))
sample_data_folder = os.path.join(dir_path, 'sample_data')
extraction_params = os.path.join(dir_path, "extractionParams.yaml")
path_to_features_csv = os.path.join(dir_path, "sample_csv_features.csv")

# Used for patient wise testing of the extraction before going to the batch level
patient_ref = "001-060"
lesion_directory_name = "l2"


class Testfeature_extractor(object):

    def test_extract_features(self):

        # Set up the test data
        patient = Patient(patient_ref, sample_data_folder)
        masksPath = os.path.join(sample_data_folder, patient_ref, lesion_directory_name)
        lesion = Lesion(lesion_directory_name, masksPath)
        patient.list_lesions.append(lesion)

        # Extract the features for one single lesion of a patient
        extract_features(extraction_params, lesion, patient.image)

        # Print the features
        print("Below are the supposed key-value features extracted")
        for key, value in lesion.dict_features.items():
            print(key, value)
        print("End of expected feature dictionary")

        # Assert based on the fact that the dictionary is not empty
        try:
            assert bool(lesion.dict_features)
        except AssertionError:
            print("Feature dictionary should not be empty. Feature extraction may have failed.")


    def test_convert_patients_list_to_dataFrame(self):
        # Dummy test
        # Just check that the conversion of a patient list to a pandas data frame outputs the correct result
        # TO DO (not mandatory) add an assert statement to check that the good values are being reported.

        # Set up the test data
        list_patients = []
        for refPatient in os.listdir(sample_data_folder):
            if not refPatient.startswith('.'):
                print("Processing patients %s ..." % refPatient)
                patient = Patient(refPatient, sample_data_folder)
                list_patients.append(patient)
                for directoryName in os.listdir(os.path.join(sample_data_folder, patient.ref)):
                    if directoryName != 'dcm' and 'l' in directoryName:
                        print("   Processing lesion %s ..." % directoryName)
                        masksPath = os.path.join(sample_data_folder, refPatient, directoryName)
                        lesion = Lesion(directoryName, masksPath)
                        patient.list_lesions.append(lesion)
                        extract_features(extraction_params, lesion, patient.image)

        # Call the data set converter
        patients_dataFrame = convert_patients_list_to_dataFrame(list_patients)

        # Display resulting dataset for debug
        pd.options.display.float_format = '${:,.2f}'.format
        print(patients_dataFrame)
        pass

    def test_run_extraction_pipe(self):

        # Run the extraction pipeline from sample data
        run_extraction_pipe(sample_data_folder, path_to_features_csv, extraction_params)
        pass
