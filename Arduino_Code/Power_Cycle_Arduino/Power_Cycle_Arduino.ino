// python-build-start
// upload
// arduino:megaavr:uno2018
// COM4
// python-build-end

// The above snippet is used to configure the custom programmer script

/*
 * Burn In Oven Power Cycle Controller
 * 
 * The arduino acts as a web server that allows for remote control of burn in 
 * parameters. There is also a display and buttons attached for simple control
 * and monitoring on the floor. All major configuration parameters are set 
 * over the network using the Power Cycling Monitor Python program. To reload
 * default settings if something breaks and the device does not communicate, 
 * reprogram the arduino with this sketch and follow the instructions in the 
 * serial window. 
 * 
 */

#include <SPI.h>
#include <EEPROM.h>
#include <Ethernet.h>
#include <Wire.h>
#include <Adafruit_RGBLCDShield.h>
#include <utility/Adafruit_MCP23017.h>


// FUNCTIONS....
void check_for_client();
void command_parser(char* command);
bool check_if_ready();
void power_cycle_board();
void stop_and_reset();
bool start_process();
void check_if_done();

// GLOBALS....

// Ethernet uses pins 13, 12, 11, 10, 4.
// Set this to the pin controlling the power transistor.
#define BOARD_PIN 8

// READY    =       Ready to run. All parameters are set correctly. 
// RUNNING  =       Running process. 
// DONE     =       Done with CYCLING ONLY. Power may still be on if it was requested to be.
// STANDBY  =       DEFAULT STATE. Boards are off, parameters are not set (or not determined to be so). 
enum STATE {
  READY, RUNNING, DONE, STANDBY
}; 

// For values passed in by host software and values passed back.
struct parameters {
  int cycle_period;
  int start_delay;
  int duty_cycle;
  int num_cycles;
  int end_state;
  int current_cycle;
  int current_power_state;
} device_parameters;

// For internal stuff only. 
struct machine {
  STATE state;
  unsigned long timer_duration;
  unsigned long start_time;
  unsigned long on_time;
  unsigned long off_time;
  int pin_power;
} state_machine;

// MACROS....

// Used for the lcd. 
#define WHITE 0x7

//inline void FLIP_POWER()
//{
//  digitalWrite(BOARD_PIN, TOGGLE(state_machine.pin_power));
//
//  // Note that the state of the power is always the opposite of the board pin. 
//  device_parameters.current_power_state = ~state_machine.pin_power;
//}

// Set the state of BOARD_PIN
void SET_POWER(int val)
{
  // Note that the state of the power is always the opposite of the board pin value. 
  device_parameters.current_power_state = val;  
  state_machine.pin_power = !val;
  digitalWrite(BOARD_PIN, !val);
}

// Easier to read than writing strncmp each time. strncmp compares the first input to the second 
// for the number of chars passed as the third input. So, in this case, if cmd[0 to 2] == val. 
// It returns 0 if yes. So, this macro will return true. 
#define is_command(cmd, val) (strncmp(cmd, val, 3) == 0)


// Objects....
IPAddress device_IP;  // IP Address is not static....
EthernetServer server(80);

// Adafruit LCD shield uses the I2C SCL and SDA pins.
Adafruit_RGBLCDShield lcd = Adafruit_RGBLCDShield();


