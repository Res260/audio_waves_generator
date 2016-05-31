#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''-----------------------------------------------------------------------------
							FINAL PROJECT PRS
							     main.py
Author: Émilio G!
Date: from April 30 to May 26th
Version: 1.0
Description: This program generates audio waves and play them in real time.
You can adjust amplitudes and frequencies, and change the waves' type. You can
manage up to 5 waves (WARNING: even though the program is very light on ram
usage, you might experience unfluid sound. During development, my intel 3570K
could only manage a maximum of 2 waves at the same time. My laptop could barely
manage one without having interruptions in the audio stream or crashes that
ruined the experience. If you experience fluidity issues, try running the
program using another computer.). The GUI was created using Tkinter and most of
the calculations are done with numpy. Use this program as you wish, but please
give me credits for it :).
-----------------------------------------------------------------------------'''

import functions as fn

fn.init()
