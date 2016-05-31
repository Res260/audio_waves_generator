# -*- coding: utf-8 -*-
'''-----------------------------------------------------------------------------
							FINAL PROJECT PRS
							  functions.py
Author: Émilio G!
Date: from April 30 to May 26th
Version: 1.0
Description: This file contains all the function needed to run the program.
init() will launch the program.
-----------------------------------------------------------------------------'''

import time
import numpy as np
import pyaudio
from threading import Thread
import tkinter as tk
import tkinter.ttk as ttk
import configparser as cp
import os

#CONSTANTS
SINE = 0
SQUARE = 1
TRIANGLE = 2
INCREASINGSAWTOOTH = 3
DECREASINGSAWTOOTH = 4
WAVETYPESLIST = [0,1,2,3,4]

MAXNUMBEROFWAVES = 5
PORTAUDIOFORMAT = pyaudio.paInt32
NUMBEROFCHANNELS = 1
CHUNKLENGTH = 1024
SPS = 44100
MAXINT32 = 2147483647
MAXUNSIGNEDINT32 = 4294967294
MAXDECIBELS = 20*np.log10(MAXINT32)

SIZEX = 1200
CANVASHEIGHT = 300
CANVASWIDTH = 1180
CANVASMIDDLE = np.round(CANVASHEIGHT / 2)


#-------------------THE DEVIL (GLOBAL VARIABLES)------------------------------

threads = [None]*MAXNUMBEROFWAVES

#-----------------------------------------------------------------------------


def init():
	"""
	PROCEDURE that reads a configuration file, initializes pyAudio and important
	variables and calls interfaceHandler to start the GUI. Once the mainloop
	ends, it saves the data in the same configuration file, stocked in user's
	folder.
	SIDE EFFECT: on the configuration file.
	"""
	configurationFileData = getConfigurationFileData()
	numberOfActiveWaveManagers = \
		configurationFileData["numberOfActiveWaveManagers"]
	waveManagers = [None]*MAXNUMBEROFWAVES
	waves = [None]*MAXNUMBEROFWAVES
	waveTypes = configurationFileData["waveTypes"]
	pa = pyaudio.PyAudio()
	frequencies = configurationFileData["frequencies"]
	amplitude = configurationFileData["amplitudes"]
	masterVolume = configurationFileData["masterVolume"]
	isStreamOpen = [False]
	try:
		outputDeviceIndex = [pa.get_default_output_device_info()["index"]]
	except:
		raise IOError("A problem occured when trying to access default output"
		              "device.")
	outputDevicesInfos = [{}, [[], []]]
	appendOutputDevicesInfos(pa, outputDevicesInfos)
	try:
		interfaceHandler(numberOfActiveWaveManagers, waveManagers, waves,
		                waveTypes, frequencies, amplitude, masterVolume,
		                isStreamOpen, pa, outputDevicesInfos, outputDeviceIndex)
	except:
		pa.terminate()
		saveConfigurationFile(waveManagers, waveTypes, frequencies, amplitude,
		                      masterVolume)


#----------------------------------CONFIG---------------------------------------


def getConfigurationFileData():
	"""FUNCTION that queries configuration data from the configuration file and
	appends them to configurationData, a dictionnary. If it
	doesn't exist or if the configuration file is corrupted, it appends default
	values instead.
	RETURNS: configurationData (dict)"""
	configurationData = {}
	config = cp.ConfigParser()
	path = os.path.expanduser("~\PRAconfig.cfg")
	config.read(path)
	configurationData["numberOfActiveWaveManagers"] = 0
	try:
		for key in config["WAVEMANAGERS"]:
			if(config["WAVEMANAGERS"][key] != "None"):
				configurationData["numberOfActiveWaveManagers"] += 1
	except:
		configurationData["waveManagers"] = [None]*MAXNUMBEROFWAVES
	configurationData["waveTypes"] = []
	try:
		for key in config["WAVETYPES"]:
			if(int(config["WAVETYPES"][key]) in WAVETYPESLIST):
				configurationData["waveTypes"].append(
					int(config["WAVETYPES"][key]))
			else:
				int("ok")
		while len(configurationData["waveTypes"]) < MAXNUMBEROFWAVES:
			configurationData["waveTypes"].append(0)
	except:
		configurationData["waveTypes"] = [0]*MAXNUMBEROFWAVES
	appendParameterInfos(config, configurationData, "FREQUENCIES",
						 "frequencies", 20)
	appendParameterInfos(config,configurationData,"AMPLITUDES", "amplitudes", 0)
	configurationData["masterVolume"] = []
	try:
		for key in config["MASTERVOLUME"]:
			configurationData["masterVolume"].append(
				float(config["MASTERVOLUME"][key]))
		while len(configurationData["masterVolume"]) < 1:
			configurationData["masterVolume"].append(0)
	except:
		configurationData["masterVolume"] = [0.7]
	return configurationData


