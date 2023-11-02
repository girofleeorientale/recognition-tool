/**********************************************************************************************************************
 Programmation des composants Arduino
***********************************************************************************************************************/

// Importation / initialisation des variables pour les LED RGB
#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
#include <avr/power.h> // Required for 16 MHz Adafruit Trinket
#endif
#define LEDRGBpin 4 //LED RGB
#define NUMPIXELS 12
Adafruit_NeoPixel LEDRGB(NUMPIXELS, LEDRGBpin, NEO_GRB + NEO_KHZ800); //LED RGB

// Importation / initialisation des variables pour le Servo
#include <Servo.h>
Servo myservo;

// Autres importations
#include <Chrono.h>
#include <string.h>
#include "Vector.cpp"
//#include "ARDUINO_message.cpp"
//#include "PC_message.cpp"
using namespace std;


// Définition des variables Pinout
#define ServoPin 6
#define MotorPin1 8
#define MotorPin2 9
#define FDC1Pin 36
#define FDC2Pin 34
#define ProxPin 12

// Variables globales
MyVector<String> Messages; // File de messages reçus
String message = ""; // Stocke le message brut reçu
String instruction = ""; // Stocke l'instruction du message reçu
String current_message = "";
int state = 0;
int message_count = 0;

// Variables d'état
unsigned int stateSwitch1 = 0; // 0 -> neutre; 1 -> pull; 2 -> push
unsigned int stateSwitch2 = 0; // 0 -> neutre; 1 -> goodOreo; 2 -> badOreo
unsigned int stateCapteur = 0; // 0 ... voir plus tard pour les leds
    
// Variables des controleurs de la machine
unsigned int stateMotor = 0;
unsigned int stateServo = 0;
unsigned int stateLed = 0;

// Variables de temps
unsigned long dateMessage = millis();; // Date d'envoi du dernier message
int deltaMessage = 500; // Envoyer un message tous les 500 ms





/************************************************************************************************
* CLASSE ARDUINO_message (Objet représentant le message à envoyer au PC)
************************************************************************************************/
class ARDUINO_message{
  public:
    //static unsigned int ID_MESSAGE;

    unsigned int idMessage;
    unsigned int stateSwitch1;
    unsigned int stateSwitch2;
    unsigned int stateCapteur;
  
  
  ARDUINO_message(unsigned int stateS1, unsigned int stateS2, unsigned int stateC){
    //idMessage = ARDUINO_message::ID_MESSAGE;
    stateSwitch1 = stateS1;
    stateSwitch2 = stateS2;
    stateCapteur = stateC;

    //ARDUINO_message::ID_MESSAGE++;
  }

     
  // Construit le message à envoyer à partir des attributs de l'objet
  String toString(){
    // --- Concatenation des attributs
    String message = ",";
    message = message + String(idMessage) + ",";
    message = message + String(stateSwitch1) + ",";
    message = message + String(stateSwitch2) + ",";
    message = message + String(stateCapteur);

    // --- Calcul des checkSum
    int nb_car = message.length();

    int ascii_sum = 0;
    for(int i = 0; i<message.length(); i++){
      ascii_sum += int(message.charAt(i));
    } 
    ascii_sum = ascii_sum%10000;

    // Convert in str
    String nb_car_string = String(nb_car);
    if(nb_car_string.length()!=2){
      nb_car_string = "0"+nb_car_string;
    }

    String ascii_sum_string = String(ascii_sum);
    for(int l = 0; l<=3-String(ascii_sum).length(); l++){
      ascii_sum_string = "0"+ascii_sum_string;
    }

    // On les ajoute au message
    message = nb_car_string + "," + ascii_sum_string + message;
    return message;
  }

};





/************************************************************************************************
* CLASSE PC_message (Objet représentant le message reçu de la part du PC)
************************************************************************************************/
class PC_message{
  public :
    unsigned int checkLen;
    unsigned int checkSum;
    unsigned int idMessage;
    unsigned int MotorV;
    unsigned int ServoV;
    unsigned int LedV;
    String initial_message;


  PC_message(String message){
    initial_message = message;
    parse_string();
  }


  void parse_string(){
    String message = initial_message;
    String token;
    MyVector<String> parsed;

    int begin = 0;
    int end = 0;
    for(int i = 0; i<message.length(); i++){
      if(String(message.charAt(i)).compareTo(String(','))!=0){
        end++;
      }
      else{
        if(begin < end){
          parsed.append(message.substring(begin, end));
          begin = end + 1;
          end = begin;
        }
      }
    }
    parsed.append(message.substring(begin, end+1));


    checkLen = (parsed.get_at(0)).toInt();
    checkSum = (parsed.get_at(1)).toInt();
    idMessage = (parsed.get_at(2)).toInt();
    MotorV = (parsed.get_at(3)).toInt();
    ServoV = (parsed.get_at(4)).toInt();
    LedV = (parsed.get_at(5)).toInt();
  }
     
        

  // Retourne True si le message est valide, False sinon
  bool checkIntegrity(){
    // Controle de l'intégrité du message reçu
    int nb_car = initial_message.substring(7, initial_message.length()).length();
    if(nb_car != checkLen){
      return false;
    }
    
    // Controle de l'intégrité par somme des ascii
    int ascii_sum = 0;
    for(int i = 7; i < initial_message.length(); i++){
      ascii_sum = ascii_sum + int(initial_message.charAt(i));
    }
    ascii_sum = ascii_sum%10000;
    if(checkSum != ascii_sum){
      return false;
    }
        
    return true;
  }
};







/***************************************************************************************************
* Partie principale du programme : initialisation + gestion de la communication avec le PC
***************************************************************************************************/

