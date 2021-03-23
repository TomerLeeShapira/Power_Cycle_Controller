import sys
import os
# import PyQt5
import PySide6
import subprocess
import configparser as cp
# from PyQt5.QtCore import *
# from PyQt5.QtGui import *
# from PyQt5.QtWidgets import *

from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from UI import UI, Add_Device
# from ./UI/device_select_widget import Device_Select
# from ./UI/device_config_widget import Device_Config
# from add_device_dialog import Add_Device
# from arduino_programmer_wrapper import Programmer_Thread
from controller import Controller_Connection

cwd = os.getcwd()
programmer_path = os.path.join('C:/Users/tomer/Documents/Oven_Power_Cycling/Autoconfig_Scripts/')
DEVICE_LIST_FILE = 'device_list.ini'


################################################################################

#-- C O N T R O L L E R   T H R E A D -----------------------------------------#

################################################################################
# 	Wraps around the controller module to make it work with signals/slots. This
#   is moved to a QThread spawned by the main class. There should be a cleaner 
#   way to do the wrapping....
#
################################################################################
'''
	TODO:
	Remove redundant checks for connection.
'''
class Device_Process(QObject, Controller_Connection):

	finished = Signal()
	connection_status_signal = Signal(bool)

	def __init__(self):
		super().__init__()

	
	############################################################################
	#-- S E T   P A R A M E T E R S -------------------------------------------#
	############################################################################
	# 	Slot that passes the given parameters to the controller. Serves as a Qt
	#   interface to the controller class functions. 
	# 
	#   INPUTS:
	#   params:  		dict of parameters sent by the GUI thread. 
	#   
	############################################################################
	@Slot(dict)
	def set_parameters(self, params):

		# Extract from the parameters dict. It has an pre-set set of keys. 
		start_delay = params['start_delay']
		cycle_period = params['cycle_period']
		duty_cycle = params['duty_cycle']
		num_cycles = params['num_cycles']
		end_state = params['end_state']

		print(params)

		self.set_cycle_period(cycle_period)
		self.set_start_delay(start_delay)
		self.set_duty_cycle(duty_cycle)
		self.set_number_of_cycles(num_cycles)
		self.set_end_state(end_state)


	############################################################################
	#-- C O N N E C T   T O   D E V I C E -------------------------------------#
	############################################################################
	# 	Slot that uses the given host / port info passed in to connect to a
	#   controller. 
	# 
	#   INPUTS:
	#   conn:			tuple of host IP and port, which is passed to the 
	#                   controller module to make a socket connection. 
	#   
	############################################################################
	@Slot(tuple)
	def connect_to_device(self, conn):
		host = conn[0]
		port = conn[1]
		self.connect_controller(host, port)
		self.connection_status_signal.emit(self.is_connected())


	############################################################################
	#-- D I S C O N N E C T   F R O M   D E V I C E ---------------------------#
	############################################################################
	# 	Slot used to disconnect from the controller. 
	# 
	#   INPUTS:
	#   None
	#   
	############################################################################
	@Slot()
	def disconnect_from_device(self):

		if self.is_connected():
			self.disconnect_controller()

		self.connection_status_signal.emit(self.is_connected())


	############################################################################
	#-- S T A R T   P O W E R   C Y C L E -------------------------------------#
	############################################################################
	# 	Slot used to tell the controller to start running the power cycle 
	#   process. 
	# 
	#   INPUTS:
	#   None
	#   
	############################################################################
	@Slot()
	def start_power_cycle(self):

		if self.is_connected():
			self.start_process()


	############################################################################
	#-- S T O P   P O W E R   C Y C L E ---------------------------------------#
	############################################################################
	# 	Slot used to tell the controller to stop running the power cycle 
	#   process. 
	# 
	#   INPUTS:
	#   None
	#   
	############################################################################
	@Slot()
	def stop_power_cycle(self):

		if self.is_connected():
			self.stop_process()


	############################################################################
	#-- E N D   P R O C E S S -------------------------------------------------#
	############################################################################
	# 	Main threaded process. Basically, spins in place unless told to stop. 
	# 
	#   INPUTS:
	#   None
	#   
	############################################################################
	# This may be redundant?
	@Slot()
	def end_process(self):

		self.finished.emit()

################################################################################

#-- P O W E R   C Y C L E   M O N I T O R -------------------------------------#