def appendOutputDevicesInfos(pa, outputDevicesInfos):
	"""
	PROCEDURE that queries output devices from pyAudio and adds them in
	outputDevicesInfos. It cleans duplicates. The result is a list of 2 elements
	outputDevicesInfos[0]: a dictionnary. [Key] = Name of output device
								          Value = device's index
	outputDevicesInfos[1]: list of 2 lists: [0]: device's index
											[1]: device's name
	SIDE EFFECT: outputDevicesInfos
	"""
	doContinue = True
	i = 0
	while doContinue:
		try:
			deviceInfos = pa.get_device_info_by_index(i)
			if(deviceInfos["maxInputChannels"] == 0):
				outputDevicesInfos[1][0].append(deviceInfos["index"])
				outputDevicesInfos[1][1].append(deviceInfos["name"])
		except:
			doContinue = False
		i += 1
	j = len(outputDevicesInfos[1][1]) - 1
	while j > 0:
		if(outputDevicesInfos[1][1][j] in outputDevicesInfos[1][1][0:j]):
			outputDevicesInfos[1][0].pop(j)
			outputDevicesInfos[1][1].pop(j)
		j -= 1
	outputDevicesInfosLength = len(outputDevicesInfos[1][0])
	k = 0
	while k < outputDevicesInfosLength:
		outputDevicesInfos[0][outputDevicesInfos[1][1][k]] = \
			outputDevicesInfos[1][0][k]
		k += 1


def appendParameterInfos(config, configurationData, nameInConfig,
						 nameInDictionnary, defaultValue):
	"""
	PROCEDURE that appends values to configurationData[nameInDictionnary] based
	on what's in config[nameInConfig]. If there is a problem, it appends
	defaultValue instead.
	SIDE EFFECT: dictionnary
	"""
	configurationData[nameInDictionnary] = []
	try:
		for key in config[nameInConfig]:
			configurationData[nameInDictionnary].append(
				int(config[nameInConfig][key]))
		while len(configurationData[nameInDictionnary]) < MAXNUMBEROFWAVES:
			configurationData[nameInDictionnary].append(defaultValue)
	except:
		configurationData[nameInDictionnary] = [defaultValue]*MAXNUMBEROFWAVES


def saveConfigurationFile(waveManagers, waveTypes, frequencies, amplitude,
                          masterVolume):
	"""
	PROCEDURE that takes all arguments above and writes their values in the
	configuration file.
	SIDE EFFECT: the configuration file.
	"""
	config = cp.ConfigParser()

	addParameter(config, "WAVEMANAGERS", waveManagers)
	addParameter(config, "WAVETYPES", waveTypes)
	addParameter(config, "FREQUENCIES", frequencies)
	addParameter(config, "AMPLITUDES", amplitude)
	addParameter(config, "MASTERVOLUME", masterVolume)
	path = os.path.expanduser("~\PRAconfig.cfg")
	with open(path, "w") as configFile:
		config.write(configFile)


def addParameter(config, parameterName, values):
	"""
	PROCEDURE that adds parameterName and its values to the config object.
	SIDE EFFECT: config (object).
	"""
	config[parameterName] = {}
	parameterLength = len(values)
	i = 0
	while i < parameterLength:
		config[parameterName][str(i)] = str(values[i])
		i +=1


#----------------------------------SOUND----------------------------------------


def generateWave(type, frequency, amplitude):
	"""
	FUNCTION that generate a single wave of desired type (sine 0, square 1,
	triangle 2, increasing sawtooth 3 or decreasing sawtooth 4),
	(peak) amplitude (in dB) and frequency (in Hz).
	Note: the frequency is approximated i.e. It is rounded with the sample rate.
	RAISES TypeError if either argument is invalid.
	RAISES ValueError if type is an invalid number.
	RETURNS a numpy array containing 32 bits integers of a wave.
	"""
	if(not isinstance(type, int) or not isinstance(frequency, int) or
		(not isinstance(amplitude, int) and not isinstance(amplitude, float))):
		raise TypeError("An argument is not of the good type (integer)")
	else:
		if(amplitude > MAXDECIBELS):
			raise ValueError("Amplitude is too high.")
		else:
			waveLength = np.round(SPS / frequency)
			highestNumber = np.round(10**(amplitude/20))
			waveArray = actuallyGenerateWave(type, waveLength, highestNumber)
			waveArray = np.clip(waveArray, -MAXINT32, MAXINT32)
			waveArray = np.repeat(waveArray, NUMBEROFCHANNELS)
	return np.int32(waveArray)


