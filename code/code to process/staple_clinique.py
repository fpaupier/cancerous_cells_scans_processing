import numpy as np
import scipy as sc
from scipy import misc
import matplotlib.pyplot as plt
from PIL import Image
from PIL import ImageSequence
import numpy.ma as ma
import SimpleITK as sitk

# Ce code est destine aux etudes cliniques dont les segmentations ont ete faites par les methodes 40%, adaptative, nestle et Kmean

# Fonction : STAPLE

### Arguments
# indim : numero du patient

### Retourne
# volLesion 	: volume de la lesion par STAPLE
# vol40		: volume de la lesion par la methode 40 %
# voladapt	: volume de la lesion par la methode Adaptative
# volnestle	: volume de la lesion par la methode Nestle
# volkmean	: volume de la lesion par la methode K mean

### Enregistre chaque coupe de l image segmentee par STAPLE

def STAPLE(indim):

	print ' --- ---  STAPLE patient %d --- --- ' %(indim)
	print ' ---  ---  ---  ---  ---  ---  --- '


#
# Ouverture des images
#

	# Methode 40 %
	i40=Image.open('/media/HDD2bis/Projet_suivi_therapeutique/Pheo/MultiSegmentation.Run1/40/'+str(indim)+'.tif')
	# Methode adaptative
	iadapt=Image.open('/media/HDD2bis/Projet_suivi_therapeutique/Pheo/MultiSegmentation.Run1/adapt/'+str(indim)+'.tif')
	# Methode nestle
	inestle=Image.open('/media/HDD2bis/Projet_suivi_therapeutique/Pheo/MultiSegmentation.Run1/nestle/'+str(indim)+'.tif')
	# Methode k mean
	ikmean=Image.open('/media/HDD2bis/Projet_suivi_therapeutique/Pheo/MultiSegmentation.Run1/kmean/'+str(indim)+'.tif')

	# Ouverture premiere coupe pour chaque methode
	i40.seek(0)
	iadapt.seek(0)
	inestle.seek(0)
	ikmean.seek(0)

	#juste pour determiner le nombre de coupe
	inputImage = sitk.ReadImage ('/media/HDD2bis/Projet_suivi_therapeutique/Pheo/MultiSegmentation.Run1/dcmCrop/'+str(indim)+'.tif',sitk.sitkFloat32)


#
# Parametres
#
	MAX_ITERATIONS = 10 	# nombre maximal d iterations
	EPSILON = 0.00001 	# critere de convergence
	ACCEPT = 0.5		# seuil d acceptation que le voxel appartient a la lesion ou au fond

	nbmethods = 4		# Nombre de methodes (40%, adaptative, nestle et kmean)

	volVoxel = 4*4*2	# volume d un voxel

	volLesion = 0		# volume de la lesion par Staple
	vol40 = 0		# volume de la lesion par methode 40
	voladapt = 0		# volume de la lesion par methode adaptative
	volnestle = 0		# volume de la lesion par methode nestle
	volkmean = 0		# volume de la lesion par methode kmean

	# Dimensions de l image
	imageDims=i40.size
	w=i40.size[0]		# largeur
	h=i40.size[1]		# hauteur
	m=w*h			# nombre de voxels par image

	fT1 = 0.8		# probabilite d avoir le voxel a 1, intervient pour calcul du poids des voxels W
	fT0 = 1 - fT1		# probabilite d avoir le voxel a 0, intervient pour calcul du poids des voxels W

	nbslides=inputImage.GetDepth()
	print(nbslides)
	tablep = np.zeros((nbslides,nbmethods))		# matrice regroupant les sensibilites de chaque methode pour chaque coupe
	tableq = np.zeros((nbslides,nbmethods))		# matrice regroupant les specificites de chaque methode pour chaque coupe

	# Matrice regroupant tous les voxels de toutes les methodes de segmentation
	# voxels en ligne, methodes en colonne
	D=np.zeros((m,nbmethods))

	# Acces aux valeurs des voxels de chaque image sous forme de listes
	l40 = list(i40.getdata())
	ladapt = list(iadapt.getdata())
	lnestle = list(inestle.getdata())
	lkmean = list(ikmean.getdata())

	for ind in xrange(0,m):
		#insertion voxels i40 dans 1ere colonne matrice D
		D[ind,0]= l40[ind]
		#insertion voxels iadapt dans 2eme colonne matrice D
		D[ind,1]= ladapt[ind]
		#insertion voxels inestle dans 3eme colonne matrice D
		D[ind,2]= lnestle[ind]
		#insertion voxels ikmean dans 4eme colonne matrice D
		D[ind,3]= lkmean[ind]

	# Creation d une image binaire segmentee selon staple
	imageOut=Image.new("1", (w,h) )

