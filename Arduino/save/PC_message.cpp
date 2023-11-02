#include "PC_message.hpp"


PC_message::PC_message(String message){
  initial_message = message;
  parse_string();
}

    
void PC_message::parse_string(){
  String message = initial_message;
  String delimiter = ",";
  size_t pos_start = 0, pos_end, delim_len = delimiter.length();
  String token;
  MyVector<String> parsed;

  while ((pos_end = message.find(delimiter, pos_start)) != std::string::npos) {
      token = message.substr(pos_start, pos_end - pos_start);
      pos_start = pos_end + delim_len;
      parsed.append(token);
  }
  parsed.append(message.substr(pos_start));


  checkLen = stoi(parsed.get_at(0));
  checkSum = stoi(parsed.get_at(1));
  idMessage = stoi(parsed.get_at(2));
  MotorV = stoi(parsed.get_at(3));
  ServoV = stoi(parsed.get_at(4));
  LedV = stoi(parsed.get_at(5));
}
     
        

// Retourne True si le message est valide, False sinon
bool PC_message::checkIntegrity(){
  // Controle de l'intégrité du message reçu
  nb_car = message.substr(6, pos_end - initial_message.get_length()).get_length()
  if(nb_car != checkLen){
    return false;
  }
  
  // Controle de l'intégrité par somme des ascii
  int ascii_sum = 0;
  for(int i = 6; i < initial_message.get_length(); i++){
    ascii_sum = ascii_sum + int(initial_message.at(i));
  }
  ascii_sum = ascii_sum%10000;
  if(checkSum != ascii_sum){
    return false;
  }
      
  return true;
}
