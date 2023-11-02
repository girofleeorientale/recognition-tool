#include "ARDUINO_message.hpp"


ARDUINO_message::ARDUINO_message(unsigned int stateS1, unsigned int stateS2, unsigned int stateC){
  idMessage = ARDUINO_message::ID_MESSAGE;
  stateSwitch1 = stateS1;
  stateSwitch2 = stateS2;
  stateCapteur = stateC;

  ARDUINO_message::ID_MESSAGE++;
}
     
    

// Construit le message à envoyer à partir des attributs de l'objet
String ARDUINO_message::String toString(){
  // --- Concatenation des attributs
  String message = "";
  message = message + to_string(idMessage);
  message = message + to_string(stateSwitch1);
  message = message + to_string(stateSwitch2);
  message = message + to_string(stateCapteur);

  // --- Calcul des checkSum
  int nb_car = message.get_length();

  int ascii_sum = 0;
  for(int i = 0; i<message.get_length(); i++){
    ascii_sum += ord(message.at(i));
  } 
  ascii_sum = ascii_sum%10000;

  // Convert in str
  String nb_car_string = to_string(nb_car);
  if(nb_car_string.get_length()!=2){
    nb_car_string = "0"+nb_car_string;
  }

  String ascii_sum_string = to_string(ascii_sum);
  for(int l = 0; l<=3-to_string(ascii_sum).get_length(); l++){
    ascii_sum_string = "0"+ascii_sum_string;
  }

  // On les ajoute au message
  message = nb_car_string + "," + ascii_sum_string + "," + message;
  return message;
}