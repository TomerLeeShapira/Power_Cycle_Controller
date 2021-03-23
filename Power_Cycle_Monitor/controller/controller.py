import sys
import os
import socket


ascii_header = '\n<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>\n'

sock = None
HOST = '172.28.208.17'
PORT = 80


##########################COMMANDS###########################
# Set Cycle Period			SCP
# Set Start Delay 			SSD
# Set Duty Cycle 			SDC
# Set Number of Cycles  	SNC
# Set End State  			SES
# Get Current State			GCS
# Run						RUN
# Stop						STP


################################################################################

#-- D E V I C E   C O N N E C T I O N -----------------------------------------#

################################################################################
# 	Class that represents a connection to a device. 
#
################################################################################
class Controller_Connection(object):
	
	############################################################################
	#-- I N I T ---------------------------------------------------------------#
	############################################################################
	# 	Constructor. Creates the socket object and inits the connection to 'not
	#   connected'.      
	# 
	#   INPUTS:
	#   None
	#   
	############################################################################
	def __init__(self):
		self._sock = None
		self._is_connected = False
		self._device = None


	############################################################################
	#-- I S   C O N N E C T E D -----------------------------------------------#
	############################################################################
	#   Returns the connection status
	# 
	#   INPUTS:
	#   None	 	
	#   
	############################################################################
	def is_connected(self):
		return self._is_connected


	############################################################################
	#-- D I S C O N N E C T   C O N T R O L L E R -----------------------------#
	############################################################################
	#   Closes the connected socket, if possible. 
	# 
	#   INPUTS:
	#   None	 	
	#   
	############################################################################
	def disconnect_controller(self):
		
		try:
			self._sock.close()
			self._is_connected = False
			print("disconnected")
		except:
			pass


	############################################################################
	#-- C O N N E C T   C O N T R O L L E R -----------------------------------#
	############################################################################
	#   Connects to the given host over the given port. 
	# 
	#   INPUTS:
	#   host:			IP address string
	#   port:			port for connection
	#   
	############################################################################
	def connect_controller(self, host, port):
		self._device = (host, port)
		self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self._sock.connect(self._device)
			self._is_connected = True
			print("connected")
		except Exception as err:
			print(str(err))


	############################################################################
	#-- S E N D   T O   C O N T R O L L E R -----------------------------------#
	############################################################################
	#   Sends a message to the controller. Returns the response. 
	# 
	#   INPUTS:
	#   message:		String to be sent. 	 	
	#   
	############################################################################
	def send_to_controller(self, message):

		# Init return variable. Will stay empty if comms fails. 
		resp = ''
		
		# Attempt to send the message. 
		try:
			self._sock.sendall(message.encode())

			# Read responses until \r (terminating char) is received. 
			while '\r' not in resp:
				resp += str(self._sock.recv(1024), 'ascii')
			print(resp)
		
		# Print out errors for now. Details TBD
		except Exception as err:
			print(str(err))

		return resp
	

	############################################################################
	#-- S E T   C Y C L E   P E R I O D ---------------------------------------#
	############################################################################
	#   Tells to device to set its cycle period to the given value.
	# 
	#   INPUTS:
	#   value:			cycle period to be set. a cycle is one round of on-off.	 	
	#   
	############################################################################
	def set_cycle_period(self, value):
		
		if self._is_connected:
			message = 'SCP:%d\r' % value
			self.send_to_controller(message)
			
		else:
			pass


	############################################################################
	#-- S E T   S T A R T   D E L A Y -----------------------------------------#
	############################################################################
	#   Tells to device to set its start delay time to the given value.
	# 
	#   INPUTS:
	#   value:			total delay time in seconds 	 	
	#   
	############################################################################
	def set_start_delay(self, value):

		if self._is_connected:
			message = 'SSD:%d\r' % value
			self.send_to_controller(message)

		else:
			pass


	############################################################################
	#-- S E T   D U T Y   C Y C L E -------------------------------------------#
	############################################################################
	#   Tells to device to set its duty cycle to the given value.
	# 
	#   INPUTS:
	#   value:			duty cycle in percent 	 	
	#   
	############################################################################
	def set_duty_cycle(self, value):

		if self._is_connected:
			message = 'SDC:%d\r' % value
			self.send_to_controller(message)
		
		else:
			pass


	############################################################################
	#-- S E T   N U M B E R   O F   C Y C L E S -------------------------------#
	############################################################################
	#   Tells to device to set its number of cycles to the given value.
	# 
	#   INPUTS:
	#   value:			number of cycles	
	#   
	############################################################################
	def set_number_of_cycles(self, value):

		if self._is_connected:
			message = 'SNC:%d\r' % value
			self.send_to_controller(message)
		
		else:
			pass


	############################################################################
	#-- S E T   E N D   S T A T E ---------------------------------------------#
	############################################################################
	#   Tells to device to set its end state to the given state.
	# 
	#   INPUTS:
	#   state:			state for the power cycle to end on. 0 is off. 1+ is on.	
	#   
	############################################################################
	def set_end_state(self, state):

		if self._is_connected:
			message = 'SES:%d\r' % state
			self.send_to_controller(message)

		else:
			pass


	############################################################################
	#-- S T A R T   P R O C E S S ---------------------------------------------#
	############################################################################
	#   Tells to device to start running its power cycle process.
	# 
	#   INPUTS:
	#   None			
	#   
	############################################################################
	def start_process(self):

		if self._is_connected:
			message = 'RUN\r'
			self.send_to_controller(message)

		else:
			pass


	############################################################################
	#-- S T O P   P R O C E S S -----------------------------------------------#
	############################################################################
	#   Tells to device to stop running and return to the STANDBY state. 
	# 
	#   INPUTS:
	#   None	
	#   
	############################################################################
	def stop_process(self):

		if self._is_connected:
			message = 'STP\r'
			self.send_to_controller(message)

		else:
			pass


if __name__ == '__main__':
	print(ascii_header)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print("Enter IP")
	HOST = input()
	print('Connecting to Server....')
	server = (HOST, PORT)
	try:
		sock.connect(server)
	except Exception as err:
		print(str(err))
