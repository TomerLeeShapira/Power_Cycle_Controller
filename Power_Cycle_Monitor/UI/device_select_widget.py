import sys
import os
# import PyQt5
# from PyQt5.QtCore import *
# from PyQt5.QtGui import *
# from PyQt5.QtWidgets import *

import PySide6
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

################################################################################

#-- D E V I C E   S E L E C T -------------------------------------------------#

################################################################################
# 	Widget that shows options for what devices have been saved and allows 
#   connections to be made / broken. 
#
################################################################################
class Device_Select(QWidget):

	def __init__(self):
		super(Device_Select, self).__init__()

		self.grid = QGridLayout()
		self.setLayout(self.grid)

		self.title = QLabel()
		self.title.setText("Select Power Controller")
		self.grid.addWidget(self.title, 0, 0)

		# Device drop down menu. Items are added later. 
		self.device_dropdown = QComboBox()
		# self.device.addItem("TEST1")
		# self.device.addItem("TEST2")
		self.grid.addWidget(self.device_dropdown, 1, 0, 1, 2)

		# Buttons for connecting and disconnecting.
		self.connect_button = QPushButton("Connect")
		self.connect_button.setObjectName("connect_button")
		self.disconnect_button = QPushButton("Disconnect")
		self.disconnect_button.setObjectName("disconnect_button")
		self.grid.addWidget(self.connect_button, 2, 0)
		self.grid.addWidget(self.disconnect_button, 3, 0)

		# Buttons for setting parameters and starting / stopping
		self.start_button = QPushButton("Start Power Cycle")
		self.start_button.setObjectName("start_button")
		self.stop_button = QPushButton("Stop Power Cycle")
		self.stop_button.setObjectName("stop_button")
		self.config_button = QPushButton("Set Parameters")
		self.config_button.setObjectName("config_button")
		self.add_devices_button = QPushButton("Add Device")
		self.add_devices_button.setObjectName("add_devices_button")
		self.grid.addWidget(self.start_button, 2, 3)
		self.grid.addWidget(self.stop_button, 3, 3)
		self.grid.addWidget(self.config_button, 1, 3)
		self.grid.addWidget(self.add_devices_button, 0, 3)

		self.status_console = QTextEdit()
		self.status_console.setObjectName("status_console")
		self.grid.addWidget(self.status_console, 0, 2, 4, 1)