def actuallyGenerateWave(type, waveLength, highestNumber):
	"""FUNCTION that is called by generateWave() which is only made to shorten
	generateWave()'s length.
	RETURNS a numpy array containing 32 bits integers of a single wave."""
	if(waveLength < 0 or highestNumber < 0):
		raise ValueError("waveLength and highestNumber need to be positive.")
	else:
		waveArray = np.array([], dtype=np.int32)
		if(type == 0):
			linearSamples = np.linspace(0.5,(2*np.pi)+0.5, waveLength + 1)
			for sample in linearSamples:
				waveArray = np.append(waveArray, np.round(\
					np.sin(sample)*highestNumber))
			waveArray = np.delete(waveArray, len(waveArray) - 1)
		elif(type == 1):
			if(waveLength % 2 != 0):
				waveLength += 1
			half = waveLength / 2
			i = 0
			while i < half:
				waveArray = np.append(waveArray, highestNumber)
				i += 1
			while i < waveLength:
				waveArray = np.append(waveArray, -highestNumber)
				i +=1
		elif(type == 2):
			if(waveLength % 2 != 0):
				waveLength += 1
			half = waveLength / 2
			firstHalf = np.linspace(-highestNumber, highestNumber, half + 1)
			secondHalf =np.linspace(highestNumber, -highestNumber, half + 1)
			firstHalf = np.delete(firstHalf, len(firstHalf) - 1)
			secondHalf =np.delete(secondHalf, len(secondHalf) - 1)
			waveArray = np.append(waveArray, firstHalf)
			waveArray = np.append(waveArray, secondHalf)
		elif(type == 3):
			waveArray = np.append(waveArray, np.array(\
				np.linspace(-highestNumber,highestNumber, waveLength)))
		elif(type == 4):
			waveArray = np.append(waveArray, np.array(\
				np.linspace(highestNumber,-highestNumber, waveLength)))
		else:
			raise ValueError("Invalid Type.")
	return waveArray


def callback(in_data, frame_count, time_info, status, waves, masterVolume,
             frameIterators):
	"""NOTE: Changed so it is not threaded anymore. 160531"""
	"""SHOULD NOT BE CALLED BY ANYTHING ELSE THAN A PYAUDIO STREAM.
	UNPURE FUNCTION that starts a Thread for each wave in waves to repeat them
	correctly(to match CHUNKLENGTH). It then mixes every wave together to return
	a single chunk of audio data which will be multiplied by masterVolume's
	value, clipped and then played by the pyAudio Stream.
	SIDE EFFECT: frameIterators
	RETURNS a Tuple of
			-numpy array containing CHUNKLENGTH*NUMBEROFCHANNELS 32 bits audio
			samples
			-0 to tell the Stream Class to continue calling this function.
	"""

	repeatedWavesList = [None]*MAXNUMBEROFWAVES
	i = 0
	while i < MAXNUMBEROFWAVES:
		index = i
		processWave(index, waves[i], repeatedWavesList, frameIterators)
		i += 1
	mixedChunks = mixChunks(repeatedWavesList)
	return (np.int32(np.clip(mixedChunks*masterVolume[0],\
	                         -MAXINT32, MAXINT32)), 0)


def mixChunks(chunksList):
	"""
	FUNCTION that mixes all audio chunks together. The simple algorithm used is
	the addition ( :) ).
	RETURNS a single (unclipped) audio chunk.
	"""
	if(not isinstance(chunksList, list)):
		raise TypeError("chunksList must be a list.")
	else:
		indexesToMix = []
		chunksListLength = len(chunksList)
		i = 0
		while i < chunksListLength:
			if(type(chunksList[i]).__module__ == 'numpy'):
				indexesToMix.append(i)
			i += 1
		addedChunks = np.zeros(CHUNKLENGTH*NUMBEROFCHANNELS, dtype=np.int32)
		multipliedChunks = np.ones(CHUNKLENGTH*NUMBEROFCHANNELS, dtype=np.int32)
		for index in indexesToMix:
			addedChunks = addedChunks + chunksList[index]
		for index in indexesToMix:
			multipliedChunks = multipliedChunks * chunksList[index]
		multipliedChunks = multipliedChunks / MAXUNSIGNEDINT32
		mixedChunks = addedChunks - multipliedChunks
	return mixedChunks


