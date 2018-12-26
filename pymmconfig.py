#!/usr/bin/env python3
'''
run `pymmconfig` once at setup to initialize config settings
or run it again to change or add values
'''
import os
import sys
import inspect
import configparser

def make_config(configPath):
	if not os.path.isfile(configPath):
		print('theres no system config file yet... hang on...')
		# open(configPath,'x')
		with open(configPath,'w+') as config:
			config.write('''[paths]\noutdir_ingestsip:\naip_staging:\nresourcespace_deliver:\nprores_deliver:\
				\n\n[deriv delivery options]\nresourcespace: n\nproresHQ: n\
				\n\n[database settings]\nuse_db:\npymm_db:\npymm_db_access:\npymm_db_address:\
				\n\n[database users]\nuser: password\
				\n\n[logging]\npymm_log_dir:\
				\n\n[mediaconch format policies]\nfilm_scan_master:\nvideo_capture_master:\nmagnetic_video_mezzanine:\nfilm_scan_mezzanine:\nlow_res_proxy:\
				\n\n[ffmpeg]\nresourcespace_video_opts:["a","b","c"]\nproresHQ_opts:["a","b","c"]\nresourcespace_audio_opts:["a","b","c"]
				\n\n[bwf constants]\noriginator:\ncoding_history_ANALOG:\
				''')

def set_value(section, optionToSet,newValue=None):
	# Kieran - there are some references here to pymmFunctions.py. I added the 
	# functions that are referenced into this file, so you don't actually 
	# need it, but I left the old stuff here commented out for history.
	# You can delete it all!
	#
	# import pymmFunctions here to use get_system.... 
	# can't import it at top since it makes a circular dependency problem 
	# (i.e. if config.ini doesn't exist yet you can't use pymmFunctions)
	# https://stackoverflow.com/questions/714063/importing-modules-from-parent-folder
	# currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	# parentdir = os.path.dirname(currentdir)
	# sys.path.insert(0,parentdir) 
	# import pymmFunctions
	if newValue == None:
		print("So you want to set "+optionToSet)
		# the replace() call is a kind of stupid hack fix to get around 
		# paths with spaces getting an unnecessary escape slash
		# when you drag a folder into the terminal on Mac.... 
		# @fixme
		# should add mac functionality to sanitize func....
		# the input selection here replaces any escaped spaces with literal
		# spaces, which is needed when the paths are called by other funcs.
		newValue = input("Please enter a value for "+optionToSet+": ").rstrip().replace("\ "," ")
		newValue = sanitize_dragged_linux_path(newValue)
	config.set(section,optionToSet,newValue)
	with open(configPath,'w') as out:
		config.write(out)

def sanitize_dragged_linux_path(var):
	# this gets rid of extra characters added to paths dragged to terminal
	# in Ubuntu.
	if get_system() == 'linux':
		if len(var) >= 3 and var[0] == var[-1] == "'":
			var = var[1:-1]
			return var

		else:
			print("???")
			return var
	else:
		return var

def get_system():
	if sys.platform.startswith("darwin"):
		return "mac"
	elif sys.platform.startswith("win"):
		return "windows"
	elif sys.platform.startswith("linux"):
		return "linux"
	else:
		return False

def add_db_credentials():
	print(
		"WARNING: This is only for use when the database "
		"and the user are on the same machine. \n"
		"You must also create the user with these credentials using \n"
		"`python3 createPymmDB -m user`."
		)
	username = input("Enter the username: ")
	password = input("Enter the password for the user: ")

	set_value('database users',username,password)

def select_option():
	more = ''
	optionToSet = input("Enter the configuration option you want to set "
		"OR type 'db' to add credentials for a database user: ")
	if optionToSet in ('db','DB'):
		add_db_credentials()
		more = input("Type 'q' to quit or hit enter to choose another option to set: ")
		ask_more(more)

	else:
		matchingSections = 0
		for section in config.sections():
			if config.has_option(section,optionToSet):
				matchingSection = section
				matchingSections += 1
				set_value(section,optionToSet)
			else:
				pass

		if matchingSections == 0:
			print("\nOops, there is no option matching "+optionToSet+". Check your spelling and try again.\n")
		more = input("Type 'q' to quit or hit enter to select another option to set: ")
		ask_more(more)

def ask_more(more):
	if more == 'q':
		with open(configPath, 'r+') as conf:
			print('THIS IS WHAT THE CONFIG FILE LOOKS LIKE NOW.')
			for line in conf.readlines():
				print(line.rstrip())
			print("NOW EXITING. BYE!!")
		sys.exit()
	else:
		select_option()

configPath = os.path.join(os.path.dirname(os.path.abspath(__file__)),'config.ini')
# configPath = 'config.ini'
make_config(configPath)
config = configparser.SafeConfigParser()
config.read(configPath)

def main():
	with open(configPath, 'r+') as conf:
		print('THIS IS WHAT THE CONFIG FILE LOOKS LIKE NOW.')
		for line in conf.readlines():
			print(line.rstrip())
		print("IF YOU WANT TO CHANGE ANYTHING, LET'S GO!!")

		select_option()

if __name__ == '__main__':
	main()
