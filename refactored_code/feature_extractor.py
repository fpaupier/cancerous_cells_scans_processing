# coding: utf-8

###
# feature_extractor.py -
# This file implements the extraction pipeline to obtain the expected features from a standardized dataset of patients
# and lesions.
# This script outputs a csv file containing the computed feature per patient.
#
# Pseudo code Implementation scheme:
#
# Create an empty list of patients
# For each patient directory in the data directory :
#   Create a new Patient object
#   Add the patient to the patient list
#   For each lesion directory in the patient directory:
#       Create a new Lesion object
#       Extract the features from the lesion and the patient PET scans
# Run through the patients' list and create a CSV containing the computed features per patients
#
# Author : François Paupier - francois.paupier@gmail.com
#
# Created on : 16/02/2018
###

import os

import pandas as pd
from radiomics import featureextractor

from Lesion import Lesion
from Patient import Patient


def run_extraction_pipe(PATH_TO_DATA, PATH_TO_FEATURES_CSV, PATH_TO_EXTRACTION_PARAMS):
    '''Pipe function takes the path to the standardized patients dataset and the path to the csv containing the
    extracted features. If no CSV path is provided a CSV file will be created in the parent directory of the patient
    dataset.'''

    print("Path to Data : %s \nPath to CSV feature : %s" % (PATH_TO_DATA, PATH_TO_FEATURES_CSV))
    list_patients = []
    for refPatient in os.listdir(PATH_TO_DATA):
        if not refPatient.startswith('.'):
            print("Processing patients %s ..." % refPatient)
            patient = Patient(refPatient, PATH_TO_DATA)
            list_patients.append(patient)
            for directoryName in os.listdir(os.path.join(PATH_TO_DATA, patient.ref)):
                if directoryName != 'dcm' and 'l' in directoryName:
                    print("Processing lesion %s ..." % directoryName)
                    masksPath = os.path.join(PATH_TO_DATA, refPatient, directoryName)
                    lesion = Lesion(directoryName, masksPath)
                    patient.list_lesions.append(lesion)
                    extract_features(PATH_TO_EXTRACTION_PARAMS, lesion, patient.image)
    patients_dataFrame = convert_patients_list_to_dataFrame(list_patients)
    patients_dataFrame.to_csv(PATH_TO_FEATURES_CSV, sep=',', encoding='utf-8')

def extract_features(PATH_TO_EXTRACTION_PARAMS, lesion, image):
    '''Extract the features specified in the .yaml parameter file. Check radiomics extraction parameter for further
     information about extraction parameters. Extracted features are recorded in the dict_features of the
     lesion object'''
    extractor = featureextractor.RadiomicsFeaturesExtractor(PATH_TO_EXTRACTION_PARAMS)
    extractor.loadParams(paramsFile=PATH_TO_EXTRACTION_PARAMS)
    classNames = extractor.getFeatureClassNames()  # Not sure this line does anything
    features = extractor.execute(image, lesion.mask)
    for key in features:
        lesion.dict_features[key] = features[key]

def convert_patients_list_to_dataFrame(list_patients):
    '''Take a patient list containing each patients' lesion and associated feature, output a panda data frame.
     Each row contains the feature extracted from a patient lesion.'''
    list_series = []
    for patient in list_patients:
        for lesion in patient.list_lesions:
            serieIndex = patient.ref + " " + lesion.ref
            localSerie = pd.Series(lesion.dict_features, index=serieIndex)
            list_series.append(localSerie)
    patients_dataFrame = pd.DataFrame(list_series)
    return patients_dataFrame


if __name__ == '__main__':
    PATH_TO_DATA = "/Users/pops/Documents/ecn/projet/MYELOME/data/"
    PATH_TO_FEATURES_CSV = "/Users/pops/Documents/ecn/projet/MYELOME/extracted_features.csv"
    PATH_TO_EXTRACTION_PARAMS = "/Users/pops/Documents/ecn/projet/petml/code/extractionParams.yaml"
    run_extraction_pipe(PATH_TO_DATA, PATH_TO_FEATURES_CSV, PATH_TO_EXTRACTION_PARAMS)