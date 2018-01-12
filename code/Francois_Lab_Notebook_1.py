
# coding: utf-8

# # François' Dev Notebook 1
# 

# ### Un pipe mimimaliste
# L'objectif de ce notebook est de mettre en place un pipe qui prenne en input un jeu de données patient avec chacun une pile de dicom et un filtre assoscié afin d'en extraire les features.

# In[3]:


import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import cv2
import dicom
import dicom_numpy
import os
import radiomics
from skimage import io
import SimpleITK as sitk
import collections
import re


# In[84]:


PATH_TO_DATA  = "../../data/"


# Structure du dossier data :
# - xxx-xxx, correspond à un dossier patient (DP), plusieurs DP dans le dossier data
#     - dcm, dossier contenant la pile d'image dicom du patient
#     - lx, dossier contenant les lables des lésions du patients, un patient peut présenter plusieurs lésions. Chaque combinaison label-dcm fait l'objet d'un input différent. Dans un dossier patient, les dossier lésions respectent la forme l1, l2, .., ln où n est le nombre de lésions du patient.
#         - 2.5 dossier contenant les piles de masques 2.5
#         - 40 dossier contenant les piles de masques 40
#         - kmean.tif fichier masque kmean. 
#         
# Pseudo code du pipeline de traitement:

# # H1 High level
# 
# ``` 
# Pour chaque patients:
#     Ouvrir son dossier patient ( dossier à la nomenclature standardisé)
#     Pour chaque lésions:
#         Construction d'un masque par vote majoriatire à partir des 3 masques (kmean, 2.5, 40)
#         Appliquer le masque à la pile de dicom
#         extraire les caractéristiques pyradiomics de la lésion
# ```
# 
# ## H2 mid level
# 
# ```
# Pour chaque dossier patient dans le dossier data:
#     Créer un objet patient
#     Pour chaque dossier lésions dans le dossier patient:
#         Créer un objet lésion
#         Construire mask par méthode du vote majoritaire sur les 3 masques existants
#         Superposer le masque et la pile d'image dcm
#         Extraire les caractéristiques radiomics de la lésion
#         ajouter les caractéristiques voulues à l'objet lésion
# ```
# 
# ### H3 low level
# 
# ```
# Pour chaque dossier dans le dossier data:
#     Instancier un objet patient avec list_lesions vide
#     ajouter le patient à la liste de patients
#     Ouvrir le dossier dcm du dossier patient:
#         convertir la pile DCM sous la forme d'un voxel ndarray puis d'un sITK
#         Ajouter le sITK créer comme attribut image du patient
#     Pour chaque dosier dans le dossier patient:
#         Si le dossier a pour nom 'lx' avec x un entier:
#             Instancier un nouvel objet lésion:
#                Mettre l'attribut nom de la lésion comme le nom du dossier lx
#                Création du masque retenue par vote majoriateire
#                Mettre l'attribut mask de la lesions sous la forme d'un sITK
#             Superposer le masque et la lésion
#             Extraire les caractéristiques radiomics de la superposition
#             Set l'attribut features de la lesions
#             
#     
#     
# ```

# ## Quelques fonctions intermédiaires
# 
# ### Fonction dcmToSimpleITK
# Pour traiter une pile de dicom et en donner une image simpleITK qui peut être utilisé par pyradiomics
# 
# ### Fonction majorityVoteMask
# A partir d'un répertoire contenant plusieurs filtres, retourne le filtre sélectionné par la méthode du vote majoritaire, ce masque est retournée sous forme d'une image simpleITK qui peut être utilisé par pyradiomics

# In[118]:


def dcmToSimpleITK(dcmDirectory):
    '''Return sITK type image from a pile of dcm files'''
    list_dcmFiles = []
    for directory, subDirectory, list_dcmFileNames in os.walk(dcmDirectory):
        for dcmFile in list_dcmFileNames:
            list_dcmFiles.append(os.path.join(directory, dcmFile))
    dcmImage = [dicom.read_file(file) for file in list_dcmFiles]
    voxel_ndarray, ijk_to_xyz = dicom_numpy.combine_slices(dcmImage)
    sITK_image = sitk.GetImageFromArray(voxel_ndarray)
    return(sITK_image)
    


# In[126]:


def majorityVoteMask(masksPath):
    '''Compute the average mask based on the majority vote method from different masks from a lesion'''
    # CODE to build --> in a first instance i only use the kmean filter!
    mask_image = io.imread(masksPath + "/kmean.tif").T
    sITK_mask = sitk.GetImageFromArray(mask_image)
    return(sITK_mask)


# ### Définition des objets Patient et Lesion

# In[120]:


class Patient:

    def __init__(self, ref, image=None, list_lesions=[]):
        '''Provide ref number of the patient as a string "xxx-xxx", image must be simpleITK'''
        self.ref = ref
        self.list_lesions = list_lesions
        dcmDirectory = PATH_TO_DATA + ref + "/dcm/"
        self.image = dcmToSimpleITK(dcmDirectory)
        


# In[159]:


class Lesion:
    
    def __init__(self, ref, masksPath, list_features=[]):
        '''Provide ref number as string "lx", where x is the number of the lesion, masksPath is the path to the folder conatining the masks'''
        self.ref = ref
        self.mask = majorityVoteMask(masksPath)
        self.list_features = list_features #la liste des features à récupérer sera à définir avec Thomas


# In[169]:


#test

patient1 = Patient("001-026")
patient1.ref
patient1.image
print(patient1.image)

l1 = Lesion('l1')
print("Lesion %s" % l1.ref)


# ## Pipeline pour l'extraction automatisée de features
# A partir d'un dossier de patients suivant une architecture standardisée

# In[170]:


list_patients = []
for refPatient in os.listdir(PATH_TO_DATA):
    print("Processing patient %s ..." % refPatient)
    patient = Patient(refPatient)
    list_patients.append(patient)
    patient.list_lesions = []
    for directoryName in os.listdir(os.path.join(PATH_TO_DATA, patient.ref)):
        if directoryName != 'dcm' and directoryName != []:
            print("Processing lesion %s ..." % directoryName)
            masksPath = PATH_TO_DATA + refPatient + '/' + directoryName
            lesion = Lesion(directoryName, masksPath)
            patient.list_lesions.append(lesion)
            lesion.list_features
            
            #Extraction des features
            R = radiomics.featureextractor.RadiomicsFeaturesExtractor()
            R.enableAllFeatures()
            #print("Features name : ", R.getFeatureClassNames())
            R.getFeatureNames('glcm')
            glcm = radiomics.glcm.RadiomicsGLCM(patient.image, lesion.mask)
            lesion.list_features.append(glcm)
            


# _NB_  : Je suppose un bug sur la lésion l1 du patient 001-026, certaines valeurs du masque doivent être incohérentes car tous les autres masques fonctionnnent. Pour mes tests, j'ai déplacé cette data dans un donnée corrupted_data

# In[171]:


for patient in list_patients:
    print("Patient %s" % patient.ref)
    for lesion in patient.list_lesions:
        print('lesion %s' % lesion.ref)
        print('Autocorrelation : %f' % lesion.list_features[0].getAutocorrelationFeatureValue())
    print('\n')
    


# #### Création du masque
#  Attention aux dimensions, être sûr de bien reconnaître l'indice des axes x, y, z.
