


import dicom
import os
from radiomics import featureextractor
from skimage import io
import SimpleITK as sitk
from skimage.external import tifffile

PATH_TO_DATA  = "/Users/pops/Documents/ecn/projet/MYELOME/" 


dcmDirectory = "/Users/pops/Documents/ecn/projet/MYELOME/050-004/dcm"

list_dcmFiles = []
for directory, subDirectory, list_dcmFileNames in os.walk(dcmDirectory):
    for dcmFile in list_dcmFileNames:
        if not dcmFile.startswith('.'):
            list_dcmFiles.append(os.path.join(directory, dcmFile))
pathToDcmSlice = list_dcmFiles[0]
print(pathToDcmSlice)  

print('Before conversion')
dcmSlice = dicom.read_file(pathToDcmSlice)
units = dcmSlice[0x00541001].value.lower() 
print('unit : %s' % units)

#setSliceUnitToSUV(pathToDcmSlice)
print('After conversion')
dcmSlice = dicom.read_file(pathToDcmSlice)
dcmSlice = dicom.re
units = dcmSlice[0x00541001].value.lower() 
print('unit : %s' % units)


# In[113]:




# In[114]:


#Test multiplySlice

scalar = 1.6

dcmDirectory = "/Users/pops/Documents/ecn/projet/MYELOME/050-004/dcm"

print('before conversion')
list_dcmFiles = []
for directory, subDirectory, list_dcmFileNames in os.walk(dcmDirectory):
    for dcmFile in list_dcmFileNames:
        if not dcmFile.startswith('.'):
            list_dcmFiles.append(os.path.join(directory, dcmFile))
pathToDcmSlice = list_dcmFiles[0]
print(pathToDcmSlice)  

print("before multiplication")
dcmSlice = dicom.read_file(pathToDcmSlice)
units = dcmSlice[0x00541001].value.lower() 
print('unit : %s' % units)
counter = 0
for x in dcmSlice.pixel_array:
    for y in x:
        if y!=0 and counter < 5:
            counter = counter + 1 
            print(y)
    
print("After multiplication")
multiplySlice(scalar,pathToDcmSlice)
dcmSlice = dicom.read_file(pathToDcmSlice)
units = dcmSlice[0x00541001].value.lower() 
print('unit : %s' % units)
counter = 0
for x in dcmSlice.pixel_array:
    for y in x:
        if y!=0 and counter < 5:
            counter = counter + 1 
            print(y)


# In[59]:





# In[69]:



                
                


# In[70]:


# Bloc test for bqml to SUV conversion

dcmDirectory = "/Users/pops/Documents/ecn/projet/MYELOME/050-004/dcm"

print('before conversion')
list_dcmFiles = []
for directory, subDirectory, list_dcmFileNames in os.walk(dcmDirectory):
    for dcmFile in list_dcmFileNames:
        if not dcmFile.startswith('.'):
            list_dcmFiles.append(os.path.join(directory, dcmFile))
            
dcmSlice = dicom.read_file(list_dcmFiles[0])

units = dcmSlice[0x00541001].value.lower() 
print('unit : %s' % units)
counter = 0
for x in dcmSlice.pixel_array:
    for y in x:
        if y!=0 and counter < 5:
            counter = counter + 1 
            print(y)
            
print('Conversion')

convertToSUV(dcmDirectory)

list_dcmFiles = []
for directory, subDirectory, list_dcmFileNames in os.walk(dcmDirectory):
    for dcmFile in list_dcmFileNames:
        if not dcmFile.startswith('.'):
            list_dcmFiles.append(os.path.join(directory, dcmFile))
dcmSlice = dicom.read_file(list_dcmFiles[0])

units = dcmSlice[0x00541001].value.lower() 
print('unit : %s' % units)
counter = 0
for x in dcmSlice.pixel_array:
    for y in x:
        if y!=0 and counter < 5:
            counter = counter + 1 
            print(y)


# In[75]:


# Bloc test for bqml to SUV conversion