################################################################################
# 	Main class for this whole application. Creates an instance of the UI and
#   links up the subprocesses and worker threads. Also connects buttons to 
#   appropriate custom functions. 
#
################################################################################
class Power_Cycle_Monitor(QObject):


	set_params = Signal(dict)
	make_connection = Signal(tuple)
	break_connection = Signal()
	start = Signal()
	stop = Signal()

	def __init__(self):

		super().__init__()

		# Init main GUI. 
		self.gui = UI()

		# Init popup windows for processes. 
		self.output_window = QDialog(self.gui)
		self.output_window.console = QTextEdit(self.output_window)
		self.output_window.setGeometry(100, 100, 400, 200)
		self.output_window.console.setGeometry(0, 0, 400, 200)

		# Connect buttons to functions.
		self.gui.device_select.add_devices_button.clicked.connect(self.run_add_device)
		self.gui.device_select.connect_button.clicked.connect(self.connect_to_device)
		self.gui.device_select.disconnect_button.clicked.connect(self.disconnect_from_device)
		self.gui.device_select.config_button.clicked.connect(self.set_parameters)
		self.gui.device_select.start_button.clicked.connect(self.start_power_cycle)
		self.gui.device_select.stop_button.clicked.connect(self.stop_power_cycle)

		# Init subprocesses and worker threads. 
		self.programmer_process = None
		self.ui_thread = QThread.currentThread()
		# self.device_connection = ctrl.Device_Connection()
		self.device_connection = Device_Process()
		self.conn_status = False

		# Thread is always running. The threaded process is a client to the 
		# connected device. 
		self.thread = QThread()

		# Graceful QThread termination....
		app.aboutToQuit.connect(self.thread.quit)

		# self.device_connection.connect_controller(host, port)

		# Thread signals to GUI slots.
		self.device_connection.moveToThread(self.thread)
		self.device_connection.finished.connect(self.thread.quit)
		self.device_connection.connection_status_signal.connect(self.connection_status)

		# GUI signals to Thread Slots
		self.make_connection.connect(self.device_connection.connect_to_device)
		self.break_connection.connect(self.device_connection.disconnect_from_device)
		self.set_params.connect(self.device_connection.set_parameters)
		self.start.connect(self.device_connection.start_power_cycle)
		self.stop.connect(self.device_connection.stop_power_cycle)

		self.thread.start()

		# Init device list.
		self.load_device_list()

		# Show the GUI
		self.gui.show()
	



	# Emitted by thread when connection state has changed. 
	# @pyqtSlot(bool)
	def connection_status(self, conn):
		print("Connection state is %s" % conn)
		self.conn_status = conn

	############################################################################
	#-- L O A D   D E V I C E   L I S T ---------------------------------------#
	############################################################################
	# 	Loads the device_list config file. This list is what stores what devices
	#   are available to connect. They are ID'd by names, which correspond to IP
	#   addresses. 
	# 
	#   INPUTS:
	#   None
	#   
	############################################################################
	def load_device_list(self):
		
		config = cp.ConfigParser()
		config.read(DEVICE_LIST_FILE)
		new_dict = {s:dict(config.items(s)) for s in config.sections()}
		print(new_dict)

		self.gui.update_device_dict(new_dict)


	############################################################################
	#-- R U N   A D D   D E V I C E -------------------------------------------#
	############################################################################
	# 	Launches the thread to connect to and program a new power cycle 
	#   controller.   
	# 
	#   INPUTS:
	#   None
	#   
	############################################################################
	def run_add_device(self):

		dialog = Add_Device(self.gui)
		action = dialog.exec_()
		
		# Check to see if the dialog was accepted. If it was not, simply return.
		if not action:
			dialog.close()
			return
		else:
			dialog.close()

			# Check the config file for current device names. Show a message if 
			# the name already exists.  	
			name = dialog.device_name.text()
			if name in self.gui.get_device_dict().keys():
				print("already exists")
				# Prompt that this will overwrite the current device with the 
				# same name. 
				warning = QMessageBox(self.gui)
				warning.setIcon(QMessageBox.Warning)
				warning.setText("WARNING: A Device with that name already exists.\nDo you wish to overwrite it?")
				warning.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
				action = warning.exec_()
				if not action:
					warning.close()
					return
				else:
					warning.close()

			# Launch the programming process....
			os.chdir(programmer_path)
			self.programmer_process = QProcess()
			self.programmer_process.readyReadStandardOutput.connect(self.programmer_output)
			self.programmer_process.readyReadStandardError.connect(self.programmer_output)
			self.programmer_process.finished.connect(self.programmer_done)
			self.output_window.console.clear()
			self.programmer_process.start('py', ['arduino_programmer.py', 
				'..\\Arduino_Code\\MAC_address_programmer\\MAC_address_programmer.ino',
				'..\\Arduino_Code\\Power_Cycle_Arduino\\Power_Cycle_Arduino.ino'])

			self.output_window.exec_()

			print("adding device")
			config = cp.ConfigParser()
			config.read(DEVICE_LIST_FILE)
			
			# Add new device to file. Overwrite existing device with the same name. 
			if not config.has_section(name):
				config.add_section(name)
			config.set(name, 'IP', self.new_IP)
			
			with open(DEVICE_LIST_FILE, 'w') as updated_file:
				config.write(updated_file)
			self.load_device_list()


	# Function used to update the programmer console widget with the output from the
	# programmer process (stdout is routed to here). Tied to 
	# readyReadStandardOutput slot.
	def programmer_output(self):

		message = self.programmer_process.readAllStandardOutput().data().decode()
		if '||' in message:
			self.new_IP = message.split('||')[1]
		cursor = self.output_window.console.textCursor()
		cursor.movePosition(QTextCursor.End)
		cursor.insertText(message)
		self.output_window.console.setTextCursor(cursor)
		self.output_window.console.ensureCursorVisible()

	# Function used by the programmer QProcess that is tied to finished. 
	def programmer_done(self):
		cursor = self.output_window.console.textCursor()
		cursor.movePosition(QTextCursor.End)
		cursor.insertText("Done Programming. You can close this window.")
		self.output_window.console.setTextCursor(cursor)
		self.output_window.console.ensureCursorVisible()
		self.programmer_process = None
		os.chdir(cwd)

	############################################################################
	#-- C O N N E C T   T O   D E V I C E -------------------------------------#
	############################################################################
	# 	Launches the thread to connect to the selected controller. 
	# 
	#   INPUTS:
	#   None
	#   
	############################################################################
	def connect_to_device(self):
		
		# Get the selected device and the associated IP address from the GUI
		# class. 
		selected = str(self.gui.get_current_device())
		dev_dict = self.gui.get_device_dict()

		host = dev_dict[selected]['ip']

		# All devices are hard-coded to port 80. 
		port = 80

		self.disconnect_from_device()			

		# self.device_connection.set_cycle_period(1234)
		self.make_connection.emit((host, port))


	############################################################################
	#-- D I S C O N N E C T   F R O M   D E V I C E ---------------------------#
	############################################################################
	# 	Disconnects from the currently connected controller. Kills any threads
	#   as well.  
	# 
	#   INPUTS:
	#   None
	#   
	############################################################################
	def disconnect_from_device(self):

		# Check if we need to even do anything.
		if self.conn_status:

			# Disconnect.
			self.break_connection.emit()


	############################################################################
	#-- S E T   P A R A M E T E R S -------------------------------------------#
	############################################################################
	# 	Launches the thread to connect to the selected controller. 
	# 
	#   INPUTS:
	#   None
	#   
	############################################################################
	def set_parameters(self):
		# proc = QProcess()
		# proc.start()

		# Get the parameters from the GUI.
		params = self.gui.get_device_config()

		self.set_params.emit(params)


	############################################################################
	#-- D I S C O N N E C T   F R O M   D E V I C E ---------------------------#
	############################################################################
	# 	Slot used to disconnect from the controller. 
	# 
	#   INPUTS:
	#   None
	#   
	############################################################################
	def start_power_cycle(self):

		self.start.emit()


	############################################################################
	#-- D I S C O N N E C T   F R O M   D E V I C E ---------------------------#
	############################################################################
	# 	Slot used to disconnect from the controller. 
	# 
	#   INPUTS:
	#   None
	#   
	############################################################################
	def stop_power_cycle(self):

		self.stop.emit()


if __name__ == "__main__":

	app  = QApplication(sys.argv)

	ui = Power_Cycle_Monitor()

	sys.exit(app.exec_())