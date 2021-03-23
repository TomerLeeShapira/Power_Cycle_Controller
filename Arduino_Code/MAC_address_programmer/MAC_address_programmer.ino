// python-build-start
// upload
// arduino:megaavr:uno2018
// COM4
// python-build-end

// The above snippet is used to configure the custom programmer script


#include <EEPROM.h>
//#include <avr/eeprom.h>
#include "MAC_address.h"

void setup()
{
  Serial.begin(9600);
  Serial.print("Storing MAC: ");
  for (int i = 0; i < sizeof(mac); i++){
    Serial.print(mac[i], HEX);
  }
  Serial.print('\n');
  EEPROM.put(0, mac);
  Serial.println("Done");
}

void loop()
{
  // Nothing to do here
}
