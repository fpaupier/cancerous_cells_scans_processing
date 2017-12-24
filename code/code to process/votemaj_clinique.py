import numpy as np
import scipy as sc
from scipy import misc
import matplotlib.pyplot as plt
from PIL import Image
from PIL import ImageSequence
import numpy.ma as ma

# Ce code est destine aux etudes cliniques dont les segmentations ont ete faites par les methodes 40%, adaptative, nestle et Kmean

# Fonction : Vote Majoritaire

### Arguments
# indim : numero du patient

### Retourne
# volLesion 	: volume de la lesion par STAPLE
# vol40		: volume de la lesion par la methode 40 %
# voladapt	: volume de la lesion par la methode Adaptative
# volnestle	: volume de la lesion par la methode Nestle
# volkmean	: volume de la lesion par la methode K mean

### Enregistre chaque coupe de l image segmentee par VoteMaj

def VoteMaj(indim):

	print ' --- ---  Vote Majoritaire patient %d --- --- ' %(indim)
	print ' --- ---  --- ---  --- ---  --- ---  --- ---  '

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

#
# Parametres
#
	ACCEPT = 0.45		# seuil d acceptation que le voxel appartient a la lesion ou au fond

	nbmethods = 4		# Nombre de methodes (40%, adaptative, nestle et kmean)

	volVoxel = 4*4*2	# volume d un voxel

	volLesion = 0		# volume de la lesion par Vote Majoritaire
	vol40 = 0		# volume de la lesion par methode 40
	voladapt = 0		# volume de la lesion par methode adaptative
	volnestle = 0		# volume de la lesion par methode nestle
	volkmean = 0		# volume de la lesion par methode kmean

	# Dimensions de l image
	imageDims = i40.size
	w = i40.size[0]		# largeur
	h = i40.size[1]		# hauteur
	m = w*h			# nombre de voxels par image

	# Image binaire segmentee selon vote majoritaire
	imageOut = Image.new("1", (w,h) )

	for x in xrange(0,w):	# parcourt des lignes
		for y in xrange(0,h):	# parcourt des colonnes

			somme = 0
			somme = i40.getpixel((x, y)) + iadapt.getpixel((x, y)) + inestle.getpixel((x, y)) + ikmean.getpixel((x, y))

			if ( float(somme)/nbmethods > ACCEPT ) :
				imageOut.putpixel((x,y), 1)	# Ajout voxel dans image de sortie

	### Sauvegarde de la premiere coupe de l image obtenue par Vote Majoritaire
	imageOut.save('/media/HDD2bis/Projet_suivi_therapeutique/Pheo/STAPLE_vote.Run1/votemaj/'+str(indim)+'/0.tiff', "tiff")

	# Affichage du nombre de voxels pour chaque couleur dans l image faite par Vote Majoritaire
	print 'couleurs des voxels du masque 0 par votemaj : ', imageOut.getcolors()

	# Calcul du volume de la lesion de chaque methode
	for item in i40.getcolors():		# Methode 40 %
		if item[1] == 1:
			vol40 += float(item[0])
	for item in iadapt.getcolors():		# Methode adaptative
		if item[1] == 1:
			voladapt += float(item[0])
	for item in inestle.getcolors():	# Methode nestle
		if item[1] == 1:
			volnestle += float(item[0])
	for item in ikmean.getcolors():		# Methode kmean
		if item[1] == 1:
			volkmean += float(item[0])
	for item in imageOut.getcolors():	# Vote Majoritaire
		if item[1] == 1:
			volLesion += float(item[0])

	### Fonction Staple sur les coupes suivantes
	try:
		while 1:	# Continuation tant qu il n y a pas d erreur

			z = i40.tell()+1		# numero de la coupe
			### Ouverture des coupes suivantes pour chaque methode
			# image.seek(z) ouvre la coupe z de image (3d)
			# retourne erreur EOFError si ouverture impossible
			i40.seek(z)
			iadapt.seek(z)
			inestle.seek(z)
			ikmean.seek(z)

			# Image binaire segmentee selon vote majoritaire
			imageOut = Image.new("1", (w,h) )

			for x in xrange(0,w):	# parcourt des lignes
				for y in xrange(0,h):	# parcourt des colonnes

					somme = 0
					somme = i40.getpixel((x, y))+iadapt.getpixel((x, y))+inestle.getpixel((x, y))+ikmean.getpixel((x, y))
					if ( float(somme)/nbmethods > ACCEPT ) :
						imageOut.putpixel((x,y), 1)	# Ajout voxel dans image de sortie

			### Sauvegarde de l image obtenue par Vote Majoritaire
			imageOut.save('/media/HDD2bis/Projet_suivi_therapeutique/Pheo/STAPLE_vote.Run1/votemaj/'+str(indim)+'/'+str(z)+'.tiff', "tiff")

			# Affichage du nombre de voxels pour chaque couleur dans l image faite par staple
			print 'couleurs des voxels du masque %d par votemaj : ' %(z), imageOut.getcolors()

			# Calcul du volume de la lesion de chaque methode
			for item in i40.getcolors():		# Methode 40 %
				if item[1] == 1:
					vol40 += float(item[0])
			for item in iadapt.getcolors():		# Methode adaptative
				if item[1] == 1:
					voladapt += float(item[0])
			for item in inestle.getcolors():	# Methode nestle
				if item[1] == 1:
					volnestle += float(item[0])
			for item in ikmean.getcolors():		# Methode kmean
				if item[1] == 1:
					volkmean += float(item[0])
			for item in imageOut.getcolors():	# Vote Majoritaire
				if item[1] == 1:
					volLesion += float(item[0])


	# La fonction image.seek(z) donne une erreur EOFError lorsqu il est impossible d ouvrir la coupe z
	# Execution de except si une exception intervient dans try (ie arret de try apres ouverture impossible de la coupe)
	# Si pas d exception, pas d execution de except
	except EOFError:
		pass # fin de la sequence

	# Execution de finally dans tous les cas, si presence exception ou non
	finally :
		print ' '
		print 'Patient %i : ' %(indim)
		print 'volume de la lesion estime par votemaj : %f voxels' %(volLesion)
		print ' '
		print 'volume de la lesion par methode 40 : 	%f voxels' %(vol40)
		print 'volume de la lesion par adaptative : 	%f voxels' %(voladapt)
		print 'volume de la lesion par nestle : 	%f voxels' %(volnestle)
		print 'volume de la lesion par k mean : 	%f voxels' %(volkmean)
		print ' '

		### Fonction VoteMaj retourne le volume de la lesion par vote majoritaire, 40 %, Adaptative, Nestle, K mean
		return volLesion,vol40,voladapt,volnestle,volkmean