def setNewWave(index, waves, waveTypes, frequencies, amplitude,  canvas):
	"""
	PROCEDURE that calls generateWave with the good index of waveTypes,
	frequencies and amplitudes arguments and appends the result to wave[index].
	It then calls paintAudioChunk to update the desired canvas.
	SIDE EFFECT: waves AND waveManager[index]'s canvas
	"""
	waves[index] = generateWave(waveTypes[index], frequencies[index],\
	                            amplitude[index])
	paintAudioChunk(waves[index], canvas, index)


def soundHandler(pa, waves, masterVolume,  isStreamOpen, outputDeviceIndex,
                 playButton, stopButton):
	"""
	PROCEDURE that starts sound() in a separate Thread if the stream is not
	already opened.
	SIDE EFFECT:-output device (sound will play)
				-isStreamOpen(when the user clicks on the stop Button)
				-playButton and stopButton(when stream starts or ends)
	"""
	if(not isStreamOpen[0]):
		lambdaSound = lambda: sound(pa, waves, masterVolume, isStreamOpen,\
		                            outputDeviceIndex, playButton, stopButton)
		threadSound = Thread(target=lambdaSound)
		threadSound.start()
	else:
		pass


def sound(pa, waves, masterVolume, isStreamOpen, outputDeviceIndex, playButton,
          stopButton):
	"""PROCEDURE that initializes a pyAudio Stream class that will periodically
	call lambdaCallback in another Thread to play sound. Then, it checks every
	0.2s if the stream should still be running. It also manages playButton and
	stopButton's states(normal/disabled). frameIterators exists to keep track of
	each wave's repetition so it sounds smooth.
	SIDE EFFECT:-outputDevice (sound will play)
				-isStreamOpen
				-playButton and stopButton"""
	framesIterator = [0]*len(waves)
	lambdaCallback = lambda in_data, frame_count, time_info, status: \
		callback(in_data, frame_count, time_info, status, waves, masterVolume,\
		         framesIterator)
	try:
		playButton.config(state=tk.DISABLED)
		stopButton.config(state=tk.NORMAL)
		stream = pa.open(
			rate=SPS,
			channels=NUMBEROFCHANNELS,
			format=PORTAUDIOFORMAT,
			output=True,
			output_device_index=outputDeviceIndex[0],
			frames_per_buffer=CHUNKLENGTH,
			stream_callback=lambdaCallback
		)
		stream.start_stream()
		isStreamOpen[0] = True
		continueStream = True
		while continueStream:
			time.sleep(0.2)
			if(not isStreamOpen[0]):
				continueStream = False
		stream.close()
		playButton.config(state=tk.NORMAL)
		stopButton.config(state=tk.DISABLED)
	except:
		playButton.config(state=tk.NORMAL)
		stopButton.config(state=tk.DISABLED)


def processWave(index, wave, repeatedWavesList, frameIterators):
	"""
	PROCEDURE that takes a single audio wave as an argument and repeats it
	enough times to match CHUNKLENGTH*NUMBEROFCHANNELS samples
	SIDE EFFECT:
	            -repeatedWavesList[index]
				-frameIterators[index] (too keep track of wave's period on the next
				call of this procedure.
	"""
	if(wave == None):
		pass
	else:
		waveLength = len(wave)
		numberOfSamples = CHUNKLENGTH * NUMBEROFCHANNELS
		repeatedChunk = np.array([])
		j = frameIterators[index]
		while j < numberOfSamples + frameIterators[index]:
			repeatedChunk = np.append(repeatedChunk, wave[j % waveLength])
			j += 1
		frameIterators[index] = j % waveLength
		repeatedWavesList[index] = repeatedChunk


#----------------------------SEMI-GLOBAL VARIABLES------------------------------


