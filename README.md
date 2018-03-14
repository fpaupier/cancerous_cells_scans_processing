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

1. Implement a pre-processing pipeline to extract the features from the patients' scans [ongoing]
2. Try different machine learning algorithms to compare prediction of estimated survival time against ground truth [To Do]


To run the tests units, cd to the petml directory and run pytest.

---

## Directory organization
The project is currently divided into two code section : 

1. The *refactored_code* folder containing the last version of our extraction pipe and the associated lesion and patient class.
A few tests units are implemented (not exhaustive) to check for the global sanity of the code. Use the code in this folder 
to compute features from a patients data set.

2. The old, deprecated, un-tested and buggy jupyter notebooks used to process the data are stored in the *deprecated_code* directory. 
They are not removed yet because they sometimes provide some insights on the dicom tags in a patient scan. 

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

