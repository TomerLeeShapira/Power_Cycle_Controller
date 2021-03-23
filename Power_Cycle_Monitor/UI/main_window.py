import sys
import os
# import PyQt5
import PySide6
import subprocess
# from PyQt5.QtCore import *
# from PyQt5.QtGui import *
# from PyQt5.QtWidgets import *

from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from .device_select_widget import Device_Select
from .device_config_widget import Device_Config
# from add_device_dialog import Add_Device
# from arduino_programmer_wrapper import Programmer_Thread
# import controller as ctrl

# cwd = os.getcwd()
# programmer_path = os.path.join('C:/Users/Tomer.Shapira/OneDrive - Novanta/Documents/Oven_Power_Cycling/Autoconfig_Scripts/')
# DEVICE_LIST_FILE = 'device_list.ini'

MODULE_PATH = os.path.dirname(__file__)
FONT_PATH = os.path.join(MODULE_PATH, 'Fonts')
STYLESHEET_PATH = os.path.join(MODULE_PATH, 'stylesheet')
print(STYLESHEET_PATH)


################################################################################

#-- M A I N   W I N D O W -----------------------------------------------------#

################################################################################
# 	Class for the main UI of the burn in controller application. 
#
################################################################################
class UI(QMainWindow):

	def __init__(self):
		super(UI, self).__init__()

		screen = QGuiApplication.primaryScreen()
		available_height = int(QScreen.availableGeometry(screen).height())
		ui_max_height = int(self.geometry().height())
		ui_max_width = int(self.geometry().width())

		if (ui_max_height + 29) > available_height:
			self.scale = (available_height - 31) / (ui_max_height + 29)
		else:
			self.scale = 1
		
		self.scale_ui(self.scale)

		self.central_widget = QWidget(self)

		self.central_grid = QGridLayout()
		self.central_widget.setLayout(self.central_grid)

		self.setCentralWidget(self.central_widget)

		self.header = QLabel()
		self.header.setObjectName("header")
		# header2 = QLabel()
		# header.setGeometry(QRect(580*self.scale, 100*self.scale, 191*self.scale, 21*self.scale))
		self.header.setText("Power Cycle Monitor")
		# header2.setText("FOO")
		self.central_grid.addWidget(self.header, 0, 0)
		# self.grid.addWidget(header2, 1, 0)
		self.device_select = Device_Select()
		self.central_grid.addWidget(self.device_select, 1, 0)

		self.device_config = Device_Config()
		self.central_grid.addWidget(self.device_config, 2, 0)

		# self.central_grid.addWidget(device_select, 2, 0)

		# load custom fonts (celera motion company styles)
		QFontDatabase.addApplicationFont(os.path.realpath(os.path.join(FONT_PATH, "Whitney-Book-Bas.otf")))
		QFontDatabase.addApplicationFont(os.path.realpath(os.path.join(FONT_PATH, "Whitney-Light-Bas.otf")))
		QFontDatabase.addApplicationFont(os.path.realpath(os.path.join(FONT_PATH, "Whitney-Semibold-Bas.otf")))
		QFontDatabase.addApplicationFont(os.path.realpath(os.path.join(FONT_PATH, "Whitney-Medium-Bas.otf")))

		# Use the stylesheet to make it look nice. 
		file = open(os.path.realpath(os.path.join(STYLESHEET_PATH, "main_stylesheet.qss")), 'r')
		MAIN_STYLESHEET = file.read()
		file.close()
		self.setStyleSheet(MAIN_STYLESHEET)

		# self.ext_proc = Programmer_Thread()

		self._device_dict = None
		self._new_IP = ''

		# file = open(os.path.join("device_select_stylesheet.qss"), 'r')
		# DEVICE_SELECT_STYLESHEET = file.read()
		# file.close()
		# self.device_select.setStyleSheet(DEVICE_SELECT_STYLESHEET)

	
	def update_device_dict(self, devices):

		self._device_dict = devices
		self.device_select.device_dropdown.clear()
		for d in devices.keys():
			self.device_select.device_dropdown.addItem(d)


	def get_device_dict(self):
		return self._device_dict


	def get_current_device(self):
		return self.device_select.device_dropdown.currentText()


	# Builds a dict from the fields in self.device_config
	def get_device_config(self):

		params = dict()

		start_delay = self.device_config.cycle_start_delay.get_time()
		cycle_period = self.device_config.cycle_period.get_time()
		duty_cycle = self.device_config.duty_cycle.to_int()
		num_cycles = self.device_config.number_of_cycles.to_int()
		end_state = self.device_config.get_end_state()

		params['start_delay'] = start_delay
		params['cycle_period'] = cycle_period
		params['duty_cycle'] = duty_cycle
		params['num_cycles'] = num_cycles
		params['end_state'] = end_state

		return params


	############################################################################
	#-- S C A L E   U I -------------------------------------------------------#
	############################################################################
	# 	Adjusts the UI geometry to fit in any resolution below 1920x1200p     
	# 
	#   INPUTS:
	#   scale:	 		scale to use to adjust ui size
	#   
	############################################################################
	def scale_ui(self, scale):

		# self.setGeometry(0, 0, 1300*scale, (1100 + 29)*scale)
		self.setGeometry(0, 0, 400*scale, 300*scale)

		for attr, value in vars(self).items():
			try:
				rect = value.geometry()
				x = int(rect.x())
				y = int(rect.y())
				h = int(rect.height())
				w = int(rect.width())
				value.setGeometry(x*scale, y*scale, w*scale, h*scale)
				# print("%s: %d" % (attr, x))				
			except:
				pass


if __name__ == "__main__":
	app = QApplication(sys.argv)

	ui = UI()
	ui.show()

	sys.exit(app.exec_())