#ifndef _ARDUINO_message_H
#define _ARDUINO_message_H
 


class ARDUINO_message{
  public:
    static int ID_MESSAGE;

    unsigned int idMessage;
    unsigned int stateSwitch1;
    unsigned int stateSwitch2;
    unsigned int stateCapteur;
    
    ARDUINO_message(unsigned int stateS1, unsigned int stateS2, unsigned int stateC);

    // Construit le message à envoyer à partir des attributs de l'objet
    String toString();
};
 
#endif