def setMasterVolumeValue(masterVolume, newValue):
	"""
	PROCEDURE that calculates a new volume multiplicator with newValue and puts
	it in masterVolume[0]
	SIDE EFFECT:-masterVolume[0]
	Formula taken from http://www.dr-lex.be/info-stuff/volumecontrols.html
	"""
	if(newValue == 0):
		masterVolume[0] = 0
	elif(newValue == 1):
		masterVolume[0] = 1
	else:
		masterVolume[0] = 0.001*np.exp(6.908*newValue)


def setOutputDeviceIndexValue(outputDevicesInfos, outputDeviceIndex,
                              outputDeviceListWidget, pa, waves, masterVolume,
                              isStreamOpen, playButton, stopButton):
	"""
	PROCEDURE that gets outputDeviceListWidget's value and gets its associated
	index. If a stream is playing, it stops the current one and starts another
	one (calling soundHandler), this time with the new output device.
	SIDE EFFECT:-outputDeviceIndex[0]
				-Same as soundHandler.
	"""
	outputDeviceIndex[0] = int(outputDevicesInfos[0][outputDeviceListWidget.get()])
	if(isStreamOpen[0]):
		isStreamOpen[0] = False
		time.sleep(0.2)
		soundHandler( pa, waves, masterVolume, isStreamOpen, outputDeviceIndex,\
		              playButton, stopButton)


def setFrequencyValue(index, waves, waveTypes, frequencies, amplitude,
                      newFrequency, canvas):
	"""
	PROCEDURE that sets newFrequency in frequencies[index]. It
	then produces a new wave with the new frequency.
	SIDE EFFECT:-frequencies[index]
				-waves[index]
				-waveManagers[index]'s canvas
	"""
	frequencies[index] = newFrequency
	setNewWave(index, waves, waveTypes, frequencies, amplitude,  canvas)


def setAmplitudeValue(index, waves, waveTypes, frequencies, amplitude,
                      newAmplitude, canvas):
	"""
	PROCEDURE that sets newAmplitude in amplitudes[index]. It
	then produces a new wave with the new amplitude.
	SIDE EFFECT:-amplitudes[index]
				-waves[index]
				-waveManagers[index]'s canvas
	"""
	amplitude[index] = newAmplitude
	setNewWave(index, waves, waveTypes, frequencies, amplitude,  canvas)


def setWaveType(index, waves, waveTypes, frequencies, amplitude, newWaveType,
                canvas):
	"""
	PROCEDURE that sets newWaveType in waveTypes[index]. It
	then produces a new wave with the new wave type.
	SIDE EFFECT:-waveTypes[index]
				-waves[index]
				-waveManagers[index]'s canvas
	"""
	waveTypes[index] = newWaveType
	setNewWave(index, waves, waveTypes, frequencies, amplitude,  canvas)


def setStreamStatus(isStreamOpen, status, stopButton):
	"""
	PROCEDURE that sets isStreamOpen[0] to status and disable stopButton.
	SIDE EFFECT: isStreamOpen[0] and stopButton.
	"""
	isStreamOpen[0] = status
	stopButton.config(state=tk.DISABLED)


#------------------------------INTERFACE----------------------------------------


def getIndex(waveManagers):
	"""
	FUNCTION that returns an appropriate index based on which index of
	waveManagers is None.
	RETURNS an index (int)
	"""
	if(not isinstance(waveManagers, list)):
		raise TypeError("waveManagers must be a list.")
	else:
		doContinue = True
		i = 0
		while doContinue:
			if(waveManagers[i] == None):
				doContinue = False
			else:
				i += 1
	return i


