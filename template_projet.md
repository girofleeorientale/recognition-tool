# Titre du projet
Contrôle qualité de gâteaux Oréo


## Introduction générale

Dans le cadre du module "Projet long", nous souhaitons travailler sur un projet de Data-Science et plus spécifiquement sur la reconnaissance d'image.
L'objectif est de produire un système de contrôle qualité de gâteaux grâce au machine learning.
Ce projet original nous permettra d'apprendre les différentes étapes nécessaires à sa mise en place, mais également d'acquiérir des compétences dans l'utilisation de composants Arduino.


## Objectifs

L'objectif principal du projet est de mettre en oeuvre plusieurs méthodes de machine learning (ex: YOLO) pour permettre la classification de gâteaux Oréo selon leur défauts.

L'objectif intermédiaire est de créer une machine (mécanique + Arduino) pour rendre le défilement des Oréo et leur analyse automatique.

L'objectif supplémentaire est de créer l'interface graphique pour voir en temps réel l'execution de l'algorithme sur les images capturées par la caméra de la machine, ainsi que pour obtenir des informations statistiques sur la session d'analyse courante.



## Testabilité

Dans un premier temps, on appliquera nos modèles aux sets de donnés dédiés aux tests.
Puis, lorsque la machine sera créée, on les appliquera à la vidéo d'une caméra filmant en temps réel les Oréos.



## Calendrier

Etape 1 : Novembre - Fin Décembre:
Création de la base de données contenant les Oréos avec et sans défaut. (fabrication des Oréos, prise de photos, labélisation, ...)
Mise en place du machine learning avec un certain type d'algorithme (dans un premier temps).

Etape 2 : Fin Décembre - Janvier:
Une fois que les tests avec le premier algorithme sont concluants, l'objectif est d'en tester un second afin de les comparer.

Etape 3 : Février - Mars:
Création de la machine qui permet le défilement automatique des Oréos devant une caméra, les classifie, et les oriente en fonction de leur qualité (mal imprimés, mal assemblés, fissurés, ...)

Etape 4 : Mars - Mai:
Création d'une interface graphique permettant de voir en temps réel les Oréos défiler, ainsi que l'execution des algorithmes. On ajoutera une section "statistique" pour avoir un récapitulatif des différents défauts trouvés et leur proportion.


## Références

L'idée est de reproduire un système de contrôle qualité à petite échelle (ex : https://www.youtube.com/watch?v=Uk35Y3sL1rk)
