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


# QLineEdit where only positive integers work. Anything else is set to 0.
class Int_QLineEdit(QLineEdit):

	def __init__(self, parent=None):
		super(Int_QLineEdit, self).__init__(parent=parent)

	# Return the integer it holds, 0 if not an integer. 
	def to_int(self):
		if self.text() == None or self.text() == '':
			return 0
		
		elif not self.text().isnumeric():
			return 0

		else:
			return int(self.text())

# Widget that makes a set of Int_QLineEdits to represent hours:minutes:seconds.
class Time_Split_Entry(QWidget):
	
	def __init__(self, parent=None):
		super(Time_Split_Entry, self).__init__(parent=parent)

		self.grid = QGridLayout()
		self.setLayout(self.grid)

		# Using the Int_QLineEdit class since it has a method that returns 
		# either the integer value or 0 if not an integer. 
		self.hours = Int_QLineEdit()
		self.hours.setObjectName('hours')
		self.minutes = Int_QLineEdit()
		self.minutes.setObjectName('minutes')
		self.seconds = Int_QLineEdit()
		self.seconds.setObjectName('seconds')

		self.separator1 = QLabel(':')
		self.separator2 = QLabel(':')
		self.description = QLabel('Format as  Hours  :  Minutes  :  Seconds')
		self.grid.addWidget(self.hours, 0, 0)
		self.grid.addWidget(self.separator1, 0, 1)
		self.grid.addWidget(self.minutes, 0, 2)
		self.grid.addWidget(self.separator2, 0, 3)
		self.grid.addWidget(self.seconds, 0, 4)
		self.grid.addWidget(self.description, 0, 5)

	# Returns time entered in seconds.
	def get_time(self):

		hours = self.hours.to_int()
		
		minutes = self.minutes.to_int()
		
		seconds = self.seconds.to_int()

		return hours*60*60 + minutes*60 + seconds


################################################################################

#-- D E V I C E   S E L E C T -------------------------------------------------#

################################################################################
# 	Widget that shows options for what devices have been saved and allows 
#   connections to be made / broken. 
#
################################################################################
class Device_Config(QWidget):

	def __init__(self):
		super(Device_Config, self).__init__()

		self.grid = QGridLayout()
		self.setLayout(self.grid)

		# Form for entering parameters.
		# parameters = ['Power Cycle Start Delay', 'Duty Cycle', 'Power Cycle Duration', 'End State']
		# for param in parameters:
		# 	new_param = QLineEdit()
		# 	new_param.setObjectName(param)
		# 	self.grid.addWidget(new_param)

		# Using the Int_QLineEdit class since it has a method that returns 
		# either the integer value or 0 if not an integer. 
		self.number_of_cycles = Int_QLineEdit()
		self.number_of_cycles.setObjectName('number_of_cycles')
		self.number_of_cycles_label = QLabel('Number of Cycles')
		self.grid.addWidget(self.number_of_cycles_label, 0, 0)
		self.grid.addWidget(self.number_of_cycles, 0, 1)


		self.cycle_start_delay = Time_Split_Entry(self)
		self.cycle_start_delay.setObjectName('cycle_start_delay')
		self.start_delay_label = QLabel('Power Cycle Start Delay')
		self.grid.addWidget(self.start_delay_label, 1, 0)
		self.grid.addWidget(self.cycle_start_delay, 1, 1)

		self.cycle_period = Time_Split_Entry(self)
		self.cycle_period.setObjectName('cycle_period')
		self.cycle_period_label = QLabel('Cycle Period')
		self.grid.addWidget(self.cycle_period_label, 2, 0)
		self.grid.addWidget(self.cycle_period, 2, 1)

		# Using the Int_QLineEdit class since it has a method that returns 
		# either the integer value or 0 if not an integer. 
		self.duty_cycle = Int_QLineEdit()
		self.duty_cycle.setObjectName('duty_cycle')
		self.duty_cycle_label = QLabel('Duty Cycle')
		self.grid.addWidget(self.duty_cycle_label, 3, 0)
		self.grid.addWidget(self.duty_cycle, 3, 1)

		self.end_state = QGroupBox()
		hbox = QHBoxLayout()
		self.end_state.setLayout(hbox)
		hbox.addWidget(QRadioButton("ON", self.end_state))
		hbox.addWidget(QRadioButton("OFF", self.end_state))
		self.end_state.setObjectName('end_state')
		self.end_state_label = QLabel('End State')
		self.grid.addWidget(self.end_state_label, 4, 0)
		self.grid.addWidget(self.end_state, 4, 1)


	def get_end_state(self):

		for radio in self.end_state.findChildren(QRadioButton):
			if radio.isChecked():
				if radio.text() == 'ON':
					return 1

		# Default state is going to be off.
		return 0