dcmDirectory = "/Users/pops/Documents/ecn/projet/MYELOME/050-004/dcm"

print('before conversion')
list_dcmFiles = []
for directory, subDirectory, list_dcmFileNames in os.walk(dcmDirectory):
    for dcmFile in list_dcmFileNames:
        if not dcmFile.startswith('.'):
            list_dcmFiles.append(os.path.join(directory, dcmFile))
            
dcmSlice = dicom.read_file(list_dcmFiles[0])
print(dcmSlice)
units = dcmSlice[0x00541001].value.lower() 
print('unit : %s' % units)

print('delta computation')
acquisitionHour = int(dcmSlice[0x00080031].value[0:2])
acquisitionMinute = int(dcmSlice[0x00080031].value[2:4])
injectionHour = int(dcmSlice[0x00540016].value[0][0x00181072].value[0:2])
injectionMinute = int(dcmSlice[0x00540016].value[0][0x00181072].value[2:4])
        
deltaHour = acquisitionHour - injectionHour
deltaMinute = acquisitionMinute - injectionMinute 
if (deltaMinute < 0):
                deltaMinute = 60 + deltaMinute
                deltaHour = deltaHour - 1


print('dhour : %i, dminute : %i' % (deltaHour, deltaMinute))
for x in dcmSlice.pixel_array:
    for y in x:
        if y!=0:
            print(y)
            


# In[101]:


#Extraction de feature depuis l'image standardisée
(pathToKmeanMask, pathTo40Mask, pathTo25Mask) = getTifMasks("/Users/pops/Documents/ecn/projet/MYELOME/050-004/l2")
dcmDirectory = "/Users/pops/Documents/ecn/projet/MYELOME/050-004/dcm"
image = dcmToSimpleITK(dcmDirectory)
mask = sitk.GetImageFromArray(io.imread(pathToKmeanMask).T)

print("Superposition des masques")



extractor = featureextractor.RadiomicsFeaturesExtractor(PARAM_PATH)
extractor.loadParams(paramsFile=PARAM_PATH)
classNames = extractor.getFeatureClassNames()
features = extractor.execute(image, mask)
for key in features:
    print("%s: %s \n" % (key, features[key]))


# In[78]:


### Test bloc ### 

pathToSlice = os.path.join(PATH_TO_DATA,"050-004/dcm/PI.1.3.46.670589.28.2.15.2199422639.3.82.0.13067747800.dcm")
dcmSlice = dicom.read_file(pathToSlice)
print(dcmSlice.PatientName,
     dcmSlice.RescaleSlope)
print(dcmSlice[0x00100010])
print(dcmSlice[0x18,0x50])
print(dcmSlice)
print("######## HERE ########")

patientMass = float(dcmSlice[0x00101030].value)
print(patientMass)


# In[79]:





# #2 Fonction intermediaire getTifMasks
# ```
# Ouverture du dossier lesion:
# 
# Si il existe un fichier 25.tif:
#     assigner le chemin vers ce fichier à la variable pathToMask25Tif
# Sinon ouvrir le dossier 25:
#     construire .tif à partir de la pile
#     assigner le chemin vers ce fichier à la variable pathToMask25Tif
#     
# Si il existe un fichier 40.tif:
#     assigner le chemin vers ce fichier à la variable pathToMask40Tif
# Sinon ouvrir les dossiers 40 
#     construire .tif à partir de la pile
#     assigner le chemin vers ce fichier à la variable pathToMask40Tif
#     
# retourner les 3 masques en .tif
# ```

# In[80]:



# In[81]:



# In[82]:




# In[83]:


masksPath = PATH_TO_DATA + "001-060/l1"
getTifMasks(masksPath)


# In[84]:


maskKmean = tifffile.imread(PATH_TO_DATA + '001-060/l1/kmean.tif')
mask40 = tifffile.imread(PATH_TO_DATA + '001-060/l1/40.tif')


# In[85]:


print('Kmean : ',maskKmean.shape,' \n40 : ', mask40.shape)


