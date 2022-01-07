# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 20:06:34 2020

@author: Steinar
"""

# Runs the main script auto_vid_gen.py for the number of times assigned in range()

from IPython import get_ipython
import time

for n in range(1, 15): # Number of times to run main script

    startTime = time.time()

    try:
        get_ipython().magic('clear') # Clear console output
        get_ipython().magic('reset -f') # Reset variables
    except:
        pass

    runfile('C:/Users/pokal/AVFALL/aaaavg/auto_vid_gen.py', wdir='C:/Users/pokal/AVFALL/aaaavg')
    
    executionTime = (time.time() - startTime)
    print('Execution time in seconds: ' + str(executionTime))