# coding: utf-8

###
# run-pipe.py -
# This file handle the running of the extraction pipe (computation of features per lesion) through specifying the
# arguments through command line.
#
# Author : François Paupier - francois.paupier@gmail.com
#
# Created on : 13/03/2018
###

import argparse
from feature_extractor import run_extraction_pipe

PATH_TO_DATA = 'C:/Users/mathi_000/jupyter/Projet/data/'

def main():

    parser = argparse.ArgumentParser(
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--data_dir', type=str, default=PATH_TO_DATA,
                        help='Data directory containing patients folder')
    parser.add_argument('--feature_csv', type=str, default='extracted_features.csv',
                        help='CSV containing the features extracted from the lesions')
    parser.add_argument('--params', type=str, default='extractionParams.yaml',
                        help='Path to the extraction parameter files (.yaml file)')
    args = parser.parse_args()

    run_extraction_pipe(args.data_dir, args.feature_csv, args. params)


if __name__ == "__main__":
    main()
