# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 13:33:50 2018

@author: ludiv
"""
import os
from random import randint
from skimage import io
import numpy as np
from Patient import initializePatientImage

import SimpleITK as sitk 

import radiomics
from radiomics import featureextractor

from sklearn.ensemble import RandomForestClassifier
import csv
import pandas as pd

from sklearn import svm
from sklearn.metrics import roc_auc_score
#%%
# Choix patient test ##########################################################
PATH_TO_DATA = 'C:/Users/ludiv/Documents/Aide_au_diag/Data/Patients/'

def test_choice(PATH_TO_DATA): #to choice which patient between five will be use for test and others (4) will be use for training
    print ('Test choice')
    list_ref = []
    for patient in os.listdir(PATH_TO_DATA):
        list_ref.append(patient) #liste nom patients
    i=randint(0,len(list_ref)-1)
    patient_test = list_ref[i]
    patient_train=list_ref
    del patient_train[i]
    print('        choose patient : ',patient_test)
    return patient_train, patient_test #give patients train list and patient test list

def padding(image,k): #padding to permit to take in count edges
    pad_image=np.pad(image,((0,2*k),(0,2*k),(0,2*k)),mode = 'symmetric')
    return pad_image


def calcul_ratio(patch): #calculation of the ratio of positive patchs in a list
    nb_pos=len(np.where(patch!=0))
    nb_neg=len(np.where(patch==0))
    ratio=nb_pos/(nb_pos+nb_neg)
    return ratio

def patch_creation(x,y,z,k,image): #to create a patch from the patient image
    patch = np.ones((2*k+1,2*k+1,2*k+1))
    for xp in range(patch.shape[0]):
        for yp in range(patch.shape[1]):
            for zp in range(patch.shape[2]):
                patch[xp][yp][zp]=image[xp+x][yp+y][zp+z]
    return patch

# Recherche patch aléatoires ##################################################
#recherche lesion
#liste coordonnées dans patch et autour ( tout ce qui est positif)
#prendre aléatoirement un certain nombre de patchs dans cette liste et le reste dans le corps mais en dehors de ces patchs

def positive_patch(mask,k,pourcent_ratio,pd_mask): #taille patch = 2k+1
    '''donne liste des patchs positifs du mask 3D'''
    print('     Looking for positives patchs ...')
    indice=np.where(mask!=0)
    min_x=indice[0].min()
    max_x=indice[0].max()
    min_y=indice[1].min()
    max_y=indice[1].max()
    min_z=indice[2].min()
    max_z=indice[2].max()
    
    sup=int(pourcent_ratio*(2*k+1)+1)
    liste_pos=[]
    liste_coord_pos=[]
    for x in range(min_x-sup,max_x+sup) :
        for y in range(min_y-sup,max_y+sup):
            for z in range(min_z-sup,max_z+sup) :
                patch = patch_creation(x,y,z,k,pd_mask)
                if calcul_ratio(patch)>= pourcent_ratio : 
                    liste_coord_pos.append((x,y,z))
                    liste_pos.append(patch)
    return liste_pos, liste_coord_pos      
        
#prendre aléatoirement 50% dans liste_pos et 50 dans le reste tant que ce n'est pas dans l'image.
    
def random_patch(mask,k, pourcent_ratio, nb_patch,image,pd_image,pd_mask):
    ''' pour une lesion, avoir une liste de patchs (equivalents pos/neg) aléatoires avec leur valeur pos/neg associée'''
    print('creation of random patches list ...')
    nb_pos=nb_patch//2
    nb_neg = nb_patch - nb_pos
    liste_pos, liste_coord_pos = positive_patch(mask,k,pourcent_ratio,pd_mask)
    liste_patch_coord=[]
    liste_indice = []
    liste_value=[]
    liste_patch=[]
    while len(liste_indice) < nb_pos :
        i = randint(0,len(liste_pos))
        if i not in liste_indice :
            liste_indice.append(i)
            liste_patch.append(liste_pos[i])
            liste_patch_coord.append(liste_coord_pos[i])
            liste_value.append(1)
    c=0
    while c < nb_neg :
        x=randint(0,len(image)-(2*k))
        y=randint(0,len(image[0])-2*k)
        z=randint(0,len(image[0][0])-2*k)
        if (x,y,z) not in liste_coord_pos:
            patch = patch_creation(x,y,z,k,pd_image)
            liste_patch_coord.append((x,y,z))
            liste_patch.append(patch)
            liste_value.append(0)
            c=c+1
            
    return liste_patch_coord,liste_value, liste_patch

def all_patch(mask,k, pourcent_ratio, nb_patch,nim,pd_image,pd_mask):
    '''avoir tous les patchs d'une image'''
    liste_patch=[]
    liste_patch_value=[]
    liste_patch_coord=[]
    for x in range(0,len(nim),(2*k+1)):
        for y in range(0,len(nim[0]),(2*k+1)):
            for z in range(0,len(nim[0][0]),(2*k+1)):
#                print(x,y,z)
#                print(len(pd_image),len(pd_image[0]),len(pd_image[0][0]))
                patch=patch_creation(x,y,z,k,pd_image)
                liste_patch.append(patch)
                liste_patch_coord.append((x,y,z))
                if calcul_ratio(patch)>= pourcent_ratio :
                    liste_patch_value.append(1)
                else :
                    liste_patch_value.append(0)
    return liste_patch, liste_patch_value, liste_patch_coord

#%% 


# Création liste patchs training ##############################################

def create_train(patient_train,k, pourcent_ratio, nb_patch):            
    liste_patch_train=[]
    liste_patch_train_val=[]
    for patient in patient_train:
        print(patient, '.......................................................')
        image3D = initializePatientImage(os.path.join(PATH_TO_DATA,patient,'dcm'))
        nim = sitk.GetArrayFromImage(image3D)
        pd_image = padding(nim,k)
        for lesion in os.listdir(os.path.join(PATH_TO_DATA,patient)):
            print(lesion, '..............................')
            if 'majority.tif' in os.listdir(os.path.join(PATH_TO_DATA,patient,lesion)):
                mask=io.imread(os.path.join(PATH_TO_DATA,patient,lesion,'majority.tif')).T
                pd_mask=padding(mask,k)
                liste_patch_coord,liste_value, liste_patch = random_patch(mask,k, pourcent_ratio, nb_patch,nim,pd_image,pd_mask)
                liste_patch_train.extend(liste_patch)
                liste_patch_train_val.extend(liste_value)
    return liste_patch_train, liste_patch_train_val



# Création patch test #########################################################

def create_test(patient_train,patient_test,k,pourcent_ratio,nb_patch):
    image3D = initializePatientImage(os.path.join(PATH_TO_DATA,patient_test,'dcm'))
    nim = sitk.GetArrayFromImage(image3D)
    pd_image = padding(nim,k)
    liste_patch_test=[]
    liste_patch_test_val=[]
    liste_patch_test_coord=[]
    for lesion in os.listdir(os.path.join(PATH_TO_DATA,patient_test)):
        print(lesion, '...................')
        if 'majority.tif' in os.listdir(os.path.join(PATH_TO_DATA,patient_test,lesion)):
            mask=io.imread(os.path.join(PATH_TO_DATA,patient_test,lesion,'majority.tif')).T
            pd_mask=padding(mask,k)
            liste_patch, liste_patch_value, liste_patch_coord = all_patch(mask,k, pourcent_ratio, nb_patch,nim,pd_image,pd_mask)
            liste_patch_test.extend(liste_patch)
            liste_patch_test_val.extend(liste_patch_value)
            liste_patch_test_coord.extend(liste_patch_coord)
    return liste_patch_test, liste_patch_test_val, nim, liste_patch_test_coord

# Calcul features #############################################################

def features_calculation(patch_size,liste_patch):
    print("Calculation of features ...")
    valeurs_features = []    
    for k in range(len(liste_patch)):
        liste_var=[]
        patch= liste_patch[k]
        masque_patch=np.ones((patch_size,patch_size,patch_size))
        patch_sitk=sitk.GetImageFromArray(patch)
        masque_patch_sitk=sitk.GetImageFromArray(masque_patch)
        extractor = radiomics.firstorder.RadiomicsFirstOrder(patch_sitk,masque_patch_sitk)
        entropy = extractor.getEntropyFeatureValue()
        maximum = extractor.getMaximumFeatureValue()
        
        # GLCM features
        extractor = radiomics.glcm.RadiomicsGLCM(patch_sitk,masque_patch_sitk)
        homogenity = extractor.getIdFeatureValue()
        dissimilarity = extractor.getDifferenceAverageFeatureValue()
    
         # GLRLM features
        extractor = radiomics.glrlm.RadiomicsGLRLM(patch_sitk,masque_patch_sitk)
        HGLRE = extractor.getHighGrayLevelRunEmphasisFeatureValue()
        
         # GLSZM features
        extractor = radiomics.glszm.RadiomicsGLSZM(patch_sitk,masque_patch_sitk)
        ZLNU = extractor.getSizeZoneNonUniformityFeatureValue()
        SZHGE = extractor.getSmallAreaHighGrayLevelEmphasisFeatureValue()
        ZP = extractor.getZonePercentageFeatureValue()
        
        liste_var=[np.mean(patch),np.min(patch), np.median(patch),entropy, maximum,homogenity, dissimilarity,HGLRE, ZLNU, SZHGE, ZP ]
        valeurs_features.append(liste_var)
            
    return valeurs_features

def csv_creation(valeurs,name):  #create csv file with extracted features
    with open(name, 'w', newline='') as csvfile:
        fieldnames = ['Mean','Min','Median','Entropy','Maximum','homogenity','dissimilarity','HGLRE','ZLNU','SZHGE','ZP']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for valeur in valeurs :
            writer.writerow({'Mean': valeur[0] , 'Min': valeur[1], 'Median' : valeur[2],'Entropy' : valeur[3] , 'Maximum' : valeur[4] , 'homogenity' : valeur[5],'dissimilarity' : valeur[6],'HGLRE' : valeur[7],'ZLNU' : valeur[8],'SZHGE' : valeur[9],'ZP' : valeur[10]})
    print("     Features extraction done")

#%%
# Machine learning ############################################################
    
    
def random_forest(train_x,train_y,test_x,test_y):
    print("Random Forest processing ...")
    
    model = RandomForestClassifier()
    model.fit(train_x,train_y)
    
    print ("Trained model :: ", model)
    predictions = model.predict(test_x)
    
    for i in range(0, 5):
        print ("Actual outcome :: ", test_y[i], ' and Predicted outcome :: ', predictions[i])
    fieldnames = ['Mean','Min','Median','Entropy','Maximum','homogenity','dissimilarity','HGLRE','ZLNU','SZHGE','ZP']

    #y_oob=model.
    #print('         auc score : ',roc_auc_score(y,y_oob))
        
    pourr=0
    for i in range(len(test_y)):
        if int(test_y[i])==int(predictions[i]):
            pourr=pourr+1 #to count the number of good results
    pr=pourr/len(test_y)*100
    print("     pourcent of good résults : ", pr,"%")
    features_importance= pd.Series(model.feature_importances_, index=fieldnames)
    features_importance.sort_values()
    features_importance.plot(kind='barh')
    print("    Random Forest done")

    return model,predictions,pr

def svm_method(k,liste_patch_train, liste_patch_train_val, liste_patch_test, liste_patch_test_val):
    print('SVM processing ...')
    nombre_patch=len(liste_patch_train)
    
    train_x=np.array(liste_patch_train)
    patch_pixel=(2*k+1)**3
    rs_train_x=[]
    for i in range(len(train_x)):
        s=np.reshape(train_x[i],(patch_pixel))
        rs_train_x.append(s)
    train_y=liste_patch_train_val
    np.reshape(train_y,(nombre_patch))

    test_x=np.array(liste_patch_test)
    patch_pixel=(2*k+1)**3
    rs_test_x=[]
    for i in range(len(test_x)):
        s=np.reshape(test_x[i],(patch_pixel))
        rs_test_x.append(s)
    test_y=liste_patch_test_val
    np.reshape(test_y,(len(test_y)))
    
    clf = svm.SVC(kernel='linear', C = 1.0)
    clf.fit(rs_train_x,train_y)
    
    result = clf.predict(rs_test_x)
    pourc=0
    for i in range(len(result)):
        if result[i]==test_y[i]:
            pourc=pourc+1 #to count the number of good results
    p=pourc/len(result)*100
    print("     pourcent of good results : ", p,"%")
    print("SVM done")
    return result, p, clf


#%%
#def main(pourcent_ratio =0.4, k=4, nb_patch = 10):
##################        Main        ##########################################
#
#    patient_train, patient_test = test_choice(PATH_TO_DATA)  
#    print(' .............. TRAIN LIST CREATION................................')     
#    liste_patch_train, liste_patch_train_val=create_train(patient_train,k, pourcent_ratio, nb_patch)
#    print(' .............. TEST LIST CREATION .................................')
#    liste_patch_test, liste_patch_test_val, image_patient_test, liste_patch_coord = create_test(patient_train,patient_test,k,pourcent_ratio,nb_patch)
#    print(' .............. FEATURES EXTRACTION ...............................')
#    valeurs_features_train=features_calculation(2*k+1,liste_patch_train)
#    csv_creation(valeurs_features_train,'extraction_train.csv')
#    valeurs_features_test=features_calculation(2*k+1,liste_patch_test)
#    csv_creation(valeurs_features_test,'extraction_test.csv')
#    print(' .............. RANDOM FOREST ..................................')
#    model,predictions,pr =random_forest(valeurs_features_train,liste_patch_train_val,valeurs_features_test,liste_patch_test_val)
#    print(' .......................... SVM ................................')
#    result, p, clf=svm_method(k,liste_patch_train, liste_patch_train_val, liste_patch_test, liste_patch_test_val)

###############################################################################
if __name__ == "__main__":
#    main()
    pourcent_ratio =0.4 #ratio de patchs test par rapport au nombre total de patchs
    k=2 #taille du patch (patch 3D a pour shape (2*k+1,2*k+1,2*k+1))
    nb_patch = 50
    
    patient_train, patient_test = test_choice(PATH_TO_DATA)  
    
    print(' .............. TRAIN LIST CREATION................................')     
    liste_patch_train, liste_patch_train_val=create_train(patient_train,k, pourcent_ratio, nb_patch)
    
    print(' .............. TEST LIST CREATION .................................')
    liste_patch_test, liste_patch_test_val, image_patient_test, liste_patch_coord = create_test(patient_train,patient_test,k,pourcent_ratio,nb_patch)
    
    print(' .............. FEATURES EXTRACTION ...............................')
    valeurs_features_train=features_calculation(2*k+1,liste_patch_train)
    csv_creation(valeurs_features_train,'extraction_train.csv')
    
    valeurs_features_test=features_calculation(2*k+1,liste_patch_test)
    csv_creation(valeurs_features_test,'extraction_test.csv')
    
    print(' .............. RANDOM FOREST ..................................')
    model,predictions,pr =random_forest(valeurs_features_train,liste_patch_train_val,valeurs_features_test,liste_patch_test_val)
    
    print(' .......................... SVM ................................')
    result, p, clf=svm_method(k,liste_patch_train, liste_patch_train_val, liste_patch_test, liste_patch_test_val)

    # pour chaque patch positif de l'image du patient test
        # pour chaque pixel, ajouter 1 à tableau_pixel_pos au niveau de la coord du pixel
    
    print(' ......................... Pixel lesion determination .........')
#    tableau_pixel_pos =np.zeros(image_patient_test.shape)
#    tableau_pixel_pos = padding(tableau_pixel_pos,k)
#    for i,patch in enumerate(liste_patch_test):
##        if i in [x for x in range(0,65000,5000)]:
##        print('patch ',i)
#        if predictions[i]==1 :
#            c=liste_patch_coord[i]
##            print('index',(2*k+1)*i)
#            for x in range(len(patch)):
#                for y in range(len(patch)):
#                    for z in range(len(patch)):
#                        tableau_pixel_pos[c[0]+x][c[1]+y][c[2]+z]=tableau_pixel_pos[c[0]+x][c[1]+y][c[2]+z] + 1
#    from skimage.external import tifffile
#    indice = np.where(tableau_pixel_pos !=0)
#    print('indice ', indice)
#    seuil = k**3/2
#    tab=np.zeros(tableau_pixel_pos.shape)
#    for x in range(len(tab)):
#        for y in range(len(tab[0])):
#            for z in range(len(tab[0][0])):
#                if tableau_pixel_pos[x][y][z] >= seuil:
#                    tab[x][y][z]=1
#            
#    tifffile.imsave('pixel.tif',tab.T)
    '''puis checker si il est bon et faire courbe roc pour determiner le nombre de fois ou un pixel doit apparaitre dans des lesions pos pour etre positif'''