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

#-- A D D   D E V I C E -------------------------------------------------------#

################################################################################
# 	Dialog that guides through the device scan and add functions.
#
################################################################################
class Add_Device(QDialog):

	def __init__(self, parent=None):
		super(Add_Device, self).__init__(parent=parent)

		self.grid = QGridLayout()
		self.setLayout(self.grid)

		self.prompt = QLabel('Connect Device to Computer and Click Add Device.')
		self.grid.addWidget(self.prompt, 0, 0, 1, -1, Qt.AlignCenter)

		self.device_name_label = QLabel('Enter Device\nName:')
		self.grid.addWidget(self.device_name_label, 1, 0)
		self.device_name = QLineEdit()
		self.grid.addWidget(self.device_name, 1, 1, 1, -1)

		self.button_box = QDialogButtonBox()
		self.button_box.setObjectName('button_box')
		self.button_box.addButton('Add Device', QDialogButtonBox.AcceptRole)
		self.button_box.addButton('Cancel', QDialogButtonBox.RejectRole)
		self.button_box.accepted.connect(self.accept)
		self.button_box.rejected.connect(self.reject)

		self.grid.addWidget(self.button_box, 2, 0, 1, -1)

		# self.grid.setColumnStretch(1, 40)

