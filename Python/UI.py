from tkinter import *
from tkinter import font
from PIL import ImageTk, Image
import serial.tools.list_ports
import functools
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import cv2
import random
import time
import sys



# Classe principale
class UI:    
    # --------------- Variables globales ---------------
    # *** Couleurs
    BACKGROUND_COLOR = '#%02x%02x%02x' % (33,35,36)
    BACKGROUND_COLOR_SECTIONS_1 = '#%02x%02x%02x' % (41,45,46)
    BACKGROUND_COLOR_SECTIONS_2 = '#%02x%02x%02x' % (52,54,56)
    BUTTON_COLOR = "#000000"
    BAR_COLOR = '#%02x%02x%02x' % (31,106,171)
    SPECIAL_ZONE_COLOR = '#%02x%02x%02x' % (97,97,97) #gris
    FONT_COLOR = "#FFFFFF"
    
    # *** Pour affichage de l'analyse courante :
    # Pour l'analyse YOLO
    NB_OREOS = "--"
    NB_FISSURES = "--"
    NB_MANGES = "--"
    NB_EFFACES = "--"
    NB_DECALES = "--"
    
    # Pour l'analyse OpenCv
    NB_OREOS_OPENCV = "--"
    NB_FISSURES_OPENCV = "--"
    NB_MANGES_OPENCV = "--"
    NB_EFFACES_OPENCV = "--"
    NB_DECALES_OPENCV = "--"
    
    
    # *** Pour affichage de l'analyse globale (stats) :
    NB_TOTAL_OREOS_SANS_DEFAUTS = 0
    NB_TOTAL_OREOS_AVEC_DEFAUTS = 0
    GRAPH_FRAME = None
    STAT_WIDGET = None
    
    
    # *** Pour l'affichage de la communication série
    MESSAGES = ["..."]
    MESSAGE_LIMIT = 10 # Nombre de messages affichés
    
    
    # *** Variables de dimensions 
    DIM_APP = (1536, 864) #(1200,700)
    DIM_CAM = (400,300) #4/3 
    DIM_GRAPH = (DIM_APP[0]//2, 300)
    DIM_COMM  = (DIM_APP[0]//2, 300)
    DIM_BUTTON_FRAME = (135+DIM_APP[0]//3, 100)
    DIM_MACHINE_IMAGE = (135+DIM_APP[0]//3, 370)
    
    PADDING = 10
    
    # Boutons
    ALL_BUTTONS = []
    
    # *** Variables pour le mode auto/manuel + état des actionneurs
    MODE_AUTO = True
    MOTEUR_STATE = 0
    SERVO_STATE = 0
    LED_STATE = 0
    
    SWITCHT1_STATE = 0
    SWITCHT2_STATE = 0
    CAPTEUR_STATE = 0
    
    
    # *** Camera
    # Remettre à 1 quand les tests sont finis
    #CAM = cv2.VideoCapture(0) # à supprimer, décommenter la ligne du dessous
    CAM = None
    
    # Tk
    app = None
    
    
    # Constructeur
    def initialize():
        # Initialisation de la caméra
        #UI.cap = cv2.VideoCapture(1) # 1 pour la caméra usb (mais trop long pour les tests)
        
        # Initialisation fenetre graphique
        UI.app = Tk()
        UI.app.attributes("-fullscreen", True) # Fullscreen mode
        UI.app.title("Oreo Machine")
        UI.app.geometry(str(UI.DIM_APP[0])+"x"+str(UI.DIM_APP[1]))
        UI.app.bind('<Escape>', lambda x: UI.app.destroy()) #Quit on escape
        UI.display()
        UI.app.mainloop()
        
        
    # ********** Fonctions à appeler lors de l'affichage des composants 
    # Fonction pour l'affichage de la vidéo
    def video_stream(cam_label):
        cap = UI.CAM
        # Capture image
        _, frame = cap.read()
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        # Resize et convert
        img = img.resize(UI.DIM_CAM)
        imgtk = ImageTk.PhotoImage(image=img)
        
        # Ajout au label tkinter
        cam_label.imgtk = imgtk
        cam_label.configure(image=imgtk)
        cam_label.after(1, UI.video_stream, cam_label) 
        
    def video_stream2(cam_label, cam_label2):
        cap = UI.CAM
        # Capture image
        _, frame = cap.read()
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        # Resize et convert
        img = img.resize(UI.DIM_CAM)
        imgtk = ImageTk.PhotoImage(image=img)
        
        # Ajout au label tkinter
        cam_label.imgtk = imgtk
        cam_label2.imgtk = imgtk
        cam_label.configure(image=imgtk)
        cam_label2.configure(image=imgtk)
        cam_label2.after(1, UI.video_stream2, cam_label, cam_label2) 
       
    
    # Fonction pour acutalisation de l'analyse :
    def update_analyse_text(analyse_label):
        an_text =  "Oréos        : " + str(UI.NB_OREOS) + "\n"
        an_text += "Fissures    : " + str(UI.NB_FISSURES) + "\n"
        an_text += "Morsures    : " + str(UI.NB_MANGES) + "\n"
        an_text += "Décalages    : " + str(UI.NB_DECALES) + "\n"
        an_text += "Effacements : " + str(UI.NB_EFFACES)
        analyse_label.config(text = an_text)
        UI.app.after(1000, UI.update_analyse_text, analyse_label)
        
    # Fonction pour acutalisation de l'analyse pour openCV :
    def update_analyse_text_opencv(analyse_label):
        an_text =  "Oréos        : " + str(UI.NB_OREOS_OPENCV) + "\n"
        an_text += "Fissures    : " + str(UI.NB_FISSURES_OPENCV) + "\n"
        an_text += "Morsures    : " + str(UI.NB_MANGES_OPENCV) + "\n"
        an_text += "Décalages    : " + str(UI.NB_DECALES_OPENCV) + "\n"
        an_text += "Effacements : " + str(UI.NB_EFFACES_OPENCV)
        analyse_label.config(text = an_text)
        UI.app.after(1000, UI.update_analyse_text_opencv, analyse_label)
        
        
    # Foncction qui affiche le graphique des stats sur les oreos scannés
    def generate_graph(graph_label):
        if UI.STAT_WIDGET != None:
            UI.STAT_WIDGET.destroy()
            
        # Création du graphique en matplot
        dictionnaire = {'Oreos sans défauts': UI.NB_TOTAL_OREOS_SANS_DEFAUTS, 'Oreos avec défauts':UI.NB_TOTAL_OREOS_AVEC_DEFAUTS}
        keys = list(dictionnaire.keys())
        values = list(dictionnaire.values())
        
        # Set colors
        plt.rcParams['text.color'] = "#FFFFFF"
        plt.rcParams['axes.labelcolor'] = "#FFFFFF"
        plt.rcParams['xtick.color'] = "#FFFFFF"
        plt.rcParams['ytick.color'] = "#FFFFFF"
        
        # Création figure
        fig = plt.figure(figsize = (10, 5), facecolor=UI.BACKGROUND_COLOR_SECTIONS_1)
        ax = plt.axes()
        ax.set_facecolor(UI.BACKGROUND_COLOR_SECTIONS_1)
        ax.set_title("Proportion Oréos avec défauts")
        
        plt.ylim(0, 10)
        
        plt.bar(keys, values, color=UI.BAR_COLOR)
      
        # Intégration du graph à la fenetre TK
        canvas = FigureCanvasTkAgg(fig, master = graph_label)  
        canvas.draw()   
        UI.STAT_WIDGET = canvas.get_tk_widget()
        UI.STAT_WIDGET.config(width=UI.DIM_GRAPH[0], height=UI.DIM_GRAPH[1])
        UI.STAT_WIDGET.pack()
        
        
        # Close fig
        plt.close(fig) 
        UI.app.after(5000, UI.generate_graph, graph_label)
        
    
    
    # Fonction qui permet l'affichage de la communication par le port série
    def print_comm(com_label,):
        text = ""
        for i in range(max(0,len(UI.MESSAGES)-UI.MESSAGE_LIMIT), len(UI.MESSAGES)):
            text += UI.MESSAGES[i]+"\n"
        com_label.config(text=text)
        
        UI.app.after(400, UI.print_comm, com_label)
        
        
    # Fonction qui dessine sur le canvas donné les indicateurs d'état de chaque composant
    def draw_components_state(canvas):
        # Variables constantes
        Rayon = 7
        ON_COLOR = "blue"
        OFF_COLOR = "grey"
        Outline_color = "white"
        Outline_width = 2
        Dist_square = 4
        
        # Switch1
        if UI.SWITCHT1_STATE == 0:
            canvas.create_oval(240-Rayon, 12-Rayon, 240+Rayon, 12+Rayon, fill=OFF_COLOR, outline=Outline_color, width=Outline_width)
        elif UI.SWITCHT1_STATE == 1:
            canvas.create_oval(240-Rayon, 12-Rayon, 240+Rayon, 12+Rayon, fill=ON_COLOR, outline=Outline_color, width=Outline_width)
            
        # Switch2
        if UI.SWITCHT2_STATE == 0:
            canvas.create_oval(472-Rayon, 12-Rayon, 472+Rayon, 12+Rayon, fill=OFF_COLOR, outline=Outline_color, width=Outline_width)
        elif UI.SWITCHT2_STATE == 1:
            canvas.create_oval(472-Rayon, 12-Rayon, 472+Rayon, 12+Rayon, fill=ON_COLOR, outline=Outline_color, width=Outline_width)
        
        # Capteur
        if UI.CAPTEUR_STATE == 0:
            canvas.create_oval(540-Rayon, 90-Rayon, 540+Rayon, 90+Rayon, fill=OFF_COLOR, outline=Outline_color, width=Outline_width)
        elif UI.CAPTEUR_STATE == 1:
            canvas.create_oval(540-Rayon, 90-Rayon, 540+Rayon, 90+Rayon, fill=ON_COLOR, outline=Outline_color, width=Outline_width)

        # Servo
        if UI.SERVO_STATE == 0:
            canvas.create_rectangle(510-Rayon, 125-3*Rayon-Dist_square, 510+Rayon, 125-2*Rayon-Dist_square+Rayon, fill=OFF_COLOR, outline=Outline_color, width=Outline_width)
            canvas.create_rectangle(510-Rayon, 125-Rayon, 510+Rayon, 125+Rayon, fill=ON_COLOR, outline=Outline_color, width=Outline_width)
            canvas.create_rectangle(510-Rayon, 125+3*Rayon+Dist_square, 510+Rayon, 125+2*Rayon+Dist_square-Rayon, fill=OFF_COLOR, outline=Outline_color, width=Outline_width)
        elif UI.SERVO_STATE == 1:
            canvas.create_rectangle(510-Rayon, 125-3*Rayon-Dist_square, 510+Rayon, 125-2*Rayon-Dist_square+Rayon, fill=ON_COLOR, outline=Outline_color, width=Outline_width)
            canvas.create_rectangle(510-Rayon, 125-Rayon, 510+Rayon, 125+Rayon, fill=OFF_COLOR, outline=Outline_color, width=Outline_width)
            canvas.create_rectangle(510-Rayon, 125+3*Rayon+Dist_square, 510+Rayon, 125+2*Rayon+Dist_square-Rayon, fill=OFF_COLOR, outline=Outline_color, width=Outline_width)
        elif UI.SERVO_STATE == 2:
            canvas.create_rectangle(510-Rayon, 125-3*Rayon-Dist_square, 510+Rayon, 125-2*Rayon-Dist_square+Rayon, fill=OFF_COLOR, outline=Outline_color, width=Outline_width)
            canvas.create_rectangle(510-Rayon, 125-Rayon, 510+Rayon, 125+Rayon, fill=OFF_COLOR, outline=Outline_color, width=Outline_width)
            canvas.create_rectangle(510-Rayon, 125+3*Rayon+Dist_square, 510+Rayon, 125+2*Rayon+Dist_square-Rayon, fill=ON_COLOR, outline=Outline_color, width=Outline_width)
            
        # Actionneur
        if UI.MOTEUR_STATE == 0:
            canvas.create_rectangle(90-3*Rayon-Dist_square, 125-Rayon, 90-2*Rayon-Dist_square+Rayon, 125+Rayon, fill=OFF_COLOR, outline=Outline_color, width=Outline_width)
            canvas.create_rectangle(90-Rayon, 125-Rayon, 90+Rayon, 125+Rayon, fill=ON_COLOR, outline=Outline_color, width=Outline_width)
            canvas.create_rectangle(90+3*Rayon+Dist_square, 125-Rayon, 90+2*Rayon+Dist_square-Rayon, 125+Rayon, fill=OFF_COLOR, outline=Outline_color, width=Outline_width)
        elif UI.MOTEUR_STATE == 1:
            canvas.create_rectangle(90-3*Rayon-Dist_square, 125-Rayon, 90-2*Rayon-Dist_square+Rayon, 125+Rayon, fill=ON_COLOR, outline=Outline_color, width=Outline_width)
            canvas.create_rectangle(90-Rayon, 125-Rayon, 90+Rayon, 125+Rayon, fill=OFF_COLOR, outline=Outline_color, width=Outline_width)
            canvas.create_rectangle(90+3*Rayon+Dist_square, 125-Rayon, 90+2*Rayon+Dist_square-Rayon, 125+Rayon, fill=OFF_COLOR, outline=Outline_color, width=Outline_width)
        elif UI.MOTEUR_STATE == 2:
            canvas.create_rectangle(90-3*Rayon-Dist_square, 125-Rayon, 90-2*Rayon-Dist_square+Rayon, 125+Rayon, fill=OFF_COLOR, outline=Outline_color, width=Outline_width)
            canvas.create_rectangle(90-Rayon, 125-Rayon, 90+Rayon, 125+Rayon, fill=OFF_COLOR, outline=Outline_color, width=Outline_width)
            canvas.create_rectangle(90+3*Rayon+Dist_square, 125-Rayon, 90+2*Rayon+Dist_square-Rayon, 125+Rayon, fill=ON_COLOR, outline=Outline_color, width=Outline_width)
            
        # Led
        if UI.LED_STATE == 0:
            canvas.create_oval(610-Rayon, 125-Rayon, 610+Rayon, 125+Rayon, fill=OFF_COLOR, outline=Outline_color, width=Outline_width)
        else:
            canvas.create_oval(610-Rayon, 125-Rayon, 610+Rayon, 125+Rayon, fill=ON_COLOR, outline=Outline_color, width=Outline_width)


        # Appel
        UI.app.after(100, UI.draw_components_state, canvas)
        
    
    # Fonction de rafraichissement de l'interface
    def display():
        # ---------- Clear 
        #UI.clear()
        
        # ---------- New display
        UI.app.config(background=UI.BACKGROUND_COLOR)
        #UI.app.after(1000, UI.display)
        
        # Titre
        Title = Label(UI.app,font=("Arial", 20), anchor="nw", text="THE OREO FACTORY", bg=UI.BACKGROUND_COLOR, fg="#FFFFFF")
        Title.pack()
        Title.update()
        Title.place(x=UI.DIM_APP[0]//2-Title.winfo_width()//2, y=5)
        
        # ---------- YOLO : SECTION CAMERA + ANALYSE
        frame_size = (200, 660)
        cam_frame = Frame(UI.app, padx=UI.PADDING, pady=UI.PADDING, width=frame_size[0], height=frame_size[1])
        cam_frame.config(background=UI.BACKGROUND_COLOR_SECTIONS_1)
        
        # *** Titre
        label_title = Label(cam_frame, bg=UI.BACKGROUND_COLOR_SECTIONS_1, fg="#FFFFFF")
        label_title.config(text="YOLO detection")
        label_title.pack()
        
        # *** CAMERA
        cam_label = Label(cam_frame)
        #UI.video_stream(cam_label)
        cam_label.pack()
    
        # *** Analyse
        analyse_label = Label(cam_frame,font=("Arial", 16))
        analyse_label.config(background=UI.SPECIAL_ZONE_COLOR)
        UI.update_analyse_text(analyse_label)
        analyse_label.pack(pady=(10,0), fill=BOTH)
        
        
        cam_frame.pack(padx = 10, pady=20)
        cam_frame.update()
        cam_frame.place(x=UI.PADDING, y=UI.DIM_APP[1]-cam_frame.winfo_height()-2*UI.PADDING-UI.DIM_GRAPH[1])
        
        
        # ---------- OPENCV : SECTION CAMERA + ANALYSE
        frame_size2 = (200, 660)
        cam_frame2 = Frame(UI.app, padx=UI.PADDING, pady=UI.PADDING, width=frame_size2[0], height=frame_size2[1])
        cam_frame2.config(background=UI.BACKGROUND_COLOR_SECTIONS_1)
        
        # *** Titre
        label_title2 = Label(cam_frame2, bg=UI.BACKGROUND_COLOR_SECTIONS_1, fg="#FFFFFF")
        label_title2.config(text="OPENCV detection")
        label_title2.pack()
        
        # *** CAMERA
        cam_label2 = Label(cam_frame2)
        #UI.video_stream2(cam_label2)
        cam_label2.pack()
        
        # *** Analyse
        analyse_label2 = Label(cam_frame2,font=("Arial", 16))
        analyse_label2.config(background=UI.SPECIAL_ZONE_COLOR)
        UI.update_analyse_text_opencv(analyse_label2)
        analyse_label2.pack(pady=(10,0), fill=BOTH)
        
        cam_frame2.pack(padx = 10, pady=20)
        cam_frame2.update()
        cam_frame2.place(x=cam_frame2.winfo_width()+2*UI.PADDING, y=UI.DIM_APP[1]-cam_frame2.winfo_height()-2*UI.PADDING-UI.DIM_GRAPH[1])
        
        
        # Appel commun pour les deux cameras
        UI.video_stream2(cam_label, cam_label2)
        cam_frame.update()
        cam_frame2.update()
        cam_frame.place(x=UI.PADDING, y=UI.DIM_APP[1]-cam_frame.winfo_height()-2*UI.PADDING-UI.DIM_GRAPH[1])
        cam_frame2.place(x=cam_frame2.winfo_width()+2*UI.PADDING, y=UI.DIM_APP[1]-cam_frame2.winfo_height()-2*UI.PADDING-UI.DIM_GRAPH[1])
        
        
        
        
        # ---------- SECTION Graphique pour stats
        graph_frame = Frame(UI.app, width=UI.DIM_GRAPH[0] - 2*UI.PADDING, height=UI.DIM_GRAPH[1] - 2*UI.PADDING)
        graph_frame.config(background=UI.BACKGROUND_COLOR_SECTIONS_1)
        UI.GRAPH_FRAME = graph_frame
        
        UI.generate_graph(graph_frame)
        
        graph_frame.pack()
        graph_frame.place(x=UI.PADDING, y=UI.DIM_APP[1]-UI.DIM_GRAPH[1]-UI.PADDING)
        
        
        
        # ---------- SECTION Affichage de la communication Serial
        serial_frame = Frame(UI.app, padx=10, pady=10, width=UI.DIM_COMM[0]-3*UI.PADDING, height=UI.DIM_COMM[1])
        serial_frame.config(background=UI.BACKGROUND_COLOR_SECTIONS_1)
        serial_frame.pack_propagate(0)
        #serial_frame.pack()
        serial_frame.place(x=UI.DIM_APP[0]-UI.DIM_COMM[0]+2*UI.PADDING, y=UI.DIM_APP[1]-UI.DIM_COMM[1]-UI.PADDING)
        sf_title_label = Label(serial_frame, font=("Arial", 16), anchor="nw", text="Serial port communication")
        sf_title_label.config(background=UI.BACKGROUND_COLOR_SECTIONS_1, fg="#FFFFFF")
        sf_title_label.pack()
        
        serial_label = Label(serial_frame,font=("Arial", 16), anchor="nw", width=200, height=20)
        serial_label.config(background=UI.SPECIAL_ZONE_COLOR)
        UI.print_comm(serial_label)
        serial_label.pack()
        
        
        
        
        # ---------- SECTION commande des boutons
        buttons_frame = Frame(UI.app, padx=10, pady=10, width=UI.DIM_BUTTON_FRAME[0], height=UI.DIM_BUTTON_FRAME[1])
        buttons_frame.config(bg=UI.BACKGROUND_COLOR_SECTIONS_1)
        buttons_frame.pack_propagate(0)
        buttons_frame.pack()
        buttons_frame.update()
        buttons_frame.place(x=2*cam_frame2.winfo_width()+3*UI.PADDING, y=UI.DIM_APP[1]-buttons_frame.winfo_height()-UI.DIM_COMM[1]-2*UI.PADDING)
        
        buttons_title = Label(buttons_frame, font=("Arial", 16), text="Control panel")
        buttons_title.config(bg=UI.BACKGROUND_COLOR_SECTIONS_1, fg="#FFFFFF")
        buttons_title.pack()
        
        
        sub_frame_button = Frame(buttons_frame, padx=10, pady=10)
        sub_frame_button.config(bg=UI.BACKGROUND_COLOR_SECTIONS_1)
        sub_frame_button.pack(fill=BOTH)
        sub_frame_button.place(in_=buttons_frame, anchor="c", relx=.5, rely=.8)
        
        
        # CREATION DES BOUTONS 
        # Auto
        button_auto = Button(sub_frame_button, text="Manuel", width=8, fg=UI.FONT_COLOR, font=("Arial", 12), command=lambda: UI.change_mode(button_auto))
        button_auto.config(background="#AAAAAA", fg="#000000")
        button_auto.pack(side=LEFT, padx=3)
        
        # Push
        button_push = Button(sub_frame_button, text="Push", width=8,command=UI.set_push, fg=UI.FONT_COLOR, font=("Arial", 12))
        button_push.config(background=UI.BUTTON_COLOR)
        button_push.pack(side=LEFT, padx=3)
        
        # Pull
        button_pull = Button(sub_frame_button, text="Pull", width=8, command=UI.set_pull, fg=UI.FONT_COLOR, font=("Arial", 12))
        button_pull.config(background=UI.BUTTON_COLOR)
        button_pull.pack(side=LEFT, padx=3)
        
        # Servo_good
        button_servo_left = Button(sub_frame_button, text="Servo L", width=8, command=UI.set_servoL, fg=UI.FONT_COLOR, font=("Arial", 12))
        button_servo_left.config(background=UI.BUTTON_COLOR)
        button_servo_left.pack(side=LEFT, padx=3)
        
        # Servo_horizontal
        button_servo_horizont = Button(sub_frame_button, text="Servo H", width=8, command=UI.set_servoH, fg=UI.FONT_COLOR, font=("Arial", 12))
        button_servo_horizont.config(background=UI.BUTTON_COLOR)
        button_servo_horizont.pack(side=LEFT, padx=3)
        
        # Servo_bad
        button_servo_right = Button(sub_frame_button, text="Servo R", width=8, command=UI.set_servoR, fg=UI.FONT_COLOR, font=("Arial", 12))
        button_servo_right.config(background=UI.BUTTON_COLOR)
        button_servo_right.pack(side=LEFT, padx=3)
        
        # LED
        button_led = Button(sub_frame_button, text="LED", width=8, command=UI.set_led, fg=UI.FONT_COLOR, font=("Arial", 12))
        button_led.config(background=UI.BUTTON_COLOR)
        button_led.pack(side=LEFT, padx=3)
        
        
        UI.ALL_BUTTONS.extend([button_push, button_pull, button_servo_right, button_servo_left, button_servo_horizont, button_led])
        for b in UI.ALL_BUTTONS:
            b["state"] = "disabled"
            
            
            
        # ---------- SECTION affichage des etapes en cours de la machine
        image_frame = Frame(UI.app, padx=10, pady=10, width=UI.DIM_MACHINE_IMAGE[0], height=UI.DIM_MACHINE_IMAGE[1])
        image_frame.config(background=UI.BACKGROUND_COLOR_SECTIONS_1)
        image_frame.pack_propagate(0)
        image_frame.place(x=2*cam_frame2.winfo_width()+3*UI.PADDING, y=UI.DIM_APP[1]-buttons_frame.winfo_height()-UI.DIM_COMM[1]-3*UI.PADDING-UI.DIM_MACHINE_IMAGE[1])
        # Titre
        title_image_label = Label(image_frame,font=("Arial", 16), text="Machine state", fg="#FFFFFF")
        title_image_label.config(background=UI.BACKGROUND_COLOR_SECTIONS_1)
        title_image_label.pack()
        # Image
        canvas = Canvas(image_frame, width=625, height=250, highlightthickness=0, bg=UI.BACKGROUND_COLOR_SECTIONS_1)
        image = Image.open("OreoMachine.png").convert("RGBA")
        image = ImageTk.PhotoImage(image.resize((625, 250), Image.ANTIALIAS))
        label_test = Label(image=image) 
        label_test.image = image
        canvas.pack(expand=True)
        canvas.create_image(0,0,anchor='nw', image=image)
        
        # Dessin des indicateurs d'état
        UI.draw_components_state(canvas)
        

    
    # ---------- Fonctions de commande des boutons ----------
    # Fonction pour click du bouton "mode auto"
    def change_mode(button):
        if button['text'] == "Manuel":
            # Change text
            button.config(text="Auto")
            # Change state variable
            UI.MODE_AUTO = False
            UI.SERVO_STATE = 0
            UI.MOTEUR_STATE = 0
            UI.LED_STATE = 0
            # enable button
            for b in UI.ALL_BUTTONS:
                b["state"] = "normal"
                
        elif button['text'] == "Auto":
            button.config(text="Manuel")
            UI.MODE_AUTO = True
            # disable button
            for b in UI.ALL_BUTTONS:
                b["state"] = "disabled"
                
    def set_push():
        UI.MOTEUR_STATE = 2
    
    def set_pull():
        UI.MOTEUR_STATE = 1
        
    def set_stop_moteur():
        UI.MOTEUR_STATE = 0
        
    def set_servoR():
        UI.SERVO_STATE = 1
        
    def set_servoL():
        UI.SERVO_STATE = 2
        
    def set_servoH():
        UI.SERVO_STATE = 0
        
    def set_led():
        if UI.LED_STATE == 1:
            UI.LED_STATE = 0
        else:
            UI.LED_STATE = 1
        
        
    
    # Remet les valeurs d'analyse aux valeurs "--"
    def reset_analyse():
        UI.NB_OREOS = "--"
        UI.NB_FISSURES = "--"
        UI.NB_MANGES = "--"
        UI.NB_EFFACES = "--"
        UI.NB_DECALES = "--"
        
        UI.NB_OREOS_OPENCV = "--"
        UI.NB_FISSURES_OPENCV = "--"
        UI.NB_MANGES_OPENCV = "--"
        UI.NB_EFFACES_OPENCV = "--"
        UI.NB_DECALES_OPENCV = "--"
    
    
    
    # Efface tous les composants de la fenetre
    def clear():
        l = UI.app.winfo_children()

        for element in l :
            if element.winfo_children() :
                l.extend(element.winfo_children())

        all_widgets = l
        for widg in all_widgets:
            widg.pack_forget()
        
    
    # Ferme la fenetre graphique
    def destroy():
        UI.app.quit()
        
        
    # set cam
    def set_cam(cam):
        UI.CAM = cam
        
       
        
       



# POUR UTILISER L'INTERFACE SEULE (SANS LA MACHINE)
print("Penser à décommenter le UI.init() pour que ça fonctionne")
'''
try:
    UI.initialize()
except Exception as e:
    UI.destroy()
    UI.CAM.release()
    print(e)
'''