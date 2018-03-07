# Decision making tool for PET scans

## Context

PET imaging is a valuable tool to diagnose and track patients with multiple myelomas (advanced cancers with metastasis).
PET images show lesions as dark regions.

## Goal

The goal of this project is to develop machine learning tools (*e.g.* SVMs or random forests) in order to classify lesions and predict the survival time.

## Tasks

- Bibliographic study
- Implement PET scans processing algorithms in Python to predict survival time

### Steps

1. Implement a pre-processing pipeline to extract the features from the patients' scans
2. Try different machine learning algorithms to compare prediction of estimated survival time against ground truth


Current step is step 1. 
To run the tests units, cd to the petml directory and run pytest.