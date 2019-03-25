# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 20:30:38 2019

@author: Simen
"""

from SWPC import swpc
import matplotlib.pyplot as plt
import numpy as np

s = swpc()
plt.plot(s.mag['mag-1-day']['time_tag_local_datetime'],s.mag['mag-1-day']['bz_gsm'])

for i in range(0,len(s.propagated_solar_wind['propagated-solar-wind-1-hour']['bz'])):
    #The swpc is currently not implementing numpy, so if None is present this will not plot well.
    bz = s.propagated_solar_wind['propagated-solar-wind-1-hour']['bz'][i]
    if bz == None:
        s.propagated_solar_wind['propagated-solar-wind-1-hour']['bz'][i] = np.nan
        
plt.plot(s.propagated_solar_wind['propagated-solar-wind-1-hour']['propagated_time_tag_local_datetime'],s.propagated_solar_wind['propagated-solar-wind-1-hour']['bz'])
#More info on available variables: https://services.swpc.noaa.gov/

#There are a lot of APIs that are not currently supported by the swpc class.
#At the time of writing, the swpc class will only search through the following folders for.json files:
print(s.SUPPORTED_TOP_LEVEL_FOLDERS)
print(s.SUPPORTED_SUBFOLDERS)

#In those folders the following APIs will be supported:
print(s.SUPPORTED_APIS)

#And the following will not be supported:
print(s.unsupported.keys())

#This function is the first attempt for the user to refresh only the JSON files they want.
mag = s.refresh_dataset("mag","1-day")