# ### majorityVote implementation
#
# In[86]:

# Le calcul du mask résultant par vote_maj se fait sur des fichiers en .tif





# In[87]:





# In[88]:





# In[89]:


PARAM_PATH = "/Users/pops/Documents/ecn/projet/petml/deprecated_code/extractionParams.yaml"


# In[98]:


#test du focntionnement de l'extarctionà partir d'un fichier de paramètres en .yaml
# objectif d'intancier un extracteur auquel on fourni la liste des features à extraire
# en dehors du deprecated_code pour plus de flexibilité.
ref = "050-004"
patient1 = Patient(ref)
patient1.ref
patient1.image
#lesion1 = Lesion("l2", "/Users/pops/Documents/ecn/projet/MYELOME/001-060/l2")
print('Image patient  %s' % type(patient1.image))
#print('Image lésion %s' % type(lesion1.mask))
mask = sitk.GetImageFromArray(io.imread("/Users/pops/Documents/ecn/projet/MYELOME/" + ref + "/l2/kmean.tif").T)
#lesion1.mask = sitk.GetImageFromArray(io.imread("/Users/pops/Documents/ecn/projet/MYELOME/001-060/l2/kmean.tif").T)
print("Superposition des masques")



#extractor = featureextractor.RadiomicsFeaturesExtractor(PARAM_PATH)
###


# Test extraction of features from a mask + image
# Extraction pipe params yaml
extractor = featureextractor.RadiomicsFeaturesExtractor(PARAM_PATH)
extractor.loadParams(paramsFile=PARAM_PATH)
classNames = extractor.getFeatureClassNames() # Not sure this line does anything
features = extractor.execute(patient1.image, mask)
for key in features:
    print("%s: %s \n" % (key, features[key]))


# ### Fonction extraction des features pour une lésion

# In[91]:


def setFeatures(dico_features, image, mask, paramPath):
    
    # Instantiate the extractor
    extractor = radiomics.featureextractor.RadiomicsFeaturesExtractor(paramPath)
    R = radiomics.glcm.RadiomicsGLCM(image, mask)
    dico_features["Autocorrelation"] = R.getAutocorrelationFeatureValue()
    dico_features["ClusterProminence"] = R.getClusterProminenceFeatureValue()
    dico_features["ClusterShade"] = R.getClusterShadeFeatureValue()
    dico_features["Contrast"] = R.getContrastFeatureValue()
    dico_features["Correlation"] = R.getCorrelationFeatureValue()
    dico_features["DifferenceEntropy"] = R.getDifferenceEntropyFeatureValue()
    dico_features["DifferenceVariance"] = R.getDifferenceVarianceFeatureValue()
    
    return dico_features


# ## Pipeline pour l'extraction automatisée de features
# A partir d'un dossier de patients suivant une architecture standardisée

# In[92]:


list_patients = []
for refPatient in os.listdir(PATH_TO_DATA):
    print("Processing patient %s ..." % refPatient)
    patient = Patient(refPatient)
    list_patients.append(patient)
    patient.list_lesions = []
    for directoryName in os.listdir(os.path.join(PATH_TO_DATA, patient.ref)):
        if directoryName != 'dcm' and directoryName != []:
            print("Processing lesion %s ..." % directoryName)
            masksPath = os.path.join(PATH_TO_DATA, refPatient, directoryName)
            lesion = Lesion(directoryName, masksPath)
            patient.list_lesions.append(lesion)

            lesion.dico_features = setFeatures(lesion.dico_features, patient.image, lesion.mask, PARAM_PATH)
            


# _NB_  : Je suppose un bug sur la lésion l1 du patient 001-026, certaines valeurs du masque doivent être incohérentes car tous les autres masques fonctionnnent. Pour mes tests, j'ai déplacé cette data dans un donnée corrupted_data

# In[94]:


for patient in list_patients:
    for lesion in patient.list_lesions:
        print(patient.ref)
        print(lesion.ref)
        print(lesion.dico_features)