def interfaceHandler(numberOfActiveWaveManagers, waveManagers, waves, waveTypes,
                     frequencies, amplitudes, masterVolume, isStreamOpen, pa,
                     outputDevicesInfos, outputDeviceIndex):
	"""PROCEDURE that initializes everything in the GUI and runs the mainLoop.
	   SIDE EFFECT:-every argument excepted numberOfActiveWaveManagers and pa.
				   -output device (sound might play)
				   - threads"""
	root = tk.Tk()
	setRootProperties(root)
	coreFrame = tk.Frame(root, relief=tk.RAISED)
	waveManagersContainerCanvas = tk.Canvas(coreFrame,
	                                        relief=tk.RAISED, height=1000)
	scrollbar = tk.Scrollbar(coreFrame, orient=tk.VERTICAL,
	                         command=waveManagersContainerCanvas.yview)
	waveManagersContainerCanvas.config(yscrollcommand=scrollbar.set)
	waveManagersContainer = tk.Frame(waveManagersContainerCanvas,
									 bg="#444444", relief=tk.RAISED)
	mainOptions = tk.Frame(root, relief=tk.RAISED, borderwidth=1)
	lambdaAddAWaveManager = lambda: addAWaveManager(waveManagersContainer,
	        waveManagers, waves, waveTypes, frequencies, amplitudes, addButton)
	addButton = tk.Button(mainOptions, text="Ajouter une wave",
	                      command=lambdaAddAWaveManager)
	addMainOptions(mainOptions, addButton, lambdaAddAWaveManager, root,
				   masterVolume, pa, waves, isStreamOpen, outputDeviceIndex,
				   waveManagersContainer, waveManagers, waveTypes, frequencies,
				   amplitudes, outputDevicesInfos)
	coreFrame.pack(fill=tk.BOTH, expand=True)
	scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
	waveManagersContainerCanvas.pack(side=tk.BOTTOM)
	waveManagersContainer.pack(fill=tk.BOTH, expand=True, side=tk.TOP)
	waveManagersContainer.bind("<Configure>", lambda event:\
		updateCanvasView(waveManagersContainerCanvas))
	waveManagersContainerCanvas.create_window((0,0),
	                                window=waveManagersContainer,anchor='nw')
	i = 0
	while i < numberOfActiveWaveManagers:
		addAWaveManager(waveManagersContainer, waveManagers, waves, waveTypes,
		                frequencies, amplitudes, addButton)
		i += 1
	root.mainloop()
	root.destroy()


def setRootProperties(root):
	"""
	PROCEDURE that sets properties for object root (main window).
	SIDE EFFECT: root.
	"""
	root.resizable(width=False, height=False)
	sizey = 700
	posx  = 100
	posy  = 100
	root.geometry("%dx%d+%d+%d" % (SIZEX, sizey, posx, posy))
	root.title("Projet Final PRS")


def addMainOptions(mainOptions, addButton, lambdaAddAWaveManager, root,
				   masterVolume, pa, waves, isStreamOpen, outputDeviceIndex,
				   waveManagersContainer, waveManagers, waveTypes, frequencies,
				   amplitudes, outputDevicesInfos):
	"""PROCEDURE that add main options to the GUI. This procedure only exists
	to shorten interfaceHandler's length.
	SIDE EFFECT: every argument + GUI"""
	mainOptions.pack(fill=tk.X, expand=True)
	lambdaSetMasterVolume = lambda newValue: setMasterVolumeValue(masterVolume,
	                                            			int(newValue)/100)
	lambdaSound = lambda : soundHandler(pa, waves, masterVolume, isStreamOpen,
	                                outputDeviceIndex, playButton, stopButton)
	lambdaSetStreamStatus = lambda: setStreamStatus(isStreamOpen, False,
	                                                stopButton)
	lambdaSetOutputDeviceIndexValue = lambda event:\
		setOutputDeviceIndexValue(outputDevicesInfos, outputDeviceIndex,
			outputDevicesList, pa, waves, masterVolume, isStreamOpen,
			playButton, stopButton)
	masterVolumeScale = tk.Scale(mainOptions, command=lambdaSetMasterVolume,
	    label="Volume (%)", length=250, orient=tk.HORIZONTAL, from_=0, to=100,
		resolution=1, repeatdelay=0, troughcolor="#FFFC5E")
	if(masterVolume[0] == 0):
		masterVolume[0] = 0.0001
	volumePercentage = np.round((np.log(masterVolume[0]/0.001)/6.908)*100)
	masterVolumeScale.set(volumePercentage)
	playButton = tk.Button(mainOptions, text="play", command=lambdaSound)
	stopButton = tk.Button(mainOptions, text="stop",
	    command=lambdaSetStreamStatus, state=tk.DISABLED)
	stopButton.pack(fill=tk.X, side=tk.RIGHT, ipadx=5, ipady=3, padx=2, pady=3)
	playButton.pack(fill=tk.X, side=tk.RIGHT, ipadx=5, ipady=3, padx=5, pady=3)
	addButton.pack(fill=tk.X, side=tk.RIGHT, ipadx=5, ipady=3, padx=5, pady=3)
	masterVolumeScale.pack(fill=tk.X, side=tk.RIGHT)
	comboBoxFrame = tk.Frame(mainOptions)
	comboBoxFrame.pack(fill=tk.X, expand=True, side=tk.LEFT)
	outputDevicesList = ttk.Combobox(comboBoxFrame,
		values=outputDevicesInfos[1][1], textvariable=outputDevicesInfos[1][0],
	    state="readonly", width=30)
	outputDevicesList.bind('<<ComboboxSelected>>',
	                       lambdaSetOutputDeviceIndexValue)
	outputDevicesList.pack(fill=tk.X, expand=True, side=tk.BOTTOM)
	text = tk.Label(comboBoxFrame, text="Périphérique de sortie:")
	text.pack(fill=tk.X, expand=True, side=tk.TOP)


