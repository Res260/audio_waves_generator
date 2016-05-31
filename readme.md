Audio waves generator program
=============================

Created by Émilio G! (#1434734) from april 30th to may 26th, 2015.

This program was created for my structured programming class. It is not
Object-Oriented because it was forbidden (we didn't learned it yet). This
software generates sound waves and plays them in real time. It has a GUI.

INSTALLATION
-------------------------------------------------------------------------------

1- Install Python 3 (http://python.org)
2- Unzip all the files of the program in a folder

###WINDOWS
Note: make sure C:\Python34\Scripts is in the path environment variable.
3-In a cmd, install wheel (pip install wheel)
4-Install numpy using file "numpy-1.9.2+mkl-cp34-none-win32.whl" (pip install
	"path\numpy-1.9.2+mkl-cp34-none-win32.whl"
5-Install pyAudio using file "PyAudio-0.2.8-cp34-none-win32.whl" (pip install
	"path\PyAudio-0.2.8-cp34-none-win32.whl"

###LINUX
3- In a terminal, install numpy (sudo apt-get install python3-numpy)
4-             ""         pyaudio (sudo apt-get install python3-pyaudio)
5-You might (????) need to install tkinter (sudo apt-get install python3-tk)

USAGE
-------------------------------------------------------------------------------
- Launch main.py with a python interpreter and enjoy generating audio waves.
WARNING: even though the program is very light on ram
usage, you might experience unfluid sound. During development, my intel 3570K
could only manage a maximum of 2 waves at the same time. My laptop could barely
manage one without having interruptions in the audio stream or crashes that
ruined the experience. If you experience fluidity issues, try running the
program using another computer :(.

TESTS
-------------------------------------------------------------------------------
- To use routines's tests, you need to import test.py in a python interperter.
Then, you can test a routine by calling "test*NameOfFunction*". Alternatively,
you could call the routine "executeAllTests", which will run every test in the
file at the time of this writing.

Questions or anything else: egg997@gmail.com