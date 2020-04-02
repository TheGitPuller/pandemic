# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 11:36:39 2020

@author: Rory Johnston (rory.e.johnston@gmail.com)

Dependencies:
`ffmpeg` must be installed to save animation:
    - iOS: `brew install ffmpeg` or `pip install ffmpeg`
    - Windows: `pip install ffmpeg`
    - Linux: `sudo apt-get ffmpeg` | `pip install ffmpeg`
    
`trajectories.py` must be in the same executing folder.

Acknowledgements:
    - Henry Reich from Minute Physics;
    - Aatish Bhatia;
    - https://www.postman.com/ API host
"""

from trajectory import trajectories

countriesList = ["US", "Netherlands", "United-Kingdom", "Germany", "Spain", "Italy", "China"]

''' Instantiation examples '''
#trajectory_info = trajectories()
#trajectory_info = trajectories(confirmedCaseThreshold=15e3, smoothing=True, smoothingWindow=3, smoothingDegree=1, pathname="./YOUR_PATH/")
#trajectory_info = trajectories(confirmedCaseThreshold=10e3)
trajectory_info = trajectories(countriesList = countriesList, smoothingDegree=2)
''' Generate animation '''
trajectory_info(plot=True) 