#
# Initialisation
#

	# Sensibilite p et specificite q
	# Initialisees a 0.99999 pour chaque methode
	p = np.empty(nbmethods)
	p.fill(0.99999)
	q = np.empty(nbmethods)
	q.fill(0.99999)

# E step

	# Creation d un vecteur W donnant l importance de chaque voxel
	# etabli par l ensemble des methodes
	W = np.zeros((m,1))

	for step in xrange(0,MAX_ITERATIONS):

		avgW=np.zeros((MAX_ITERATIONS,1),dtype=np.float) # moyenne des elements de W, intervient pour convergence
		sumW=np.zeros((MAX_ITERATIONS,1),dtype=np.float) # somme des elements de W, intervient pour convergence
		avgW[0] = 1
		sumW[0] = 0

		alpha=np.zeros((m,1),dtype=np.float) 	# intervient pour calcul du poids des voxels W
		beta=np.zeros((m,1),dtype=np.float)	# intervient pour calcul du poids des voxels W

		for i in xrange(0,m):	# parcourt des voxels

			mulD0p=np.array(1,dtype=np.float)
			mulD1p=np.array(1,dtype=np.float)
			mulD0q=np.array(1,dtype=np.float)
			mulD1q=np.array(1,dtype=np.float)

			for j in xrange(0,nbmethods):	# parcourt des methodes

				if D[i,j]==1:
					mulD1p = np.multiply(mulD1p,p[j])
					mulD1q = np.multiply(mulD1q,(1-q[j]))

				else :
					mulD0p = np.multiply(mulD0p,(1-p[j]))
					mulD0q = np.multiply(mulD0q,q[j])

			alpha[i]= fT1*np.multiply(mulD0p,mulD1p)
			beta[i] = fT0*np.multiply(mulD0q,mulD1q)

			W[i] = float(alpha[i])/float(alpha[i]+beta[i])	# poids du voxel i
			sumW[step]=np.sum(W)				# somme des poids des voxels


# M Step

		for j in xrange(0,nbmethods):	# parcourt des methodes

			sumD0p=0
			sumD1p=0
			sumD0q=0
			sumD1q=0

			for i in xrange(0,m):	# parcourt des voxels

				if D[i,j] > ACCEPT:
					sumD1p += W[i]
					sumD1q += (1-W[i])
				else :
					sumD0p += W[i]
					sumD0q += (1-W[i])

			p[j] = sumD1p/(sumD0p+sumD1p)	# Sensibilite de la methode
			q[j] = sumD0q/(sumD0q+sumD1q)	# Specificite de la methode

			tablep[0,j]=p[j]		# Mise a jour de la matrice regroupant les sensibilites pour la methode j
			tableq[0,j]=q[j]		# Mise a jour de la matrice regroupant les specificites pour la methode j


		### Test convergence
		# Arret si la difference entre la somme des poids des voxels (ie le volume calcule par staple) de l iteration en cours
		# et celle de l iteration precedente est inferieure a la tolerance epsilon
		# Si le volume calcule varie peu, on s arrete car on a une bonne approximation du volume

		if step>0:	# pas d arret a la premiere etape
			if ( abs(sumW[step] - sumW[step-1])) < EPSILON :
				avgW[step] = float(sumW[step]) / nbmethods
				break	# arret car convergence
			avgW[step] = float(sumW[step]) / nbmethods

		# Cas ou tous les voxels sont identiques
		# La boucle if ci dessus donne un poids a 0.5 pour tous les voxels, alors qu ils devraient etre tous a 1 ou tous a 0
		if (p[j]==1 and q[j]==0) or (p[j]==0 and q[j]==1):
			avgW[step] = float(sumW[step]) / nbmethods
			break