def addAWaveManager(waveManagersContainer, waveManagers, waves, waveTypes,
                    frequencies, amplitude,  addButton):
	"""PROCEDURE that appends a new wave manager to the GUI. It manages
	   index attribution so the wave manager changes only his own values.
	   SIDE EFFECT: every argument + threads."""
	index = getIndex(waveManagers)
	waveManagers[index] = tk.Frame(waveManagersContainer, borderwidth=2,
	                               relief=tk.RAISED, height=500)
	waveManagers[index].pack(fill=tk.X)
	if(not None in waveManagers):
		addButton.config(state=tk.DISABLED)
	waveManagerBottom = tk.Frame(waveManagers[index])
	waveManagerBottom.pack(side=tk.BOTTOM, fill=tk.X, expand=True)
	lambdaAmplitudeScaleValue = lambda amplitudeScaleValue: \
		setAmplitudeValue(index, waves, waveTypes, frequencies, amplitude,
		                  int(amplitudeScaleValue), canvas)
	amplitudeScale = tk.Scale(waveManagerBottom,
	    command=lambdaAmplitudeScaleValue, label="Amplitude(dB)", length=250,
	    orient=tk.HORIZONTAL, from_=0, to=np.floor(MAXDECIBELS), resolution=1,
	    repeatdelay=0, troughcolor="#FF975E")
	amplitudeScale.set(amplitude[index])
	amplitudeScale.pack(side=tk.LEFT)
	lambdaFrequencyScaleValue = lambda frequencyScaleValue:\
		setFrequencyValue(index, waves, waveTypes, frequencies, amplitude,
		                  int(frequencyScaleValue), canvas)
	frequencyScale = tk.Scale(waveManagerBottom,
		command=lambdaFrequencyScaleValue, label="Fréquence(Hz)", length=600,
	    orient=tk.HORIZONTAL, from_=20, to=18000, resolution=1, repeatdelay=0,
		troughcolor='#FFE25E')
	frequencyScale.set(frequencies[index])
	frequencyScale.pack(side=tk.LEFT)

	lambdaPaint = lambda event: paintAudioChunk(waves[index], canvas, index)
	canvas = tk.Canvas(waveManagers[index], width=CANVASWIDTH,
	                   height=CANVASHEIGHT, bg="#F2C849",
	                   highlightthickness=0)
	addButtonsToWaveManager(waveManagerBottom, index, waves, waveTypes, frequencies, amplitude, SINE, canvas, waveManagers, addButton)
	canvas.bind("<Button-1>", lambdaPaint)
	canvas.pack(side=tk.BOTTOM)
	createCanvasStaticElements(canvas, index)


def updateCanvasView(canvas):
	"""
	PROCEDURE that updates canvas' view to fit with the scrollbar.
	SIDE EFFECT: canvas.
	"""
	canvas.configure(scrollregion=canvas.bbox("all"),width=SIZEX -50,height=600)


