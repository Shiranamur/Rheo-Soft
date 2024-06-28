
/*************************************************** Déclaration des variables **********************************************/


int cnt = 0;
int imp = 0;
char inByte = 0;
float debit = 0;
float ancien_debit = 0; 

float Commande_pompe = 0;
int Setpoint = 0;

int Buzzer = 6;
int Analog_pump_In = 10;
int Flowmeter = 2;
/********************************************************* INITIALISATIONS ****************************************************/

void demarrage_pompe()   // Démarrage progressif de la pompe jusqu'a Setpoint = 100 ( ~ 2V )
  {
    for (Setpoint=0; Setpoint <=200; Setpoint++)
      {
        analogWrite(Analog_pump_In, Setpoint);  // PWM de la pompe conecté a la broche 3 du Arduino uno
        delay(50);
        //Serial.println(Setpoint);
      }
  }


void Alarme()                 //Alerte de Sécurité en cas de disfonctionnement du refroidissement des Peltiers 
  {
    analogWrite(Buzzer, 127);      // Envoie d'une fréquence d'~ 500Hz sur un HP  ---> Broche 6 du Arduino Uno
  }

  void Alarme_Stop()                 //Alerte de Sécurité en cas de disfonctionnement du refroidissement des Peltiers 
  {
    analogWrite(Buzzer, 0);      // Envoie d'une fréquence d'~ 500Hz sur un HP  ---> Broche 6 du Arduino Uno
  }
  

void setup()   
    { 
     pinMode(Flowmeter, INPUT);           // On positionne la broche 2 en entrée pour y connecter le signal en provenance du Débimetre
                                          // provenant du débimetre (compteur d'impulsions)
     pinMode(Analog_pump_In, OUTPUT);
     pinMode(Buzzer, OUTPUT);
     
     Serial.begin(115200);   // on initialise la communication serie         
   

     cli(); // Désactive l'interruption globale
     bitClear (TCCR2A, WGM20); // WGM20 = 0
     bitClear (TCCR2A, WGM21); // WGM21 = 0 
     TCCR2B = 0b00000110; // Clock / 256 soit 16 micro-s et WGM22 = 0
     TIMSK2 = 0b00000001; // Interruption locale autorisée par TOIE2
     sei(); // Active l'interruption globale
     attachInterrupt(0, gestionINT0, RISING);

     delay(500);

     demarrage_pompe();
     
    }    

/******************************************************* PROGRAMME PRINCIPAL ***************************************************/

void loop()
    {
                  
     //if(debit != ancien_debit)
     //{
      Serial.print(debit);
      Serial.println(" L/min");        
      delay(500);
      //ancien_debit = debit;      
     //} 

     if (debit == 0)
     {
      Alarme();
     }
     if (debit > 0)
     {
      Alarme_Stop();
     }
     
     if(Serial.available() > 0) 
       {          
         Commande_pompe = Serial.parseFloat();
         Setpoint = Commande_pompe*51;        // Conversion des volts en commande de PWM 0 5V --> 0 255
         constrain(Setpoint, 0, 200);        // Securité pour empêcher la commande de la pompe de dépasser 2.5V et ainsi limiter la surpression dans le circuit de refroidissement des Peltiers
         Serial.print(Setpoint);
         Serial.print("Nouvelle consigne: ");
         Serial.print(Commande_pompe);
         Serial.println(" V");
         analogWrite(Analog_pump_In, Setpoint);
         delay(200);
        }
      
              
    }

/********************************************************** SOUS-FONCTIONS *******************************************************/     

// Routines d'interruption

// A chaque impulsion reçue, on incrémente la variable imp
void gestionINT0() 
    {
     imp = imp+1;          
    }
 
 
// On va compter le nombre d'impulsions envoyé par le capteur par tranche de 0.5 secondes 
ISR(TIMER2_OVF_vect) 
     {
      TCNT2 = 6; //  4 ms
      cnt++;   
      if (cnt > 125)  // 125 * 4 ms = 500 ms 
        {
         debit = float(imp)*0.048; // -----------------------------------------> débit [L.sec] = (Nb d'impulsions / 2500)* 2  
                                   //                                                                [L]                  [sec]
                                   //                                            DONC  débit [L.min] = (Nb d'impulsions / 2500)* 2 * 60 = Nb d'impulsions * 0.048         
         cnt = 0;     // On réinitialise le compteur cnt                   
         imp = 0;    //  On réinitialise le compteur d'impulsion               
        }             
     }
    
    