//////////////////////////////////////////////////////////////////////////////////
// THIS IS THE SETUP PROCESS. 
//////////////////////////////////////////////////////////////////////////////////
// This is mostly taken from the ethernet server example.
void setup()
{
  
  // Init the board pin to be HIGH, (burn-in power turned off).  
  pinMode(BOARD_PIN, OUTPUT);
  state_machine.state = STANDBY;
  SET_POWER(0);

  // LCD is 16cols x 2rows. 
  lcd.begin(16, 2);

  lcd.print("INITIALIZING");
  lcd.setBacklight(WHITE);

  // Move cursor to 2nd row of LCD for status printing.
  lcd.setCursor(0, 1);

  // Pull the MAC address from the EEPROM. 
  byte mac[6] = {
    0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED
  };
//  EEPROM.get(0, mac);
  
  // Init the stuff for ethernet to work.
  Ethernet.init(10);  // The Ethernet v2 shield uses pin 10 here.
  
  // Serial for debugging.
  Serial.begin(9600);

  Serial.println("Getting IP address from DHCP....");

  // The following is ripped from the DhcpAddressPrinter example sketch:
  if (Ethernet.begin(mac) == 0) {
    Serial.println("Failed to configure Ethernet using DHCP");
    if (Ethernet.hardwareStatus() == EthernetNoHardware) {

      lcd.print("No Eth Shield");
      Serial.println("Ethernet shield was not found.  Sorry, can't run without hardware. :(");
      
      // Cannot progress if there is no ethernet hardware. 
      while (true) {
        delay(1);
      }
      
    } else if (Ethernet.linkStatus() == LinkOFF) {
      Serial.println("Ethernet cable is not connected.");

      lcd.print("No Eth Cable");

      // This may be an intermittent thing....
      while (Ethernet.linkStatus() == LinkOFF) {
        Serial.println("Attempting to detect Ethernet connection....");
        delay(1);
      }
    }
  }
  // Print out the IP address, and save it to a config file for use with
  // the Python module. 
  device_IP = Ethernet.localIP();

  // Start the server with the IP address.
  server.begin();
  Ethernet.begin(mac, device_IP);

  Serial.print("MAC is: ");
  for (int i = 0; i < sizeof(mac); i++){
    Serial.print(mac[i], HEX);
  }
  Serial.print('\n');
  Serial.print("Device IP address: ");
  Serial.println(device_IP);
   
  lcd.setCursor(0, 0);
  lcd.clear();
  lcd.print("READY");
  lcd.setCursor(0, 1);
  lcd.print(device_IP);
  
}


//////////////////////////////////////////////////////////////////////////////////
// THIS IS THE MAIN LOOP. 
//////////////////////////////////////////////////////////////////////////////////
void loop()
{
  // Process incoming requests
  check_for_client();

  // Read buttons to see if commands came from there.
  check_buttons();
  
  // Switch the power for the burn-in board.
  power_cycle_board();

  // Check if the process is done.
  check_if_done();
  
}


// Check the inputs from the buttons. They will change the state.
void check_buttons()
{
  uint8_t buttons = lcd.readButtons();

  if (buttons){

    unsigned long t = millis();
    while (millis() - t < 50);
    
    // Left button is START
    if (buttons & BUTTON_LEFT){

      // Basically, call the RUN command.
      if (state_machine.state == STANDBY){
        command_parser("RUN\r");
      }
    }

    // Right button is STOP
    if (buttons & BUTTON_RIGHT){

      // Basically, call the STP command.
      command_parser("STP\r");
    }
  }
}


// Check for some message from the host.
void check_for_client()
{
  EthernetClient client = server.available();
  char command[40] = "";     // Arduino String Library is evil....
  char temp[2];
  temp[1] = '\0';
  
  // If a connection is detected....
  if (client){
    Serial.println("New Client Connected.");

    // ....check for input.
    while (client.connected()){
      if (client.available()){
        char c = client.read();

        // Build the command string. '\r' will be used to define the end of a command.
        if (c != '\r'){
          temp[0] = c;
          strcat(command, temp);
        }
        // Got '\r', so parse the whole command.
        else {
          Serial.println(command);
          command_parser(command);
          command[0] = '\0';
          return;
        }
      }
    }
  }
}