def addButtonsToWaveManager(waveManagerBottom, index, waves, waveTypes,
				frequencies, amplitude, SINE, canvas, waveManagers, addButton):
	"""PROCEDURE that adds buttons (wave type buttons and the delete button) to
	waveManagers[index]. This procedure only exists to shorten
	addAWaveManager()'s length.
	SIDE EFFECT: every argument + GUI"""
	waveTypeFrame =tk.Frame(waveManagerBottom)
	waveTypeFrame.pack(side=tk.LEFT)
	sineWaveButton = tk.Button(waveTypeFrame, text="Sinusoïdale",
	    relief=tk.GROOVE, wraplength=70, command=lambda: setWaveType(index,
						waves, waveTypes, frequencies, amplitude, SINE, canvas))
	sineWaveButton.grid(row=0,column=0, sticky="wens")
	squareWaveButton = tk.Button(waveTypeFrame, text="Carrée", relief=tk.GROOVE,
	    wraplength=70, command=lambda: setWaveType(index, waves, waveTypes,
										frequencies, amplitude, SQUARE, canvas))
	squareWaveButton.grid(row=1,column=1, sticky="wens")
	triangleWaveButton = tk.Button(waveTypeFrame, text="Triangulaire",
	    relief=tk.GROOVE, wraplength=70, command=lambda: setWaveType(index,
					waves, waveTypes, frequencies, amplitude, TRIANGLE, canvas))
	triangleWaveButton.grid(row=0,column=1, sticky="wens")
	increasingSawToothWaveButton = tk.Button(waveTypeFrame,
		text="Dent de scie montante", relief=tk.GROOVE, wraplength=150,
	    command=lambda: setWaveType(index, waves, waveTypes, frequencies,
		                            amplitude, INCREASINGSAWTOOTH, canvas))
	increasingSawToothWaveButton.grid(row=0,column=3, sticky="wens")
	decreasingSawToothWaveButton = tk.Button(waveTypeFrame,
	    text="Dent de scie descendante", relief=tk.GROOVE, wraplength=150,
		command=lambda: setWaveType(index,waves, waveTypes, frequencies,
									amplitude, DECREASINGSAWTOOTH, canvas))
	decreasingSawToothWaveButton.grid(row=1,column=3, sticky="wens")
	deleteWaveManagerButton = tk.Button(waveTypeFrame, text="Supprimer",
	    relief=tk.GROOVE, wraplength=150, bg="#CC0000", fg="#FFFFFF",
	    command=lambda: deleteWaveManager(index, waveManagers, waves, waveTypes,
		                                frequencies, amplitude, addButton))
	deleteWaveManagerButton.grid(row=1,column=0, sticky="wens")


def deleteWaveManager(index, waveManagers, waves, waveTypes, frequencies,
                      amplitude, addButton):
	"""
	PROCEDURE that delete a wave manager from the GUI and resets
	variables[index]'s original values.
	SIDE EFFECT: every argument + threads.
	"""
	waveManagers[index].pack_forget()
	waveManagers[index] = None
	threads[index] = None
	waves[index] = None
	waveTypes[index] = SINE
	frequencies[index] = 20
	amplitude[index] = 0
	addButton.config(state=tk.NORMAL)


def createCanvasStaticElements(canvas, index):
	"""
	PROCEDURE that paints static elements for canvas. It will be called
	everytime a wave manager's wave is updated.
	SIDE EFFECT: canvas.
	"""
	canvas.create_text(40,10, text="Wave #" + str(index))
	canvas.create_line(0, 0, 0, CANVASHEIGHT, width=2, fill="#D45F00")
	canvas.create_line(CANVASWIDTH, 0, CANVASWIDTH, CANVASHEIGHT,\
	                   width=2, fill="#D45F00")
	canvas.create_line(0, CANVASMIDDLE, CANVASWIDTH, CANVASMIDDLE,\
	                   width=2, fill="#D45F00")


def resetCanvas(canvas, index):
	"""
	PROCEDURE that resets the canvas to its orginal state, so we can paint
	another wave in it. It will be called everytime a wave manager's wave is
	updated.
	SIDE EFFECT: canvas
	"""
	canvas.delete("all")
	createCanvasStaticElements(canvas, index)


def paintAudioChunk(chunk, canvas, index):
	"""
	PROCEDURE that first resets the canvas, then paints each sample of a sound
	chunk. It adapts itself to the length of chunk, which is cool.
	SIDE EFFECT: canvas
	"""
	resetCanvas(canvas, index)
	chunkLength = len(chunk)
	canvas.create_text(40,30, text=str(chunkLength) + " frames")
	if(chunkLength >=2000):
		width = 2
	else:
		width = np.ceil(-5*np.log10((chunkLength/2) / 1000)) + 1
	positionX = 3
	progressionPositionX = CANVASWIDTH / (chunkLength/NUMBEROFCHANNELS)
	x = 0
	while x < chunkLength:
		ratio = chunk[x] / MAXINT32
		if(ratio > 1):
			ratio = 1
		elif(ratio < -1):
			ratio = -1
		lineHeight = np.round(ratio * (CANVASMIDDLE - 1))
		canvas.create_line(np.round(positionX), CANVASMIDDLE - lineHeight,\
		                   np.round(positionX), CANVASMIDDLE - lineHeight+1,\
		                   width=width, fill="#000000")
		positionX += progressionPositionX
		x += NUMBEROFCHANNELS