// Fonction setup lancée une fois au démarage
void setup() {
  delay(1000);
  Serial.begin(57600); // Au max 57600

  //Initialisation LED RGB
  LEDRGB.begin();
  LEDRGB.clear();

  //Initialisaiton servo
  myservo.attach(ServoPin);

  //Initilisation moteur
  pinMode(MotorPin1, OUTPUT);
  pinMode(MotorPin2, OUTPUT);
  // On mets l'actionneur à l'arret
  digitalWrite(MotorPin1, LOW);
  digitalWrite(MotorPin2, LOW);

  //Initialisation fin de course (0 quand activé, sinon 5V)
  pinMode(FDC1Pin, INPUT_PULLUP);
  pinMode(FDC2Pin, INPUT_PULLUP);

  //Initialisation capteur proximité
  pinMode(ProxPin, INPUT);

  myservo.write(80);
}


// Fonction loop lancée en boucle après la fonction setup
void loop() {
  // Mise à jour des variables de capteurs
  if(digitalRead(FDC1Pin)==0){stateSwitch1 = 1;}else{stateSwitch1 = 0;}
  if(digitalRead(FDC2Pin)==0){stateSwitch2 = 1;}else{stateSwitch2 = 0;}
  if(digitalRead(ProxPin)==0){stateCapteur = 1;}else{stateCapteur = 0;}

  if((stateMotor == 1 && stateSwitch1 == 1) || (stateMotor == 2 && stateSwitch2 == 1)){
    digitalWrite(MotorPin1, LOW);
    digitalWrite(MotorPin2, LOW);
  }

  
  // ********** Envoyer un message toutes les X millisec **********
  if((millis()-dateMessage) >= deltaMessage){
    dateMessage = millis();
    ARDUINO_message ar_message = ARDUINO_message(stateSwitch1, stateSwitch2, stateCapteur);
    ar_message.idMessage = message_count;
    message_count ++;
    String message = ar_message.toString();
    Serial.println(message);
  } 



  // ********** Tentative de réception d'un message de PC *********
  ReceiveMessage();
  
            
  if(current_message != instruction){ //Messages.get_length()>0){
    //current_message = Messages.get_first();
    current_message = instruction;
    // 1) Créer un objet PC message
    PC_message message_object = PC_message(current_message);
    // 2) Vérifier son intégrité
    bool is_valid = message_object.checkIntegrity();
    if(is_valid){
      stateMotor = message_object.MotorV;
      stateServo = message_object.ServoV;
      stateLed = message_object.LedV;
    }

    // Positionnement du Servo 
    if(stateSwitch1 == 1){ // -> A condition que le switch de fin de course ne soit pas acctivé
      if(stateServo == 0){
        myservo.write(80);
      }
      if(stateServo == 1){
        myservo.write(130);
      }
      if(stateServo == 2){
        myservo.write(30);
      }
    }      


    // Mouvements de l'actionneur
    if(stateMotor == 0){ // Arret de l'actionneur
      digitalWrite(MotorPin1, LOW);
      digitalWrite(MotorPin2, LOW);
    }
    else{
      if(stateCapteur == 1){ // -> A condition que le plateau soit droit
        if(stateMotor == 1){ // pull actionneur
          if(stateSwitch1 != 1){ // -> si on est pas déjà en bout de course
            digitalWrite(MotorPin1, LOW);
            digitalWrite(MotorPin2, HIGH);
          }
        }
        if(stateMotor == 2){ // push actionneur
          if(stateSwitch2 != 1){ // -> Si on est pas déjà en bout de course (de l'autre coté)
            digitalWrite(MotorPin1, HIGH);
            digitalWrite(MotorPin2, LOW);
          }
        }
      }
    }


    // Gestion des LEDS
    if(stateLed == 0){
      set_leds(0,0,0);
    }
    if(stateLed == 1){
      set_leds(0,5,0);
    }
    if(stateLed == 2){
      set_leds(5,0,0);
    }

    
  }

  

}
  
  



// Display vector
void display(MyVector<String> v){
  for(int i = v.reading_pointer; i<v.current; i++){
    Serial.println("- "+v.arr[i]);
  }
}

/********** Fonction de lecture d'un message **********/
void ReceiveMessage(){
  if(Serial.available()>0){
    char char_read = ' ';
    while(Serial.available()>0){
      char_read = Serial.read();
      if(char_read != '\n'){
        message = message+char_read;
      }
      else{
        instruction = message; // On stocke le message dans instruction
        //Messages.append(instruction); // On ajout ce message à la file des messages
        message = ""; // On efface le buffer message qui servait juste à lire l'entrée
      }
    }
  } 
}





/********** Fonctions pour les LEDS **********/
// Donne une couleur aux leds sans 'animation'
void set_leds(int r, int g, int b){
  for (int i = 0; i < NUMPIXELS ; i++){ 
    LEDRGB.setPixelColor(i, LEDRGB.Color(r, g, b));
  }
  LEDRGB.show();
}
// Donne une couleur aux leds avec 'animation'
void set_leds_animate(int r, int g, int b){
  for (int i = 0; i < NUMPIXELS ; i++){ 
    LEDRGB.setPixelColor(i, LEDRGB.Color(r, g, b));
    delay(100);
    LEDRGB.show();
  }
}
void funny_leds(){
  while(1){
    int  r = random(256);
    int g = random(256);
    int b = random(256);
    int  i = random(13);
    
    LEDRGB.setPixelColor(i, LEDRGB.Color(r, g, b));
    delay(100);
    LEDRGB.show();
  }
}











    

