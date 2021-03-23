# Power_Cycle_Controller

Qt (PySide6) based application used to interract with an Arduino Uno that serves as a power cycling controller. The implication is that Pin 8 on the Arduino controls a relay or power transistor (PMOS) that sits on the DC power of the system-to-be-controlled. Parameters for power cycling, such as intitial hold time, end state, number of cycles, cycle period, and duty cycle are all configurable. 

To ensure you have the needed modules, use the requirements.txt file with your python environment. 


## TO-DO

- Run-time information should be printed to the text box widget.
- Add button / command for getting current state. 
