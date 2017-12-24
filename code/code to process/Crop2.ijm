setBatchMode(true);
run("DICOM...", "open");
//=======================================================
//  Cropage (suivant x,y,z) des reconstructions TEP
//	ETAPE 2
//=======================================================

/*
 * En entree : une image 3D appartennant a une serie d images 3D et un fichier texte
 *
 * Enregistre une image recadree au plus pres dans le dossier Segmentation
 * en prenant les memes parametres que la serie d images
 *
 */


//------------ Dialogue ------------------------
// Demande a l utilisateur d entrer l indice du patient
Dialog.create("Choice");
Dialog.addString("Equivalent patient number for STAPLE or majority vote:", 0);
Dialog.show();
patient = Dialog.getString();

// Demande a l utilisateur de selectionner le dossier patient
dir = getDirectory("Choisir le dossier patient");

//------------ Ouverture du fichier texte contenant les dimensions du recadrage ------------
filestring = File.openAsString(""+dir+"/Log.txt")
//filestring = File.openAsString("")

//open(""+path+"/Log.txt"); // ok si path a partir de ce fichier Code/Cas_cliniques

/*	Le fichier texte possede une ligne par image avec les informations suivantes :
	- premier masque ou un pixel a 1 apparait (rappel : la lésion  est à 1 et le fond à 0)
	- dernier masque ou un pixel a 1 apparait
	- abscisse du point le plus en haut a gauche dont la valeur est 1
	- ordonnee du point le plus en haut a gauche dont la valeur est 1
	- distance horizontale entre le point le plus en haut a gauche et le point le plus en bas a droite dont les valeurs sont 1
	- distance verticale entre le point le plus en haut a gauche et le point le plus en bas a droite dont les valeurs sont 1
*/

rows = split(filestring, "\n");
debutlesion_z = newArray(rows.length);
finlesion_z = newArray(rows.length);
dl_x = newArray(rows.length);
dl_y = newArray(rows.length);
largeur = newArray(rows.length);
hauteur = newArray(rows.length);


indice = 0; // indice de la methode en cours

