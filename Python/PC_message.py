# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 13:04:51 2023

@author: remil
"""




# Objet qui représente un message envoyé par le PC à ARDUINO
class PC_message:
    ID_MESSAGE = 0
    def __init__(self, motorV, servoV, ledV):
        self.idMessage = PC_message.ID_MESSAGE # id du message courant
        self.MotorValue = motorV # 0 -> neutre; 1 -> pull; 2 -> push
        self.ServoValue = servoV # 0 -> neutre; 1 -> goodOreo; 2 -> badOreo
        self.LedValue = ledV # 0 ... voir plus tard pour les leds
        
        PC_message.ID_MESSAGE += 1
        
        
    # Construit le message à envoyer à partir des attributs de l'objet
    def toString(self):
        # --- Concatenation des attributs 
        message = ","
        message += str(self.idMessage)+","
        message += str(self.MotorValue)+","
        message += str(self.ServoValue)+","
        message += str(self.LedValue)
        
        # --- Calcul du checksum
        # les deux premiers chiffres représentent le nombre de caractères dans le message
        nb_car = len(message)
        
        # les quatres suivants représentent la somme des valeurs ascii % 10000
        ascii_sum = 0
        for lettre in message:
            ascii_sum += ord(lettre)
        ascii_sum = ascii_sum%10000
        
        # On les ajoute en début de message
        nb_car_string = str(nb_car).zfill(2)
        ascii_sum_string = str(ascii_sum).zfill(4)
        message = nb_car_string+","+ascii_sum_string+message
        
        return message
    
    
    


# Objet dans lequel on va stocker les données des messages venant de ARDUINO
class ARDUINO_message:
    def __init__(self, string):
        self.checkLen = 0 # Stocke la longueur du message
        self.checkSum = 0 # Stocke la somme des valeurs ascii
        self.idMessage = 0
        self.stateSwitch1 = 0  # 1 => activé, 0 sinon
        self.stateSwitch2 = 0  # 1 => activé, 0 sinon
        self.stateCapteur = 0  # 1 => plateau horizontal, 0 sinon
        
        self.initial_message = string # Stocke le message brut
        self.parse_string()
     
        
    # Initialise les attributs par parsing d'une chaine de caractères représentant un message venant de l'arduino
    def parse_string(self):
        parsed = self.initial_message.split(",")
        try:
            self.checkLen = int(parsed[0])
            self.checkSum = int(parsed[1])
            self.idMessage = int(parsed[2])
            self.stateSwitch1 = int(parsed[3])
            self.stateSwitch2 = int(parsed[4])
            self.stateCapteur = int(parsed[5])
        except:
            print("ERROR in initialisation of ADUINO_message object : unexcepted parsing")
     
            
    # Retourne True si le message est valide, False sinon
    def checkIntegrity(self):
        # Controle de l'intégrité du message reçu
        nb_car = len(self.initial_message[7:])
        if nb_car != self.checkLen:
            print("ERROR in message integrity : checkLen doesn't correspond to message length")
            return False
        
        # Controle de l'intégrité par somme des ascii
        ascii_sum = 0
        for lettre in self.initial_message[7:]:
            ascii_sum += ord(lettre)
        ascii_sum = ascii_sum%10000
        if self.checkSum != ascii_sum:
            print("ERROR in message integrity : checkSum doesn't correspond to message's ascii sum")
            return False
        
        return True
        
    
    
