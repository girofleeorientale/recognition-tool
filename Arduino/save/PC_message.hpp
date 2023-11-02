#ifndef _PC_message_H
#define _PC_message_H

#include "Vector.cpp"


class PC_message{
  public:
    unsigned int checkLen;
    unsigned int checkSum;
    unsigned int idMessage;
    unsigned int MotorV;
    unsigned int ServoV;
    unsigned int LedV;
    String initial_message;

    // Constructeur
    PC_message(String message);

    // Parse a string message
    void parse_string();
     
    // Retourne True si le message est valide, False sinon
    bool checkIntegrity();
};


#endif