// Parse the message from the host and call / do the appropriate routine.
void command_parser(char* command)
{
  // Commands look like this:
  // "CMD:value", where CMD is a 3 letter command and value is some number as a parameter.
  // To parse this, first check if the 3 letter command is something useful.
  // Then, grab the parameters (if any) and store them, or do the requested routine. 
  
  // Set Cycle Period
  if (is_command(command, "SCP")){
    int temp;
    sscanf(&command[4], "%d", &temp);
    device_parameters.cycle_period = temp;
    Serial.print("Set cycle period to: ");
    Serial.println(temp);
    server.print("SCP:");
    server.print(temp);
    server.print("\r");
    Serial.println("Done Sending to client");
  }

  // Set Start Delay
  else if (is_command(command, "SSD")){
    int temp;
    sscanf(&command[4], "%d", &temp);
    device_parameters.start_delay = temp;
    Serial.print("Set total time to: ");
    Serial.println(temp);
    server.print("SSD:");
    server.print(temp);
    server.print("\r");
    Serial.println("Done Sending to client");
  }

  // Set Duty Cycle
  else if (is_command(command, "SDC")){
    int temp;
    sscanf(&command[4], "%d", &temp);
    device_parameters.duty_cycle = temp;
    Serial.print("Set duty cycle to: ");
    Serial.println(temp);
    server.print("SDC:");
    server.print(temp);
    server.print("\r");
    Serial.println("Done Sending to client");
  }

  // Set Number of Cycles
  else if (is_command(command, "SNC")){
    int temp;
    sscanf(&command[4], "%d", &temp);
    device_parameters.num_cycles = temp;
    Serial.print("Set number of cycles to: ");
    Serial.println(temp);
    server.print("SNC:");
    server.print(temp);
    server.print("\r");
    Serial.println("Done Sending to client");
  }

  // Set End State
  else if (is_command(command, "SES")){
    int temp;
    sscanf(&command[4], "%d", &temp);
    device_parameters.end_state = temp;
    Serial.print("Set end state to: ");
    Serial.println(temp);
    server.print("SES:");
    server.print(temp);
    server.print("\r");
    Serial.println("Done Sending to client");
  }

  // Get Current State
  else if (is_command(command, "GCS")){

    // Print out the contents of device_parameters....
    Serial.print("Start Delay: ");
    Serial.println(device_parameters.start_delay);
    Serial.print("Cycle Period: ");
    Serial.println(device_parameters.cycle_period);
    Serial.print("Number of Cycles: ");
    Serial.println(device_parameters.num_cycles);
    Serial.print("Duty Cycle: ");
    Serial.println(device_parameters.duty_cycle);
    Serial.print("End State: ");
    Serial.println(device_parameters.end_state);
    Serial.print("Current Cycle is: ");
    Serial.println(device_parameters.current_cycle);
    Serial.print("Current Power State is: ");
    if (device_parameters.current_power_state){
      Serial.println("ON");
    }
    else {
      Serial.println("OFF");
    }
  }

  // Run power cycle process with current parameters. 
  else if (is_command(command, "RUN")){
    
    if (check_if_ready()){
      state_machine.state = READY;
    }
    else {
      return;
    }
    Serial.println(state_machine.state);
    // Attempt to start the process.
    if (start_process()){
      server.print("RUN\r");
    }
    else {
      server.print("ERR:CANNOT RUN. Process is either running or power is being held on.\r");
    }
  }

  // Stop everything and set to init state if Stop is requested.
  else if (is_command(command, "STP")){
    server.print("STP\r");
    stop_and_reset();
  }
}


// Check if parameters are set in a way that we can run the process.
bool check_if_ready()
{
  // Only worth checking if we are not running or holding power on.
  if (state_machine.state == STANDBY){

    // Certain values cannot be zero, if we are cycling.
    if (device_parameters.num_cycles > 0){

      // Check for period and duty cycle values. None can be zero.
      if (device_parameters.cycle_period == 0){
        server.print("ERR:Cycle Period cannot be Zero\r");
        lcd.setCursor(0, 0);
        lcd.clear();
        lcd.print("BAD PERIOD");
        return false;
      }
      if (device_parameters.duty_cycle == 0){
        server.print("ERR:Duty Cycle cannot be Zero\r");
        lcd.setCursor(0, 0);
        lcd.clear();
        lcd.print("BAD DUTY CYCLE");
        return false;
      }
      if (device_parameters.duty_cycle >= 100){
        server.print("ERR:Duty Cycle cannot be 100+\r");
        lcd.setCursor(0, 0);
        lcd.clear();
        lcd.print("BAD DUTY CYCLE");
        return false;
      }
    }
    return true;
  }

  // We basically do nothing if we are not in STANDBY.
  else {
    server.print("ERR:NOT READY. Process is either running or power is being held on.\r");
    lcd.setCursor(0, 0);
    lcd.clear();
    lcd.print("NOT READY OR BUSY");
    return false;
  }
}