#
# Resultats
#

	# Mise a jour de l image staple avec les valeurs W[i]
	data=np.zeros((w,h)) 	# matrice de voxels

	x=0
	y=0
	for i in xrange (0,m):	# parcourt les voxels de W
		data[x,y] = W[i]				# remplissage matrice
		imageOut.putpixel((x,y), data[x,y])		# ajout voxel dans image de sortie
		x +=1
		if x==w:	# fin de la ligne : passage a la ligne suivante
			x=0
			y +=1

	### Sauvegarde de la premiere coupe de l image obtenue par Staple
	imageOut.save('/media/HDD2bis/Projet_suivi_therapeutique/Pheo/STAPLE_vote.Run1/staple/'+str(indim)+'/0.tiff', "tiff")

	# Affichage du nombre de voxels pour chaque couleur dans l image faite par staple
	print 'couleurs des voxels du masque 0 par staple : ', imageOut.getcolors()

	# Calcul du volume de la lesion de chaque methode
	for item in i40.getcolors():		# Methode 40 %
		if item[1]== 1:
			vol40 +=float(item[0])
	for item in iadapt.getcolors():		# Methode adaptative
		if item[1]== 1:
			voladapt +=float(item[0])
	for item in inestle.getcolors():	# Methode nestle
		if item[1]== 1:
			volnestle +=float(item[0])
	for item in ikmean.getcolors():		# Methode kmean
		if item[1]== 1:
			volkmean +=float(item[0])
	for item in imageOut.getcolors():	# STAPLE
		if item[1]== 1:
			volLesion +=float(item[0])

	### Fonction Staple sur les coupes suivantes
	try:
		while 1:	# Continuation tant qu il n y a pas d erreur

			z = i40.tell()+1	# numero de la coupe
			### Ouverture des coupes suivantes pour chaque methode
			# image.seek(z) ouvre la coupe z de image (3d)
			# retourne erreur EOFError si ouverture impossible
			i40.seek(z)
			iadapt.seek(z)
			inestle.seek(z)
			ikmean.seek(z)

			# Image binaire segmentee selon staple
			imageOut=Image.new("1", (w,h) )

			### Mise a jour matrice D regroupant tous les voxels de toutes les methodes de segmentation pour coupe z
			# voxels en ligne, methodes en colonne

			# Acces aux valeurs des voxels de chaque image sous forme de listes
			l40 = list(i40.getdata())
			ladapt = list(iadapt.getdata())
			lnestle = list(inestle.getdata())
			lkmean = list(ikmean.getdata())

			for ind in xrange(0,m):
				#insertion voxels i40 dans 1ere colonne matrice D
				D[ind,0]= l40[ind]
				#insertion voxels iadapt dans 2eme colonne matrice D
				D[ind,1]= ladapt[ind]
				#insertion voxels inestle dans 3eme colonne matrice D
				D[ind,2]= lnestle[ind]
				#insertion voxels ikmean dans 4eme colonne matrice D
				D[ind,3]= lkmean[ind]

#
# Initialisation
#

			# Sensibilite p et specificite q
			# Initialisees a 0.99999 pour chaque methode
			p = np.empty(nbmethods)
			p.fill(0.99999)
			q = np.empty(nbmethods)
			q.fill(0.99999)

# E step

			# Creation d un vecteur W donnant l importance de chaque voxel
			# etabli par l ensemble des methodes
			W = np.zeros((m,1))

			for step in xrange(0,MAX_ITERATIONS):

				avgW=np.zeros((MAX_ITERATIONS,1),dtype=np.float) # moyenne des elements de W, intervient pour convergence
				sumW=np.zeros((MAX_ITERATIONS,1),dtype=np.float) # somme des elements de W, intervient pour convergence
				avgW[0] = 1
				sumW[0] = 0

				alpha=np.zeros((m,1),dtype=np.float)
				beta=np.zeros((m,1),dtype=np.float)

				for i in xrange(0,m):	# parcourt des voxels

					mulD0p=np.array(1,dtype=np.float)
					mulD1p=np.array(1,dtype=np.float)
					mulD0q=np.array(1,dtype=np.float)
					mulD1q=np.array(1,dtype=np.float)

					for j in xrange(0,nbmethods):	# parcourt des methodes

						if D[i,j]==1:
							mulD1p = np.multiply(mulD1p,p[j])
							mulD1q = np.multiply(mulD1q,(1-q[j]))

						else :
							mulD0p = np.multiply(mulD0p,(1-p[j]))
							mulD0q = np.multiply(mulD0q,q[j])

					alpha[i]= fT1*np.multiply(mulD0p,mulD1p)	# intervient pour calcul du poids des voxels W
					beta[i] = fT0*np.multiply(mulD0q,mulD1q)	# intervient pour calcul du poids des voxels W

					W[i] = float(alpha[i])/float(alpha[i]+beta[i])	# poids du voxel i
					sumW[step]=np.sum(W)				# somme des poids des voxels


