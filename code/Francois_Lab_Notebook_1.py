
# coding: utf-8

# # François' Dev Notebook 1
# 

# ### Un pipe mimimaliste
# L'objectif de ce notebook est de mettre en place un pipe qui prenne en input un jeu de données patient avec chacun une pile de dicom et un filtre assoscié afin d'en extraire les features.

# ### H3 low level implementation scheme
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

# In[1]:


import numpy as np
import dicom
import dicom_numpy
import os
import radiomics 
from skimage import io
import SimpleITK as sitk
import re
from skimage.external import tifffile


# In[1]:


PATH_TO_DATA  = "/home/popszer/Documents/ei3/petML/data/"


# ## Quelques fonctions intermédiaires 
# --> a déplacer dans un fichier utils que l'on appelera depuis le fichier principale
# 
# ### Fonction dcmToSimpleITK
# Pour traiter une pile de dicom et en donner une image simpleITK qui peut être utilisé par pyradiomics
# 
# ### Fonction majorityVote
# A partir de 3 masques au format .tif, retourne le filtre sélectionné par la méthode du vote majoritaire, ce masque est retournée sous forme d'une image simpleITK qui peut être utilisé par pyradiomics
# 
# ### Fonction getTifMasks
# A partir d'un dossier lésion, la fonction getTifMasks renvoie les 3 masques 40, 2.5 et kmean au format .tif 
# 
# ### Fonction makeTifFromPile 
# A partir d'une pile de masque, la fonction makeTifFromPile créer un masque au format.tif et le place dans le dossier racine de la lésion. Cette fonction prend en entrée le chemin vers la pile de fichiers à convertir en .tif. makeTifFromPile retourne le chemin vers le nouveau masque au format tif créé

# In[3]:


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

# In[4]:


def getTifMasks(masksPath):
    '''Return path toward the KMean, 40 and 2.5 mask respectively in this order'''
    list_files = [file for file in os.listdir(masksPath) if os.path.isfile(os.path.join(masksPath, file))]
    mask40Name = '40.tif' 
    mask25Name = '25.tif' 
    pathToKmeanMask = masksPath + '/kmean.tif'
    if mask40Name in list_files:
        pathTo40Mask = os.path.join(masksPath, mask40Name)
        print(pathTo40Mask)
    else:
        pathTo40Mask = makeTifFromPile(os.path.join(masksPath, "40"))
    if mask25Name in list_files:
        pathTo25Mask = os.path.join(masksPath, mask25Name)
    else:
        pathTo25Mask = makeTifFromPile(os.path.join(masksPath, '2.5'))
    return(pathToKmeanMask, pathTo40Mask, pathTo25Mask)


# In[5]:


def getWords(text):
    return re.compile('\w+').findall(text)


# In[6]:


def makeTifFromPile(pathToPile):
    '''Takes an absoulte path containing a pile of masks, compute the resulting .tif mask and output the path to the created .tif mask '''
    list_pileFiles = []
    for dirpath,dirnames,fileNames in os.walk(pathToPile):
        for file in fileNames:
            list_pileFiles.append(os.path.join(dirpath,file))
    list_pileFilesAsArray = []
    
    first_file = list_pileFiles[0]
    #get the shape of the image
    with open(first_file, mode='r', encoding='utf-8') as file:
        file.readline()#first line is junk data
        shapeLocalMask = getWords(file.readline()) #secondline is shape of the dcm pile
        xShape = int(shapeLocalMask[0])
        yShape = int(shapeLocalMask[1])
        mask_size = (xShape, yShape)
    
    num_file = len(list_pileFiles)
    mask_array = np.zeros((num_file, xShape, yShape))
    fileIndex = num_file-1
    for pileFile in list_pileFiles:
        with open(pileFile, mode='r', encoding='utf-8') as file:
            file.readline() #junk line
            file.readline() #secondline is shape of the dcm pile
            file.readline() # 3 lines of junk data
            for rowIndex in range(xShape):
                for colIndex in range(yShape):
                    val = file.read(1)
                    while (val!='0' and val!='1'):
                        val = file.read(1)
                    mask_array[fileIndex,rowIndex, colIndex] = int(val)
            fileIndex = fileIndex - 1

    pathToLesion = os.path.abspath(os.path.join(pathToPile, os.pardir))

    if('2.5' in pathToPile):
        pathToTifMask = os.path.join(pathToLesion, '25.tif')
    if('40' in pathToPile):
        pathToTifMask = os.path.join(pathToLesion, '40.tif')
        
    tifffile.imsave(pathToTifMask, mask_array)
    return pathToTifMask


# In[7]:


masksPath = PATH_TO_DATA + "001-026/l2"
getTifMasks(masksPath)