for (indice=0; indice<6; indice++)
{

	//------------ Ouverture de l image a recadrer ------------

	if (indice==0)
	{
		run("Image Sequence...", "open=["+dir+"/40/] sort");
	}
	if (indice==1)
	{
		run("Image Sequence...", "open=["+dir+"/adapt/] sort");
	}
	if (indice==2)
	{
		run("Image Sequence...", "open=["+dir+"/nestle/] sort");
	}
	if (indice==3)
	{
		open(""+dir+"/kmean.tif");
	}
	if (indice==4)
	{
		run("Image Sequence...", "open=["+dir+"/2.5/] sort");
	}
	if (indice==5)
	{
		run("Image Sequence...", "open=["+dir+"/dcm/] sort");
		startHour = parseInt(substring(getInfo("0008,0031"),1,3));
		startMinute = parseInt(substring(getInfo("0008,0031"),3,5));
		injHour = parseInt(substring(getInfo("0018,1072"),1,3));
		injMinute = parseInt(substring(getInfo("0018,1072"),3,5));

		deltaHour = startHour - injHour;
		deltaMinute = startMinute - injMinute;
		if(deltaMinute<0)
			{
				deltaMinute = 60 + deltaMinute;
				deltaHour = deltaHour - 1;
			}
			//18F
			decayFactor = exp(-log(2)*(60*deltaHour+deltaMinute)/109.8);
			//68Ga
			//decayFactor = exp(-log(2)*(60*deltaHour+deltaMinute)/67.71);
			correctedActivity = decayFactor*getInfo("0018,1074");
			if(getInfo("0010,1030")== "" || parseInt(getInfo("0010,1030"))==0)
				{
				Dialog.create("Enter the patient mass");
				Dialog.addNumber("Mass (kg):", 75);
				Dialog.show();
				mass = Dialog.getNumber();
				suvFactor = (mass*1000)/(correctedActivity);
				}
			else
				{
				suvFactor = (parseFloat(getInfo("0010,1030"))*1000)/correctedActivity;
				}
			//suvFactor = (parseFloat(getInfo("0010,1030"))*1000)/correctedActivity;
			//print("********");
			//print(getInfo("0010,1030"));
			//print("********");
			for (n=1; n<=nSlices; n++)
			{
 			setSlice(n);
			run("Multiply...", "value=suvFactor slice");
			//run("Reverse");
			}
	}

	run("Duplicate...", "duplicate"); 	//duplication
	rename("Duplicate");


	for(i=0; i<rows.length; i++)
	{
		columns = split(rows[i],", \t");
		debutlesion_z[i] = parseInt(columns[0]);
		finlesion_z[i] = parseInt(columns[1]);
		dl_x[i] = parseInt(columns[2]);
		dl_y[i] = parseInt(columns[3]);
		largeur[i] = parseInt(columns[4]);
		hauteur[i] = parseInt(columns[5]);
	}

	//=======================================================
	//                    CODE
	//=======================================================

	//------------ Initialisation des parametres ------------
	MIN_debutlesion_z = debutlesion_z[0];
	MAX_finlesion_z = finlesion_z[0];
	MIN_dl_x = dl_x[0];
	MIN_dl_y = dl_y[0];
	MAX_largeur = largeur[0];
	MAX_hauteur = hauteur[0];

	//------------ Mise a jour des parametres ---------------
	for (i=1; i<rows.length; i++)					// Parcourt du fichier texte
	{
		if (debutlesion_z[i]<MIN_debutlesion_z)		// premier masque avec un pixel a 1
		{
			MIN_debutlesion_z = debutlesion_z[i];
		}
		if (finlesion_z[i]>MAX_finlesion_z )		// dernier masque avec un pixel a 1
		{
			MAX_finlesion_z = finlesion_z[i];
		}
		if (dl_x[i]<MIN_dl_x)						// abscisse du point le plus en haut a gauche
		{
			MIN_dl_x = dl_x[i];
		}
		if (dl_y[i]<MIN_dl_y)						// ordonnee du point le plus en haut a gauche
		{
			MIN_dl_y = dl_y[i];
		}
		if (largeur[i]>MAX_largeur)					// largeur du recadrage minimale respectant toutes les images
		{
			MAX_largeur = largeur[i];
		}
		if (hauteur[i]>MAX_hauteur)					// hauteur du recadrage minimale respectant toutes les images
		{
			MAX_hauteur = hauteur[i];
		}
	}

	//------------ Affichages -------------------------------
	print (MIN_debutlesion_z);
	print (MAX_finlesion_z);
	print (MIN_dl_x);
	print (MIN_dl_y);
	print (MAX_largeur);
	print (MAX_hauteur);

	//------------ Creation rectangle de recadrage -----------
	makeRectangle(MIN_dl_x,MIN_dl_y,MAX_largeur,MAX_hauteur);
	// Cropage suivant x et y
	run("Crop");
	// Cropage suivant z
	run("Duplicate...", "duplicate range="+MIN_debutlesion_z+"-"+MAX_finlesion_z+"");
	rename("Cropz");

	//------------ Binarisation de l image obtenue -----------
	selectImage("Cropz");
	if (indice== 0 || indice== 1 || indice== 2)
	{run("Divide...", "value=255.000 stack");}

	//------------ Sauvegarde de l image recadree ------------
	// Enregistre les images du patient i segementeees sous le nom i.tif
	// pour chaque methode dans le dossier Segmentation
	if (indice==0)
	{
		saveAs("Tiff", "/media/HDD2bis/Projet_suivi_therapeutique/Pheo/MultiSegmentation.Run2/40/"+patient+".tif");
	}
	if (indice==1)
	{
		saveAs("Tiff", "/media/HDD2bis/Projet_suivi_therapeutique/Pheo/MultiSegmentation.Run2/adapt/"+patient+".tif");
	}
	if (indice==2)
	{
		saveAs("Tiff", "/media/HDD2bis/Projet_suivi_therapeutique/Pheo/MultiSegmentation.Run2/nestle/"+patient+".tif");
	}
	if (indice==3)
	{
		saveAs("Tiff", "/media/HDD2bis/Projet_suivi_therapeutique/Pheo/MultiSegmentation.Run2/kmean/"+patient+".tif");
	}
	if (indice==4)
	{
		saveAs("Tiff", "/media/HDD2bis/Projet_suivi_therapeutique/sarcoma_child/osteosarcoma/MultiSegmentation.Run2/2.5/"+patient+".tif");
	}
	if (indice==5)
	{
		saveAs("Tiff", "/media/HDD2bis/Projet_suivi_therapeutique/Pheo/MultiSegmentation.Run2/dcmCrop/"+patient+".tif");
	}

	//------------ Fermeture des images ----------------------
	run("Close All");

}
selectWindow("Log");
close("Log");