// Stop and reset the burn in process. Reset means back to init (board power off) state.
void stop_and_reset()
{
  SET_POWER(0);
  state_machine.state = STANDBY;
  lcd.setCursor(0, 0);
  lcd.clear();
  lcd.print("STANDBY");
}


// Start the power cycle process. 
bool start_process()
{
  // Check if ready to run.
  if (state_machine.state == READY){

    // If so, start up the process using the device parameters....

    // Derive the on_time and off_time from duty_cycle.
    // Values are stored in milliseconds. They are passed in as seconds, so convert. 
    state_machine.on_time = device_parameters.cycle_period*1000*device_parameters.duty_cycle/100;
    state_machine.off_time = device_parameters.cycle_period*1000 - state_machine.on_time;
    
    // Set the state to be RUNNING.
    state_machine.state = RUNNING;

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("RUNNING");

    // First power state is always board ON. 
    SET_POWER(1);

    // Next state switch will happen at start_delay + on_time....half way into the 1st cycle.
    // Time is based on millis(), which returns the current "board time" in milliseconds.
    state_machine.timer_duration = device_parameters.start_delay*1000 + state_machine.on_time;
    state_machine.start_time = millis();

    // Init device parameters that reflect the power state of the board and the cycle count. 
    // It is 1 since the next time we change any state, we are in the middle of the 1st cycle.
    device_parameters.current_cycle = 1;    

    lcd.setCursor(0, 1);
    lcd.print("Cycle ");
    lcd.setCursor(6, 1);
    lcd.print(device_parameters.current_cycle);
    
    return true;
  }

  // If we are not ready to run, do nothing. 
  else {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("NOT READY");
    return false;
  }
}


// Check if we are done. If so, update the state machine.
// DONE vs STANDBY relates to whether or not the boards are powered. 
void check_if_done()
{
  if (state_machine.state == DONE){

    // Check for board power state. This determines whether or not DONE or STANDBY is appropriate.
    if (device_parameters.current_power_state == 0){

      // Boards are off, state can be STANDBY.
      state_machine.state = STANDBY;
    }
  }
}


// Do the power cyclie process....
//
// ASCII ART....
// 
// One "cycle" is as follows
// 
// 1 - - - - - - - \
//                  \
//                   \
//                    \
// 0                   \ - - - - - - -  
//
// Start of cycle is board power = on (output pin set to LOW since the transistor is ACTIVE LOW).
// The length of the on-state and off-state of one cycle is dependent on the parameters set from
// software.             
void power_cycle_board()
{
  // If power cycle is running, update the system if a state change is needed. 
  // Also, check if the number of cycles that happened is the number requested. 
  if (state_machine.state == RUNNING){

    // Only change power state based on timer.
    // Check if ready to toggle. This is true when the elapsed time is equal to timer_duration. 
    // Checking for the difference from start time them helps deal with the overflow of millis() that
    // happens about every 49 days and 17 hours. Using >= in case we are a bit late on checking.
    if (millis() - state_machine.start_time >= state_machine.timer_duration){
    
      // Check if we have completed all cycles. 
      if (device_parameters.current_cycle == device_parameters.num_cycles){
  
        // Set the power to the end_state
        SET_POWER(device_parameters.end_state);
  
        // Set state to DONE
        state_machine.state = DONE;
      }
    
      // We are not done, so go and change the power state.
      else {
  
        // Set the timer approprately....
        if (device_parameters.current_power_state){
          
          // Previous power state was board ON, now it should be OFF.
          SET_POWER(0);
  
          // Set the timer for how long the board should be held off.
          state_machine.timer_duration = state_machine.off_time;
          state_machine.start_time = millis();
        }
        else {
  
          // Previous power state was board OFF, now it should be ON.
          SET_POWER(1);
  
          // Set the timer for how long the board should be held on.
          state_machine.timer_duration = state_machine.on_time;
          state_machine.start_time = millis();
  
          // Increment the cycle count state. Turning the board power on means that we are at the start 
          // of a new cycle.
          device_parameters.current_cycle++;
//          lcd.clear();
//          lcd.setCursor(0, 1);
//          lcd.print("Cycle ");
          lcd.setCursor(6, 1);
          lcd.print(device_parameters.current_cycle);
        }
      }
    }
  }
}
