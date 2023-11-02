#include <stdio.h>
using namespace std;

template <typename T> class MyVector {
public:
  T* arr;
  int capacity; // Place disponible dans le vecteur
  
  int current; // Nombre d'éléments dans le vecteur == tete d'ecriture
  int reading_pointer; // Tete de lecture
 
public:
  // Initialisation d'un vecteur
  MyVector(){
    arr = new T[1];
    capacity = 1;
    current = 0;
    reading_pointer = 0;
  }
       
  // Desctructeur d'objet
  ~ MyVector(){
    delete [] arr;
  }
 

  // Ajout d'un élément en fin de vecteur ( => push_back(element) )
  void append(T element){
    // Si le vecteur est plein, aggrandissement + recopie des éléments
    if(current == capacity){
      T* tmp = new T[2*capacity];
      for (int i = 0; i < capacity; i++) {
        tmp[i] = arr[i];
      }
      delete[] arr; // On supprime l'ancien contenu
      capacity *= 2; // La capacité est doublée
      arr = tmp; // On affecte notre nouveau tableau de taille * 2
    }

    // quand le tableau est de taille suffisante, on ajoute l'élement
    arr[current] = element;
    current++;
  }



  T get_first(){
    if(current<=reading_pointer){
      return "";
    }
    else{
      T element = arr[reading_pointer];
      reading_pointer++;
      return element;
    }
  }

  T get_at(int i){
    int tmp = reading_pointer + i;
    return arr[tmp];
  }
 
    
 
  //getters
  int get_length() { return current - reading_pointer;}
  int get_size() { return current; }
  int get_capacity() { return capacity; }
};
 
