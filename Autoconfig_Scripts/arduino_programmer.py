# simple program to compile and upload Arduino code using the Arduino command line

import subprocess
import sys
import os
import time

import serial
import serial.tools.list_ports

# TODO:
'''
Change so that it creates a unique MAC address and uses that to program the 
Arduino. Need to store that MAC in the EEPROM of the Arduino. 

So....two programs need to be made: one creates a MAC address and stores it, and
the main program, which will read it from memory.
Modify the .h file included in the MAC_address_programmer.ino to have different 
addresses and then program the arduino. 
'''

# Path to arduino executable.
print("Running")
sys.stdout.flush()
arduino_prog = os.path.join('"C:/Program Files (x86)/Arduino/arduino_debug.exe"')

init_file = sys.argv[1]
project_file = sys.argv[2]

code_file = open(init_file, 'r')

# project_ino_path = os.path.abspath(project_file)
# init_ino_path = os.path.abspath(init_file)
# start_line = code_file.readline()[3:].strip()
# action_line = code_file.readline()[3:].strip()
# board_line = code_file.readline()[3:].strip()
# port_line = code_file.readline()[3:].strip()
# end_line = code_file.readline()[3:].strip()
# code_file.close()

# if (start_line != "python-build-start" or end_line != "python-build-end"):
# 	print("Sorry, can't process file")
# 	sys.exit()

project_ino_path = os.path.abspath(project_file)
init_ino_path = os.path.abspath(init_file)
action_line = 'upload'
board_line = 'arduino:avr:uno' # 'arduino:megaavr:uno2018'
port_line = ''

ports = serial.tools.list_ports.comports()

found = False
for port, desc, hwid in sorted(ports):
	if 'Arduino' in desc:
		found = True
		port_line = str(port)
		break

if not found:
	print("No arduino detected. Device must be an Arduino Uno.")
	sys.exit()


init_command = arduino_prog + " --" + action_line + " --board " + board_line + " --port " + port_line + " " + init_file
arduino_command = arduino_prog + " --" + action_line + " --board " + board_line + " --port " + port_line + " " + project_file

# print('\nRUNNNING PROGRAM TO SAVE MAC ADDRESS ONTO THE BOARD\n')

# print("Running the following Arduino Command: ")
# print(init_command)

# print("\n-- Starting %s --\n" %(action_line))

# sys.stdout.flush()

# presult = subprocess.run(init_command)
# # presult = subprocess.Popen(arduino_command)
# # for line in iter(presult.stdout.readline, b''):
# # 	print(line)
# # if presult != 0:
# # 	print("\n Failed - result code = %s --" %(presult))
# # else:
# # 	print("\n-- Success --")

# print(presult)

# serial_port = serial.Serial(port_line)
# serial_port.baudrate = 9600
# print("CONNECTED TO BOARD")

# # Verify the MAC address was written.
# while True:
# 	s = serial_port.readline().decode()
# 	print(s)
# 	if "Done" in s:
# 		break

# sys.stdout.flush()
# serial_port.close()

# print('\nDONE SAVING MAC ADDRESS ON BOARD\n')
print('PROGRAMMING THE BOARD WITH MAIN CODE\n')

print("Running the following Arduino Command: ")
print(arduino_command)

print("\n-- Starting %s --\n" %(action_line))

sys.stdout.flush()

presult = subprocess.run(arduino_command)

print(presult)

serial_port = serial.Serial(port_line)
serial_port.baudrate = 9600
print("CONNECTED TO BOARD")

# Get the IP address and save it.
while True:
	s = serial_port.readline().decode()
	print(s)
	if "Device IP address" in s:
		ip_address = s.split(':')[1].strip()
		print("GOT IP OF || %s ||" % ip_address)
		break