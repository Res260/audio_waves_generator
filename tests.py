# -*- coding: utf-8 -*-
'''-----------------------------------------------------------------------------
							FINAL PROJECT PRS
							     tests.py
Author: Émilio G!
Date: from April 30 to May 26th
Version: 1.0
Description: This file contains tests for functions in functions.py.
-----------------------------------------------------------------------------'''

import functions as fn
import numpy as np

def executeAllTests():
	"""
	PROCEDURE that calls every test in this file.
	"""
	testGetConfigurationFileData()
	testGenerateWave()
	testActuallyGenerateWave()
	testMixChunks()
	testGetIndex()


def testGetConfigurationFileData():
	"""
	PROCEDURE that calls getConfigurationFileData() multiple times to test its
	reliability. NOTE: make sure to delete the configuration file before running
	this test, as results may vary if you have it.
	It prints if the test is passed or failed.
	"""
	isPassed = True
	data = fn.getConfigurationFileData()
	if(data["amplitudes"] != [0,0,0,0,0]):
		isPassed = False
	else:
		pass
	if(data["frequencies"] != [20,20,20,20,20]):
		isPassed = False
	else:
		pass
	if(data["masterVolume"] != [0.7]):
		isPassed = False
	else:
		pass
	if(data["waveTypes"] != [0,0,0,0,0]):
		isPassed = False
	else:
		pass
	if(data["waveManagers"] != [None,None,None,None,None]):
		isPassed = False
	else:
		pass
	if(isPassed):
		print("Test de la fonction getConfigurationFileData() réussi.")
	else:
		print("Test de la fonction getConfigurationFileData() échoué.")


def testGenerateWave():
	"""
	PROCEDURE that calls generateWave() multiple times to test its reliability.
	It prints if the test is passed or failed.
	"""
	isPassed = True
	try:
		fn.generateWave(20,20,180)
		isPassed = False
	except:
		pass
	try:
		fn.generateWave(0,["ok"],180)
		isPassed = False
	except:
		pass
	try:
		fn.generateWave(0,20,300)
		isPassed = False
	except:
		pass
	try:
		fn.generateWave(3,-20,300)
		isPassed = False
	except:
		pass
	wave = fn.generateWave(3, 18000, 186.63859730762366)
	if(wave.all() != np.array([-2147483647, 2147483647], dtype=np.int32).all()):
		isPassed = False
	else:
		pass
	if(isPassed):
		print("Test de la fonction generateWave() réussi.")
	else:
		print("Test de la fonction generateWave() échoué.")


def testActuallyGenerateWave():
	"""
	PROCEDURE that calls actuallyGenerateWave() multiple times to test its reliability.
	It prints if the test is passed or failed.
	"""
	isPassed = True
	try:
		fn.actuallyGenerateWave(5,20, 2147483647)
		isPassed = False
	except:
		pass
	try:
		fn.actuallyGenerateWave(2,"ok",180)
		isPassed = False
	except:
		pass
	try:
		fn.actuallyGenerateWave(4,20,-50)
		isPassed = False
	except:
		pass
	try:
		fn.actuallyGenerateWave(3,-20,300)
		isPassed = False
	except:
		pass
	wave = fn.actuallyGenerateWave(4, 2, 186.63859730762366)
	if(wave.all() != np.array([2147483647, -2147483647], dtype=np.int32).all()):
		isPassed = False
	else:
		pass
	if(isPassed):
		print("Test de la fonction actuallyGenerateWave() réussi.")
	else:
		print("Test de la fonction actuallyGenerateWave() échoué.")


def testMixChunks():
	"""
	PROCEDURE that calls mixChunks() multiple times to test its reliability.
	It prints if the test is passed or failed.
	"""
	isPassed = True
	try:
		fn.mixChunks(234)
		isPassed = False
	except:
		pass
	try:
		fn.mixChunks("asdf")
		isPassed = False
	except:
		pass
	try:
		fn.mixChunks([])
	except:
		isPassed = False
	mixedChunks = fn.mixChunks([np.array([2]*1024), np.array([3]*1024)])
	if(mixedChunks.all() != np.array([5]*1024).all()):
		isPassed = False
	else:
		pass
	if(isPassed):
		print("Test de la fonction mixChunks() réussi.")
	else:
		print("Test de la fonction mixChunks() échoué.")


def testGetIndex():
	"""
	PROCEDURE that calls getIndex() multiple times to test its reliability.
	It prints if the test is passed or failed.
	"""
	isPassed = True
	try:
		fn.getIndex("okkkk")
		isPassed = False
	except:
		pass
	try:
		fn.getIndex(123)
		isPassed = False
	except:
		pass
	try:
		fn.getIndex([])
		isPassed = False
	except:
		pass
	index = fn.getIndex([1,2,None,"ok", None])
	if(index != 2):
		isPassed = False
	else:
		pass
	if(isPassed):
		print("Test de la fonction getIndex() réussi.")
	else:
		print("Test de la fonction getIndex() échoué.")


def printChunk(chunk):
	"""
	PROCEDURE that take each sample of an audio chunk and prints it, respecting
	the number of channels.
	used for development.
	"""
	print("1            2            3            4           ")
	print("------------ ------------ ------------ ------------")
	lenChunk = len(chunk)
	str = ""
	i = 0
	while i < lenChunk:
		str += "{:<13}".format(chunk[i])
		if(i % NUMBEROFCHANNELS == 0):
			print(str)
			str = ""
		i += 1
	print("---")


def log(thing):
	"""
	PROCEDURE that appends thing at the end of a log file.
	used for development.
	"""
	logFile = open("log", "a+")
	logFile.write(str(thing) + "\n")
	logFile.close()