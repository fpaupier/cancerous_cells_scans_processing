# Decision making tool for PET scans

## On the use of PET scans in oncology
_PET_  - Positron-emission tomography is a nuclear medicine functional imaging technique that is used to observe 
metabolic processes. PET scans are gray-scale images.


PET scans are particularly useful to detect myelomas - _advanced cancers with metastasis._
Indeed, organs and tissues consuming carbohydrate tend to be dark areas in PET scans. Myelomas are big consumers of
carbohydrates. Thus, PET scan are a weapon of choice to track myelomas in a patient scan.


## Goal of the project

This project aims to provide a code base to extract features from those PET scans.

First we will extract the feature and compare them with the values of reference papers. Then, we perform a feature selection.
A second project will use those selected features to train a machine learning algorithm 
(likely to be a _Random Survival Forest_ as it led to meaningful results in the case of lungs cancer detection).

The end goal of this second project is to classify lesions and predict patient survival time based on their PET scans.

## Library used

We used mainly the [pydicom](https://pydicom.github.io) and [pyradiomics](http://www.radiomics.io) to perform operations
on our medical data. (pile of gray-scale PET images that can be merged together to build a 3D model of the patient scanned)

## Data structure

For each patient in our data set, data are anonymised.

Per patient we have:
 - a pile of `.dicom` images.
 - a set of binary mask to cover the regions without lesions, so we could focus only on the region of interest.
 (The masks were drawn by professional oncologists)
 - Some reference features already computed for some regions of interests.
 - Time of patient's death relative to the date the scan has been taken (_e.g_ deceased 2 years after the last scan was taken)


---
# Code related info

## Directory organization

The project is currently divided into two  section : 

1. The *code* folder contains the extraction pipe and the associated lesion and patient class.
Use the code in this folder to compute features from a patients data set.
A few tests units are implemented (not exhaustive) to check for the global sanity of the code. 


2. The *docs* folder contains several publications used to motivate the choice of extraction features.`

---

## Setting up a virtual environment
*Guidelines adapted from the virtual env installation how-to for [TensorFlow](https://www.tensorflow.org/install/install_mac)*

We recommend the Virtualenv installation. Virtualenv is a virtual Python environment isolated from other Python development,
incapable of interfering with or being affected by other Python programs on the same machine. During the Virtualenv installation
 process, you will install all the packages required. (This is actually pretty easy.) 
 To start working with the feature extraction scripts, you simply need to "activate" the virtual environment. 
 All in all, Virtualenv provides a safe and reliable mechanism for installing and running scripts requiring specific packages.
 
 ### Installing Virtualenv
 Take the following steps to install TensorFlow with Virtualenv.
 1. Start a terminal (a shell). You'll perform all subsequent steps in this shell.
 2. Install pip and Virtualenv by issuing the following commands:
```
 $ sudo easy_install pip
 $ pip install --upgrade virtualenv 
```
 3. Create a Virtualenv environment by issuing the following command:
  *Note that the code is designed in Python 3 and is likely not to work on a Python 2.7 setup*
 ```
 $ virtualenv --system-site-packages -p python3 targetDirectory # for Python 3.n
 ```
 where targetDirectory identifies the top of the Virtualenv tree. Our instructions assume that targetDirectory is ~/medicalpy, like *medical python* but you may choose any directory.
 
 4. Activate the Virtualenv environment by issuing one of the following commands:
 ```
$ cd targetDirectory
$ source ./bin/activate      # If using bash, sh, ksh, or zsh
$ source ./bin/activate.csh  # If using csh or tcsh 
 ```
 The preceding source command should change your prompt to the following:
 ```
 (targetDirectory)$ 
 ```
 5. Ensure pip ≥8.1 is installed:
  ```
  (targetDirectory)$ easy_install -U pip
  ```
 6. Issue the following command to install all the packages required into the active Virtualenv environment:
  ```
  (targetDirectory)$ pip install -r /path/to/requirements.txt
  ```
  Where *requirements.txt* is the text file provided in the project containing the python package and version needed to run
  the scrips. 
  
 7. Installing pyradiomics. [Pyradiomics](http://pyradiomics.readthedocs.io/en/latest/)  is a python package used to extract features and cannot be installed simply with
 pip install. It has to be build from source. For an up to date installation procedure check [Pyradiomics Installation guide](http://pyradiomics.readthedocs.io/en/latest/installation.html)
 Issue the following command line to clone the pyradiomics repo from github :
 ```
 (targetDirectory)$ git clone git://github.com/Radiomics/pyradiomics
 ```
 
 8. Go to the downloaded pyradiomics folder:
 ```
 (targetDirectory)$ cd pyradiomics
 (targetDirectory)$ python -m pip install -r requirements.txt
 (targetDirectory)$ python setup.py install
 ```
 
 9. Check installation succeeded by running `pytest`.


## Bibliography
Bibliography is available in the `docs` folder. The different papers available define the features considered and the 
result one can possibly expect by using them to train a machine learning / pattern detection algorithm.

## Notes
This project was done in the context of my Master Thesis at Centrale Nantes.

This project is no longer updated.