# In[8]:


maskKmean = tifffile.imread(PATH_TO_DATA + '001-026/l2/kmean.tif')
mask40 = tifffile.imread(PATH_TO_DATA + '001-026/l2/40.tif')


# In[9]:


print('Kmean : ',maskKmean.shape,' \n40 : ', mask40.shape)


# ### majorityVote implementation
# 
# Le calcul du mask résultant par vote_maj se fait sur des fichiers en .tif

# In[18]:


def majorityVote(masksPath):
    print(masksPath)
    '''Compute the average mask based on the majority vote method from different masks from a lesion'''
    #TO DO : Add a a safety check to make sure weuse the file Result.tiff, if it exists in the masksPath directory. 
    # this mask corresponds to the resulting voteMaj mask. No need to recompute it.
    
    # Import des 3 masques tif
    (pathToKmeanMask, pathTo40Mask, pathTo25Mask) = getTifMasks(masksPath)
    
    mkmean = io.imread(pathToKmeanMask).T
    m25 = io.imread(pathTo40Mask).T
    m40 = io.imread(pathTo25Mask).T
    
    # Paramètres
    ACCEPT = 0.33  # seuil d'acceptation pour que le voxel appartienne à la lésion ou au fond, valeur donnée par Thomas 0.45
    nbmethods = 3  # Nombre de methodes (40%, 2.5 et kmean)
    
    # Dimensions
    imageDims = mkmean.shape
    
    # Image binaire segmentée selon vote majoritaire
    mMajority = np.zeros(imageDims)

    somme = m40[:,:,:mkmean.shape[2]] + m25[:,:,:mkmean.shape[2]] + mkmean
    somme /= nbmethods

    mMajority[somme >= ACCEPT] = 1 #Vectorized method
    
    # print("somme shape", somme.shape) #element wise method
    # for xindex, x in enumerate(somme):
    #     for yindex, y in enumerate(x):
    #         for zindex, z in enumerate(y):
    #             #if z != 0:
    #              #   print(z)
    #               #  mMajority[xindex, yindex, zindex] = 1
    #             if z >= ACCEPT:
    #                 mMajority[xindex, yindex, zindex] = 1

    
    sITK_mask = sitk.GetImageFromArray(mMajority)
    
    majorityTiffPath = os.path.join(masksPath, "majority.tif")
    tifffile.imsave(majorityTiffPath, mMajority)
    
    return sITK_mask


# In[19]:


class Patient:

    def __init__(self, ref, image=None, list_lesions=[]):
        '''Provide ref number of the patient as a string "xxx-xxx", image must be simpleITK'''
        self.ref = ref
        self.list_lesions = list_lesions
        dcmDirectory = os.path.join(PATH_TO_DATA, ref, "dcm")
        self.image = dcmToSimpleITK(dcmDirectory)
        


# In[20]:


class Lesion:
    
    def __init__(self, ref, masksPath):
        '''Provide ref number as string "lx", where x is the number of the lesion, masksPath is the path to the folder conatining the masks'''
        self.ref = ref
        self.mask = majorityVote(masksPath)
        self.dico_features = {} #la liste des features à récupérer sera à définir avec Thomas


# In[21]:


PARAM_PATH = "/home/popszer/Documents/ei3/petML/extractionParams.yaml"


# In[22]:


#test du focntionnement de l'extarctionà partir d'un fichier de paramètres en .yaml
# objectif d'intancier un extracteur auquel on fourni la liste des features à extraire
# en dehors du code pour plus de flexibilité.

patient1 = Patient("001-026")
patient1.ref
patient1.image
lesion = Lesion("l7", "/home/popszer/Documents/ei3/petML/data/001-026/l7")
print('Image patient  %s' % type(patient1.image))
print('Image lésion %s' % type(lesion.mask))
#lesion.mask = sitk.GetImageFromArray(io.imread("/home/popszer/Documents/ei3/petML/data/001-026/l7/kmean.tif").T)
print("Superposition des masques")



#extractor = featureextractor.RadiomicsFeaturesExtractor(PARAM_PATH)
###


# This cell is equivalent to the previous cell
extractor = radiomics.featureextractor.RadiomicsFeaturesExtractor(binWidth=20, sigma=[1, 2, 3], verbose=True)  # Equivalent of code above


###
result = extractor.execute(patient1.image, lesion.mask)
print(type(result))
print ("Calculated features")
for key, value in result.items():
    print ("\t", key, ":", value)


# ### Fonction extraction des features pour une lésion

# In[23]:


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

# In[24]:


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

# In[25]:


for patient in list_patients:
    for lesion in patient.list_lesions:
        print(patient.ref)
        print(lesion.ref)
        print(lesion.dico_features)

