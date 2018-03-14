//setBatchMode(true);
//=======================================================
//  Cropage (suivant x,y,z) des reconstructions TEP
//	ETAPE 1
//=======================================================

/*
 * En entree : une image 3D
 *
 * Retourne une image recadree au plus pres suivant les trois dimensions
 *
 */

//------------ Parametres ------------
var x_max, y_max;
compteur = 0; //compteur du nombre d'images créées
largeur = 0;	// largeur de l image creee
hauteur = 0;	// hauteur de l image creee
dl_x = 0;
dl_y = 0;
number = 0;

//=======================================================
//                    CODE
//=======================================================

//------------ Ouverture de l image a recadrer ------------

// Demande a l utilisateur de selectionner le dossier patient
dir = getDirectory("Choisir le dossier patient");

indice = 0; // indice de la methode en cours

for (indice=0; indice<5; indice++)
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

	//------------ Ouverture du masque de l image ouverte ------------
	selectImage(1);
	x_max = parseInt(getWidth());	//x_max=200;
	y_max = parseInt(getHeight());	//y_max=200;
	rename("mask");
	run("Duplicate...", "duplicate");
	selectImage(2);
	rename("maskd");

	run("32-bit"); 						 //Passage du masque en 32 bits
	run("Divide...", "value=255 stack"); // Passage du masque en binaire
	imageCalculator("Multiply create stack", "mask","maskd");
	selectImage(3);
	rename("Results");

	//-----------------------------------------------------
	//            CROPAGE AXIAL suivant z
	//-----------------------------------------------------
	selectWindow("Results");
	condition=0; 	//0 si non trouve
	debutlesion_z=0;
	finlesion_z=0;

	// Acces au premier masque ou un pixel a 1 apparait (debut lesion)
	for(n=1; n<=nSlices; n++)	// parcourt des masques a partir du debut
	{
		setSlice(n);
		somme = 0;
				for(y=1; y<=y_max; y++)
				{
					for(x=1; x<=x_max; x++)
					{
						pixelValue = getPixel(x,y);
						somme = somme + pixelValue;
						if(somme != 0)
						{
							x = x_max + 1;
						}
					}
				}

				if(somme != 0)
				{
					if(condition == 0)
					{
						condition = 1;	// trouve
						debutlesion_z = n;
						//print("debut de lesion suivant z: "+debutlesion_z);
					}
					break;	// arret
				}
	}

	// Acces au dernier masque ou un pixel a 1 apparait (fin lesion)
	condition = 0;	//0 si non trouve
	for(n=nSlices; n>=1; n--) // parcourt des masques a partir de la fin
	{
		setSlice(n);
		somme = 0;
			for(y=1; y<=y_max; y++)
			{
				for(x=1; x<=x_max; x++)
				{
					pixelValue = getPixel(x,y);
					somme = somme + pixelValue;
					if(somme != 0)
					{
						x = x_max + 1;
					}
				}
			}

			if(somme != 0)
			{
				if(condition == 0)
				{
					condition = 1;	// trouve
					finlesion_z = n;
					//print("fin de lesion suivant z: "+finlesion_z);
				}
				break; // arret
			}
	}

	// Cropage suivant z
	run("Duplicate...", "duplicate range="+debutlesion_z+"-"+finlesion_z+"");
	rename("cropz");

	//-----------------------------------------------------
	//            CROPAGE SUIVANT X,Y
	//-----------------------------------------------------
	selectWindow("cropz");
	nb_slices = nSlices;

	//------------ Initialisation ------------
	setSlice(1);

	// ligne horizontale haute
	for(y=1; y<=y_max; y++)
	{
		for(x=1; x<=x_max; x++)
		{
			pixelValue = getPixel(x,y);
			if(pixelValue != 0)
			{
				dl_y = y;

				x = x_max+1; //arret boucle
				y = y_max+1; //arret boucle
			}
		}
	}

	// ligne horizontale basse
	for(y=y_max; y>=1; y--)
	{
		for(x=1; x<=x_max; x++)
		{
			pixelValue = getPixel(x,y);
			if(pixelValue != 0)
			{
				fl_y = y;

				x = x_max + 1; //arret boucle
				y = 0; //arret boucle
			}
		}
	}

	// ligne verticale gauche
	for(x=1; x<=x_max; x++)
	{
		for(y=1; y<=y_max; y++)
		{
			pixelValue = getPixel(x,y);
			if(pixelValue != 0)
			{
				dl_x = x;

				y = y_max+1; //arret boucle
				x = x_max+1; //arret boucle
			}
		}
	}

	// ligne verticale droite
	for(x=x_max; x>=1; x--)
	{
		for(y=1; y<=y_max; y++)
		{
			pixelValue = getPixel(x,y);
			if(pixelValue != 0)
			{
				fl_x = x;

				y = y_max + 1; 	//arret boucle
				x = 0; 		//arret boucle
			}
		}
	}

	//------------ Mise a jour ---------------
	for(n=2; n<=nSlices; n++)
	{
		setSlice(n); // ouverture masque n

		// ligne horizontale haute
		for(y=1; y<=y_max; y++)
		{
			for(x=1; x<=x_max; x++)
			{
				pixelValue=getPixel(x,y);
				if(pixelValue != 0)
				{
					if (y < dl_y)
					{
						dl_y = y;
					}
					x = x_max + 1; //arret boucle
					y = y_max + 1; //arret boucle
				}
			}
		}

		// ligne horizontale basse
		for(y=y_max; y>=1; y--)
		{
			for(x=1; x<=x_max; x++)
			{
				pixelValue = getPixel(x,y);
				if(pixelValue != 0)
				{
					if (y>fl_y)
					{
						fl_y = y;
					}
					x = x_max + 1; //arret boucle
					y = 0; //arret boucle
				}
			}
		}

		// ligne verticale gauche
		for(x=1; x<=x_max; x++)
		{
			for(y=1; y<=y_max; y++)
			{
				pixelValue = getPixel(x,y);
				if(pixelValue != 0)
				{
					if (x<dl_x )
					{
						dl_x = x;
					}
					y = y_max + 1; //arret boucle
					x = x_max + 1; //arret boucle
				}
			}
		}

		// ligne verticale droite
		for(x=x_max; x>=1; x--)
		{
			for(y=1; y<=y_max; y++)
			{
				pixelValue = getPixel(x,y);
				if(pixelValue != 0)
				{
					if (x>fl_x)
					{
						fl_x = x;
					}
					y = y_max + 1; 	//arret boucle
					x = 0; 		//arret boucle
				}
			}
		}
	}

	dl_x = dl_x; //A quoi sert cette ligne ?
	dl_y = dl_y; // et celle ci ?
	fl_x = fl_x + 1;
	fl_y = fl_y + 1;
	compteur = compteur + 1; //compte le nombre d'images créées
	largeur = fl_x - dl_x;
	hauteur = fl_y - dl_y;

	//------------ Affichages -------------------------------
	//print("debutlesion_x="+dl_x);
	//print("debutlesion_y="+dl_y);
	//print("finlesion_x="+fl_x);
	//print("finlesion_y="+fl_y);
	//print("largeur="+largeur);
	//print("hauteur="+hauteur);

	// Cropage suivant x et y
	makeRectangle(dl_x,dl_y,largeur,hauteur);
	run("Crop");
	rename("lesion_cropee");
	run("Set Scale...", "distance=0 known=0 pixel=1 unit=pixel");

	//------------ Insertion parametres dans boite de dialogue ------------
	a=Array.concat(debutlesion_z,finlesion_z,dl_x,dl_y,largeur,hauteur);
	Array.print(a);

	//------------ Fermeture des images ----------------------------------
	close("mask");
	close("maskd");
	close("lesion_cropee");
	close ("Results");
	close ("Results-1");
}

selectWindow("Log");
saveAs("Text", ""+dir+"/Log.txt");
close("Log");