# M Step

				for j in xrange(0,nbmethods):	# parcourt des methodes

					sumD0p=0
					sumD1p=0
					sumD0q=0
					sumD1q=0

					for i in xrange(0,m):	# parcourt des voxels

						if D[i,j] > ACCEPT:
							sumD1p += W[i]
							sumD1q += (1-W[i])
						else :
							sumD0p += W[i]
							sumD0q += (1-W[i])

					p[j] = sumD1p/(sumD0p+sumD1p)	# Sensibilite de la methode
					q[j] = sumD0q/(sumD0q+sumD1q)	# Specificite de la methode

					tablep[z,j]=p[j]		# Mise a jour de la matrice regroupant les sensibilites
					tableq[z,j]=q[j]		# Mise a jour de la matrice regroupant les specificites


		### Test convergence
		# Arret si la difference entre la somme des poids des voxels (ie le volume calcule par staple) de l iteration en cours
		# et celle de l iteration precedente est inferieure a la tolerance epsilon
		# Si le volume calcule varie peu, on s arrete car on a une bonne approximation du volume

				if step>0:		# pas d arret a la premiere etape
					if ( abs(sumW[step] - sumW[step-1])) < EPSILON :
						avgW[step] = float(sumW[step]) / nbmethods
						break	# arret car convergence
					avgW[step] = float(sumW[step]) / nbmethods

				# Cas ou tous les voxels sont identiques
				# La boucle if ci dessus donne un poids a 0.5 pour tous les voxels,
				# alors qu ils devraient etre tous a 1 ou tous a 0
				if (p[j]==1 and q[j]==0) or (p[j]==0 and q[j]==1):
					avgW[step] = float(sumW[step]) / nbmethods
					break

#
# Resultats
#

			# Mise a jour de l image staple avec les valeurs W[i]
			data=np.zeros((w,h)) 	# matrice de voxels

			x=0
			y=0
			for i in xrange (0,m):	# parcourt les voxels de W
				data[x,y] = W[i]				# remplissage matrice
				imageOut.putpixel((x,y), data[x,y])		# ajout voxel dans image de sortie
				x +=1
				if x==w:	# fin de la ligne : passage a la ligne suivante
					x=0
					y +=1

			### Sauvegarde de l image obtenue par Staple
			imageOut.save('/media/HDD2bis/Projet_suivi_therapeutique/Pheo/STAPLE_vote.Run1/staple/'+str(indim)+'/'+str(z)+'.tiff', "tiff")

			# Affichage du nombre de voxels pour chaque couleur dans l image faite par staple
			print 'couleurs des voxels du masque %d par staple : ' %(z), imageOut.getcolors()

			# Calcul du volume de la lesion de chaque methode
			for item in i40.getcolors():		# Methode 40 %
				if item[1]== 1:
					vol40 +=float(item[0])
			for item in iadapt.getcolors():		# Methode adaptative
				if item[1]== 1:
					voladapt +=float(item[0])
			for item in inestle.getcolors(): 	# Methode nestle
				if item[1]== 1:
					volnestle +=float(item[0])
			for item in ikmean.getcolors():		# Methode kmean
				if item[1]== 1:
					volkmean +=float(item[0])
			for item in imageOut.getcolors():	# STAPLE
				if item[1]== 1:
					volLesion +=float(item[0])

	# La fonction image.seek(z) donne une erreur EOFError lorsqu il est impossible d ouvrir la coupe z
	# Execution de except si une exception intervient dans try (ie arret de try apres ouverture impossible de la coupe)
	# Si pas d exception, pas d execution de except
	except EOFError:
		pass 	# fin de la sequence

	# Execution de finally dans tous les cas, si presence exception ou non
	finally :

		print ' '
		print 'Patient %i : ' %(indim)
		print 'volume de la lesion estime par staple : %f voxels' %(volLesion)
		print ' '
		print 'volume de la lesion par methode 40 : 	%f voxels' %(vol40)
		print 'volume de la lesion par adaptative : 	%f voxels' %(voladapt)
		print 'volume de la lesion par nestle : 	%f voxels' %(volnestle)
		print 'volume de la lesion par k mean : 	%f voxels' %(volkmean)
		print ' '

		### Fonction STAPLE retourne le volume de la lesion par STAPLE, 40 %, Adaptative, Nestle, K mean
		return volLesion,vol40,voladapt,volnestle,volkmean
