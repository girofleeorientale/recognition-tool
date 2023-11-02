'''
Fichier destiné à la prise de décision grâce à l'analyse du modèle de ML sur l'image de la caméra
'''

import cv2
# Importation du fichier de detection personnalisé pour fonctionné avec notre programme.
import sys
sys.path.insert(1, '../yolov5')
import detect_modifie
sys.path.insert(1, '../yolov5/classify')
import predict
sys.path.insert(1, '../PythonAnna')
import classifier

import UI



# Fonction de parsing du fichier resultat txt d'une detection
def Analyse_File():
    # Analyse des données OPENCV
    try:
        analyse = classifier.AnalyseImageOpenCV("OreoCapture.png")
        if analyse == 'entier':
            UI.UI.NB_OREOS_OPENCV = "True"
        elif analyse == 'décalé':
            UI.UI.NB_DECALES_OPENCV = "True"
        elif analyse == 'mangé':
            UI.UI.NB_MANGES_OPENCV = "True"
        elif analyse == 'fissuré':
            UI.UI.NB_FISSURES_OPENCV = "True"
    except:
        print("Error: impossible to analyse with openCV algorithm")
        
    
    
    # Analyse yolo
    # 1) Récupération des données textuelles dans une liste de strings
    All_lines = []
    try:
        file = open("../yolov5/runs/detect/exp/labels/OreoCapture.txt", "r")
        All_lines = file.readlines()
        file.close()
        file = open("../yolov5/runs/detect/exp/labels/OreoCapture.txt", "w").close()
    except:
        print("Error : Try to open non-existant file")
        return []
    
        
    # 2) Analyse des données YOLO:
    dictionnaire = {"Oreo":0, "Fissure":0, "Mange":0, "Efface":0, "Decale":0}
    for line in All_lines:
        classe = int(line[0]) # Récupération du numéro de classe
        if classe == 0:
            dictionnaire["Oreo"]+=1
        elif classe == 1:
            dictionnaire["Fissure"]+=1
        elif classe == 2:
            dictionnaire["Mange"]+=1
        elif classe == 3:
            dictionnaire["Efface"]+=1
        elif classe == 4:
            dictionnaire["Decale"]+=1
            
    # 2.bis) Mettre à jour les valeurs du nombre de chaque classe dans UI
    UI.UI.NB_OREOS = dictionnaire["Oreo"]
    UI.UI.NB_FISSURES = dictionnaire["Fissure"]
    UI.UI.NB_MANGES = dictionnaire["Mange"]
    UI.UI.NB_EFFACES = dictionnaire["Efface"]
    UI.UI.NB_DECALES = dictionnaire["Decale"]
            
    # 3) Analyse du dictionnaire et prise d'une décision
    Decision = "NONE"
    for (key, value) in dictionnaire.items():
        #print("Classe "+key+" : "+str(value))
        if key == "Oreo" and value == 1:
            Decision = "GOOD"
        elif (key != "Oreo" and value!=0) or (key=="Oreo" and value>1):
            Decision = "BAD"
    
    #print("Décision prise : "+Decision)
    if Decision == "GOOD":
        UI.UI.NB_TOTAL_OREOS_SANS_DEFAUTS += 1
    elif Decision == "BAD":
        UI.UI.NB_TOTAL_OREOS_AVEC_DEFAUTS += 1
    return Decision
        
    


# Fonction qui fait appel à notre modèle de ML pour classifier un Oréo.
# Retourne "GOOD" ou "BAD" selon la classe trouvée
def Classify_OREO(cam):
    # ETAPE 1 : Capturer l'image de la caméra
    result, image = cam.read()
    # Enregistrement 
    if result:
        cv2.imwrite("OreoCapture.png", image)
        #print("Image enregistrée avec succès")
    else:
        print("Erreur lors de la capture de l'image. Aucune image enregistrée.")
        
    # ETAPE 2 : Appliquer le modèle de ML sur cette image
    detect_modifie.run()
    
    # ETAPE 3 : Récupérer le fichier de données de cette prédiction
    return Analyse_File()
