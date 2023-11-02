# ********** IMPORTATION **********
import serial
import serial.tools.list_ports
import time
import datetime
import random
from PIL import Image
import argparse
import re
import cv2
import threading

# Our files
import PC_message
import Decision
import UI




# ********** VARIABLES GLOBALES **********
PORT = "COM8" #"5" # Pour le moment on définit un port par défaut.


# ********** Récupération du port permettant de communiquer avec la machine **********
# Affichage de la liste des ports disponibles :
all_ports = serial.tools.list_ports.comports()
print("--------------- Available ports ---------------")
for p in all_ports:
    print(str(p))
print("-----------------------------------------------")

# ********** Partie communication **********
serialMachine = serial.Serial(PORT, 57600, timeout=2)


def SendMessage(Message):
    UI.UI.MESSAGES.append(Message)
    Message = Message+"\n"
    serialMachine.write(Message.encode('utf-8'))

def ReceiveMessage():
    read = str(serialMachine.readline().decode('utf-8'))
    read = read.split('\r')[0]
    UI.UI.MESSAGES.append(read)
    return read



def main():
    
    # Mise en route de la caméra
    print("Préparation de la caméra ...")
    cam = cv2.VideoCapture(1) #1 
    print("Caméra ok")
    UI.UI.set_cam(cam)
    
    
    # Variables d'état
    state = 0 # Etat courant de la machine
    
    # Variables des capteurs la machine (Juste pour avoir l'information)
    stateSwitch1 = 0 # 0 -> neutre; 1 -> pull; 2 -> push
    stateSwitch2 = 0 # 0 -> neutre; 1 -> goodOreo; 2 -> badOreo
    stateCapteur = 0 # 0 -> vertical; 1 -> horizontal
    
    # Variables des controleurs de la machine (Variables que le PC modifie selon les états)
    stateMotor = 0 # 0-> neutre, 1->pull, 2->push
    stateServo = 0 # 0 -> neutre; 1 -> goodOreo; 2 -> badOreo
    stateLed = 0 # 0 -> eteint, 1->vert, 2->rouge
    
    # Variables autres
    deltaMessage = 200 # milliseconds d'attente entre l'envoi de deux messages
    classification = None
    Messages = []
    
    # Dates
    dateSendMessage = datetime.datetime.now()
    dateRotateServo = 0
    
    # Mise en place de l'interface graphique (Avec un thread dédié)
    UI_thread = threading.Thread(target=UI.UI.initialize)
    UI_thread.start()

    Running = True
    while Running:
        # ********** PC envoie un message toutes les X millisec pour donner des ordres **********
        if (datetime.datetime.now() - dateSendMessage).total_seconds()*1000 >= deltaMessage:
            dateSendMessage = datetime.datetime.now()
            python_message = PC_message.PC_message(stateMotor, stateServo, stateLed)
            python_message = python_message.toString()
            print("PC envoie : ["+python_message+"]")
            SendMessage(python_message)
        
        
        
        
        # ********** Tentative de réception d'un message de ARDUINO *********
        rcv = ReceiveMessage()
        if rcv != "":
            if rcv[0] == "*":
                print(rcv)
            else:
                # Ajout du message à la file de messages
                Messages.append(rcv)
                print("PC reçoit : ["+rcv+"]")
            
            
        # ********** Lecture d'un message reçu d'ARDUINO **********
        if len(Messages)>0:
            current_message = Messages[0]
            del Messages[0]
            
            # 1) Créer un objet ARDUINO_message
            message_object = PC_message.ARDUINO_message(current_message)
            
            # 2) Vérifier son intégrité
            is_valid = message_object.checkIntegrity()
            if is_valid:
                # Si le message est valide, on met à jour les variables d'état de la machine :
                stateSwitch1 = message_object.stateSwitch1
                stateSwitch2 = message_object.stateSwitch2
                stateCapteur = message_object.stateCapteur
                
                UI.UI.SWITCHT1_STATE = stateSwitch1
                UI.UI.SWITCHT2_STATE = stateSwitch2
                UI.UI.CAPTEUR_STATE = stateCapteur
                
                
        # ********** Si le mode manuel a été activé dans l'ui, passer direct à l'état 6 **********
        if UI.UI.MODE_AUTO == False:
            state = 6
        else:
            UI.UI.MOTEUR_STATE = stateMotor
            UI.UI.SERVO_STATE = stateServo
            UI.UI.LED_STATE = stateLed
            UI.UI.CAPTEUR_STATE = stateCapteur
            UI.UI.SWITCHT1_STATE = stateSwitch1
            UI.UI.SWITCHT2_STATE = stateSwitch2
            
            

            
        # ********** Mise à jour des variables des controleurs **********
        # Juste vérifier que la machine s'est bien setup
        if state == 0:
            if stateSwitch1 == 1 and stateSwitch2 == 0 and stateCapteur == 1:
                print("La machine est correctement intialisée, on peut continuer")
                stateMotor = 0
                stateServo = 0
                stateLed = 0
                state += 1
            
            elif stateSwitch1 == 0:
                stateMotor = 1
                
            elif stateSwitch1 == 1 and stateCapteur == 0:
                stateServo = 0
                
           
        # Envoyer l'ordre de placer un oreo
        elif state == 1:
            if stateSwitch2 == 0 and stateCapteur == 1:
                print("Continuer de pousser l'oréo jusq'au plateau")
                stateMotor = 2
                stateServo = 0
                stateLed = 0
                
            else:
                print("L'actionneur est arrivé en bout de course")
                stateMotor = 0
                stateServo = 0
                stateLed = 0
                state+=1
                # Dès que l'oréo est placé, on réinitialise les valeurs NB_<classe> de UI
                UI.UI.reset_analyse()
        
        # Ramener l'actionneur 
        elif state == 2:
            if stateSwitch2 == 1 and stateCapteur == 1:
                print("Continuer de tirer l'actionneur")
                stateMotor = 1
                stateServo = 0
                stateLed = 0
                
            elif stateSwitch1 == 0 and stateSwitch2 == 0 and stateCapteur == 1:
                stateMotor = 1
                stateServo = 0
                stateLed = 0
            
            else:
                print("L'actionneur est bien revenu en place")
                stateMotor = 0
                stateServo = 0
                stateLed = 0
                state += 1
                
        
        # Prendre la décision de classification
        elif state == 3:
            # Analyse de l'image grâce à notre modèle de ML
            classification = Decision.Classify_OREO(cam)
            state += 1
            # Mise à jour du graphique de l'UI
            #UI.UI.generate_graph(UI.UI.GRAPH_FRAME)
          
            
        # Envoyer ordre de basculement du servo
        elif state == 4:
            tmp_servo = 0
            tmp_led = 0
            if classification == "GOOD":
                print("Bon Oréo détecté par Python")
                tmp_servo = 1
                tmp_led = 1
            elif classification == "BAD":
                print("Mauvais Oréo détecté par Python")
                tmp_servo = 2
                tmp_led = 2
            else:
                print("Aucun Oréo détecté")
                
            if stateSwitch1 == 1:
                stateServo = tmp_servo
                stateLed = tmp_led
                state += 1
                dateRotateServo = datetime.datetime.now()
        
    
        # Faire revenir le servo en place
        elif state == 5:
            if (datetime.datetime.now() - dateRotateServo).total_seconds() >= 0.7:
                stateServo = 0
                stateLed = 0
                state = 0
                
                
                
            
        # Etat destiné au mode manuel
        elif state == 6:
            # Quand on demande à repasser en mode AUTO
            if UI.UI.MODE_AUTO == True:
                state = 0
                UI.UI.SERVO_STATE = 0
                UI.UI.MOTEUR_STATE = 0
                UI.UI.LED_STATE = 0
                
            # Gestion du mode manuel
            else:
                # ---------- Gestion Moteur ----------
                # Moteur (pull)
                if UI.UI.MOTEUR_STATE == 1:
                    if stateSwitch1 == 0:
                        stateMotor = 1
                    else:
                        stateMotor = 0
                        UI.UI.MOTEUR_STATE = 0
                # Moteur (push)
                elif UI.UI.MOTEUR_STATE == 2:
                    if stateSwitch2 == 0:
                        stateMotor = 2
                    else:
                        stateMotor = 0
                        UI.UI.MOTEUR_STATE = 0
                # Moteur stop
                elif UI.UI.MOTEUR_STATE == 0:
                    stateMotor = 0
                    
                    
                # ---------- Gestion Servo ----------
                # Tout mouvement de servo sous condition que plateau soit tiré au max
                if stateSwitch1 == 1:
                    # rotate GOOD
                    if UI.UI.SERVO_STATE == 1:
                        stateServo = 1
                    # rotate BAD
                    elif UI.UI.SERVO_STATE == 2:
                        stateServo = 2
                    # Horizontal
                    elif UI.UI.SERVO_STATE == 0:
                        stateServo = 0
                else:
                    print("Interdiction de bouger le plateau : switch1 non activé")
                
                    
                # ---------- Gestion LED ----------
                if UI.UI.LED_STATE == 1:
                    stateLed = 1
                elif UI.UI.LED_STATE == 0:
                    stateLed = 0
                
                
                # Mise à jour des variables de UI
                '''UI.UI.MOTEUR_STATE = stateMotor
                UI.UI.SERVO_STATE = stateServo
                UI.UI.LED_STATE = stateLed
                UI.UI.CAPTEUR_STATE = stateCapteur
                UI.UI.SWITCHT1_STATE = stateSwitch1
                UI.UI.SWITCHT2_STATE = stateSwitch2'''
                
                
        
            
    
    
#main()
try:
    main()
except Exception as e:
    print("Main failed")
    print("ERREUR : ")
    print(e)
finally:
    serialMachine.close()
    UI.UI.destroy()
