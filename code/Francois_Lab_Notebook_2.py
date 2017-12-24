
# coding: utf-8

# # François' Dev Notebook 2
# 

# ### Pipeline implementation 
# The goal of this notebook is to build the pipeline required to process the PET scans. <br><br>
# INPUTS : <br>
# - pet scans of the patients
# - masks assosciated to the pet scans 
# 
# 
# OUTPUT : <br>
# - list of extracted features per scans & masks

# ### Step 1 :
# Calcul de la dimension (x,y,z) la plus grande entre tous les masques pour optimiser le calcul de la segmentation par consensus (deux méthodes : vote majoritaire et STAPLE). On utilise pour cela la macro "Crop1.ijm". Cette macro exemple prend en entrée 5 méthodes différentes (nous, nous en aurons 3). Elle sort un fichier "Log.txt" qui sera utilisée dans l'étape 3 

# ### Step 2 :
# "Crop" de tous les masques + de la pile DICOM pour la réduire aux dimensions maximales de la lésion en tenant compte de tous les masques. Au passage, la pile DICOM du patient est convertie de l'unité Bq/mL en une unité normalisée appelée SUV. La macro "Crop2.ijm" fait se travail

# ### Step 3 :
# Calcul de la segmentation par consensus par la méthode de vote majoritaire. Code => votemaj_clinique.py
# 

# ### Step 4 :
# Calcul de la segmentation par consensus par la méthode STAPLE. Code => staple_clinique.py 

# ### Step 5 :
# A ce stade, on se retrouve avec une pile DICOM réduite extraite de l'étape 2 et deux masques (un extrait de l'étape 3 et un extrait de l'étape 4).
# On peut alors charger l'un ou l'autre des masques + la pile DICOM réduite pour lancer pyradiomics et extraction de features.
# 
