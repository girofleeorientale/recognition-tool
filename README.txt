********** OREO MACHINE **********
Allumage : 
- Vérifier le branchement de la caméra + du port de communcation avec la carte ARDUINO
- Allumer la machine
- Lancer le fichier principal de notre projet : communication.py


--- Architecture ---
./Arduino :
Contient l'ensemble du code C++ qui contrôle la machine (gestion des différents composants, communication Arduino vers PC, initialisation machine, ...)

./Data_save :
Il s'agit de la base de données d'images que nous avons utilisé. Elle est décomposée en plusieurs échantillons qui ont en réalité été fusionnés durant les phases d'apprentissage. Ce dossier contient également les fichiers de labélisation d'images que nous avons créé ainsi qu'un fichier statistique sur la répartition des différents types de défauts parmi nos Oréos.

./ggl :
Dossier qui stocke tout ce qui a été nécessaire à l'apprentissage du modèle YOLO.
  |_datasets_ggl : Contient les images réparties dans deux échantillons (train et valid)
  |_weight : contient les résultats des apprentissages (apprentissages que nous avons réalisé sur google collab.
  |_ggl/oreo_data : fichier de configuration personnalisé avec nos propres données.

./Python :
Ensemble du code python servant au bon déroulement du programme principal.
  |_communication.py : fichier principal de notre projet. C'est lui qui doit être exécuté. Il s'occupe de la communication avec la machine et appelle les fonctions haut-niveau des autres classes pour actionner au bon moment le modèle YOLO, faire la classification, actualiser l'interface graphique, ...
  |_Decision.py : Ensemble de fonctions qui permettent, à partir d'un fichier txt généré par YOLO, de prendre une décision de classification sur l'oréo courant
  |_PC_message.py : Contient des classes permettant de gérer l'envoi et la réception de message avec la carte ARDUINO.
  |_UI.py : Classe dédiée à l'interface graphique. Elle contient des variables globales mises à jour tout au long du déroulement du programme. L'interface se met à jour toutes les x secondes et affiche les composants selon ces variables globales.
  |_detect_modifie.py : Fichier de detection adapté à notre programme (on y a indiqué les résultats de notre entrainement, le path de l'image à analyser, modifié des paramètres et supprimé certains affichages non nécessaires)
  |_OreoCapture.png : Dernière photo prise par la caméra pour être analysée par YOLO.

./Rapport latex:
Tout ce qui est nécessaire pour nos rapport (fichier latex, images, prise de notes, ...)

./Yolov5:
Repertoire git qui contient les fichiers dont dépendent les détections.



--- En cas de problème ---
* Problème avec le dossier YOLO : 
Le dossier YOLOv5 ne peut pas être push sur git car il est lui même un répertoire git.
Si ce dossier est absent ou s'il présente un problème suivre ces étapes :
- Ouvrir detection_oreo.ipynb qui se trouve à la racine
- cloner le répertoire git (premmière ligne du fichier)
- se déplacer dans le dossier YOLOv5 (vérifier que le déplacement a bien marché)
- installer les requirements (executer la cellule associée)
- Copier le fichier detect_modifie(save).py se trouvant dans le dossier Python et le coller dans Yolov5. (Ne pas oublier de retirer le (save) dans le nom de ce fichier)

* Problème avec les ports de communication :
Si les ports ne sont pas reconnus par python/arduino : 
1) Essayer de changer le branchement
2) Essayer de changer le numéro du port directement dans le code (éventuellement s'aider de l'affichage python si besoin)
3) Essayer de changer la vitesse de communication

* Problème de caméra :
Si le programme utilise la caméra principale de l'ordinateur, il faut changer pour qu'il utilise celle en USB.
Pour ça, mettre
cam = cv2.VideoCapture(id) # avec id = 1 ou id = 2
Si ce problème ce produit, on peut le voir avec le Python/OreoCapture.png si l'image est noire. (et aussi parce que la classification donne toujours "aucun oreo détecté") 