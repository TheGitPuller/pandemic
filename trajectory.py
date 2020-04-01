# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 10:45:15 2020

@author: Rory Johnston (rory.e.johnston@gmail.com)

Acknowledgements:
    - Henry Reich from Minute Physics;
    - Aatish Bhatia;
    - https://www.postman.com/ API host
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import requests
from datetime import datetime
from matplotlib.collections import LineCollection

class trajectories():
    ''' Trajectories Class accesses live data and plots uptake against abundance
    in a log-log animation '''
    def __init__(self, confirmedCaseThreshold=None, countriesList=[""], 
                 smoothing=True, smoothingWindow=5, smoothingDegree=2, pathname="./"):
        
        if (confirmedCaseThreshold != None): self.filterByCases = True
        else: self.filterByCases = False
        
        if (countriesList[0] != ""): self.filterByCountry = True
        else: self.filterByCountry = False
    

        self.confirmedCaseThreshold = confirmedCaseThreshold
        self.countriesList = sorted(countriesList, key=str.lower)
        if self.filterByCountry:
            self.capCountriesList = self.countriesList.copy()
        else:
            self.capCountriesList = self.countriesList
        self.smoothing = smoothing
        self.smoothingWindow = smoothingWindow                  # MUST BE ODD: smoothing filter size (in days) for SlidingAverageFilter
        self.smoothingDegree = smoothingDegree                  # how many times smoothing filter is applied
        self.pathname = pathname                                # animation storage filepath
        self.availableCountries = []                                  # stores all potential countries to inspect
        
        # Convert all countries into lower case
        for i in range(len(self.countriesList)):
            self.countriesList[i] = self.countriesList[i].lower()
    
    def __call__(self, plot=True, *args, **kwargs):
        self.GetData()
        if plot:
            self.CreateAnimation()
    
    def GetData(self):
        # Get country info from COVID-19 API
        data = requests.get("https://api.covid19api.com/summary")
        # Check whether data has successfully been retrieved
        if (data.status_code == 200):
            print("="*30)
            print("Request successful")
            print("="*30)
        
        # Convert data to JSON format
        data = data.json()

        # Prepare containers and initialise parameters before for-loop
        # This will cause an error if we have the epidemiology data spanning multiple years
        prepareBuffer = False
        countriesStart = []
        if self.filterByCountry: cnt = 0
        else: cnt = 1
        checklist = self.countriesList.copy()
        # Extract slug to be used in getting Day One Total
        for i in range(1,len(data["Countries"])):
        
            totalConfirmed = data["Countries"][i]["TotalConfirmed"]
            # slug => human-readable keyword in URL (don't ask me the etymology - not even StackOverflow is useful)
            slug = data["Countries"][i]["Slug"]
            if slug[0] == '-': continue;                # Some entries start with a hyphen which indicates falsehood
            # Add to list of all potential names
            self.availableCountries.append(slug)
            # Full country name then remove commas and 
            country = data["Countries"][i]["Country"].split(",")[0].split(" (")[0]

            if self.filterByCases:
                # Only consider cases beneath confirmed case threshold
                if (totalConfirmed < self.confirmedCaseThreshold):
                    continue;       # i.e. don't do anything on this one and return to top of loop
            elif self.filterByCountry:
                if (slug not in self.countriesList):
                    continue;
                checklist.remove(slug)
            
            
            # Some countries are repeated sequentially (depending on country nomenclature), so we can omit these repeats
            if country == self.countriesList[-1]: continue
            # Korea is especially tricky, but this is lucky as North Korea won't have accurare data anyway, so we can ignore it
            if ("Korea" in country and "Korea" in self.countriesList[:]): continue  # Check for the Koreas, as these are sketchy (multiple entries for S.Korea)
            # Get information about how many cases since day one
            dayOneInfo = requests.get("https://api.covid19api.com/total/dayone/country/" + slug + "/status/confirmed")
            # Check data is accessible
            if (dayOneInfo.status_code != 200): raise print("API not connected"); exit;
            # Convert t JSON
            dayOneInfo = dayOneInfo.json()
            # Extract starting date
            startDate = dayOneInfo[0]["Date"].split('T')[0]                 # get date in yyyy-mm-dd format
            self.yyyy, mm, dd = [int(i) for i in startDate.split('-')]           # extract yyyy, mm, dd in different variables
            startDate = int(datetime(self.yyyy, mm, dd).strftime('%j'))          # collect variables and convert to Julian Day
            countriesStart.append(startDate)                                # Add to starting dates list to be used later
            dateList = np.array([], dtype=int)                              # Prepare TOTAL date list since D1
            totalConfirmedList = np.array([], dtype=int)                    # Prepare running total of total confirmed cases
            if not self.filterByCountry:
                # Add to list of str(countries names)
                self.countriesList.append(country)
            # Access total confirmed cases on a day-by-day basis for each country
            for dayCount in range(len(dayOneInfo)):
                dateList = np.append(dateList, startDate + dayCount)
                totalConfirmedList = np.append(totalConfirmedList, dayOneInfo[dayCount]["Cases"])
            # Keep track of when each country being considered stops tracking information
            endDate = dateList[-1]
            
            print(self.capCountriesList[cnt], "starts at Julian Day", startDate,
                  "and currently has", totalConfirmedList[-1], "total confirmed cases")
            # Initially we don't prepare a buffer as we're naive to the start date
            if (prepareBuffer):
                # If this start date is later than the earliest date we've encountered,
                # make a pad in array being added.
                # This will be the most commonly occuring case, so we'll put this 'if'
                # first to avoid multiple conditional evaluations.
                if(startDate > self.earliestDate): # create buffer in array
                    buffer = startDate - self.earliestDate
                    totalConfirmedList = np.hstack((np.zeros(buffer, dtype=int), totalConfirmedList))
                    
                # If this is the earliest date we've encountered, make a pad in main
                # storage block to accommodate for new dates
                elif (startDate < self.earliestDate):  # create buffer in allInfo
                    buffer = self.earliestDate - startDate
                    self.allTotal = np.hstack((np.zeros((self.allTotal.shape[0], buffer), dtype=int), self.allTotal))
                    self.earliestDate = startDate    # Reset to earlier start date
                
                ##=====================================================================
                
                # If this is the latest date we've encountered, make a pad in main
                # storage block to accommodate for new dates
                if(endDate > self.latestDate): # create buffer in array
                    buffer = endDate - self.latestDate
                    for col in range(buffer):
                        self.allTotal = np.hstack((self.allTotal, self.allTotal[:,-1].reshape((self.allTotal.shape[0], 1))))
                    # Reset to later end date 
                    self.latestDate = endDate
        
                # If data is short, make a pad in main
                # storage block to accommodate for new dates
                elif (endDate < self.latestDate):  # create buffer in allInfo
                    buffer = self.latestDate - endDate
                    totalConfirmedList = np.hstack((totalConfirmedList, np.zeros(buffer, dtype=int)))            
                
                # Otherwise unchanged...
                # If the start date for this country is the same as the earliest date
                # just wack it onto the main storage block
                self.allTotal = np.vstack((self.allTotal, totalConfirmedList))
                
            else:
                
                # If this is the first instance, just make the main storage block
                self.allTotal = totalConfirmedList.reshape(1, len(totalConfirmedList))
                self.earliestDate = startDate
                self.latestDate = endDate
                prepareBuffer = True
                
            cnt += 1
        
        # Remove the dangling empty string entry at head
        if self.filterByCases:
            self.countriesList = self.countriesList[1:] 
            self.capCountriesList = self.capCountriesList[1:]
        # Create a differences array to store new cases day-by-day for each country
        self.allNew = np.diff(self.allTotal, axis=1, prepend=0)        

        if self.smoothing:
            for i in range(self.smoothingDegree):
                # apply smoothing filter over each of the time series to iron-out the anomalies
                self.allNew = self.SlidingAverageFilter(self.allNew, window=self.smoothingWindow)
                self.allTotal = self.SlidingAverageFilter(self.allTotal, window=self.smoothingWindow)
        
        if (self.filterByCountry and len(checklist) != 0):
            errorList = []
            for error in checklist:
                errorList.append(self.capCountriesList[self.countriesList.index(error)])
            raise Exception("Error in countries given: Could not find " + str(errorList)
                            + '''\nPlease correct or use alternative spelling.
                            \nHave a look at the list of potential names:\n''' + str(self.availableCountries))
    
    # Define a smoothing filter to average out record noise
    def SlidingAverageFilter(self, timeseries, window=5):
        ''' Smoothing filter which moves a sliding window over the data for each
        country and makes each value at the centre of the window the same as  the
        mean for the surrounding values in the window
        Args:
            - timeseries: numpy ndarray of timeseries information for each country in each row
        Kwargs:
            - window: number of days being averaged over by sliding window of size = window
        
        Returns:
            - filtered timeseries.
        '''
        # Define left and right pads to get apply to the boundaries of each ndarray
        lpad = np.zeros((timeseries.shape[0], int(window/2)))
        rpad = np.zeros((timeseries.shape[0], int(window/2)))
        # Make the pads just large enough to fit half a filter wavelet in
        for i in range(int(window / 2)):        # Repeat for how many vector pads need to be added
            lpad[:,i] = timeseries[:,0]         # Repeat left side
            rpad[:,i] = timeseries[:,-1]        # Repeat right side
        
        # Join the two pads onto the main block
        timeseriesPadded = np.hstack((lpad, timeseries, rpad))
        # Move averaging filter over the entire block from first to last values of BLOCK (pads not inclusive)
        for i in range(int(window / 2), timeseries.shape[1] + int(window / 2)):
            timeseries[:,i - int(window / 2)] = np.mean(timeseriesPadded[:,i-int(window / 2):i+int(window / 2)+1], axis=1)
        # Return original timeseries
        return timeseries

    def CreateAnimation(self):
        
        image_all = []          # stores all artists per animation iteration
        image_thresold = 5
        fig, ax = plt.subplots()
        plt.style.use('seaborn')
        ax.set_xlabel("Total Confirmed Cases")
        ax.set_ylabel("New Confirmed Cases")
        ax.set_yscale("log")
        ax.set_xscale("log")
        ax.set_xlim(np.min(self.allTotal[self.allTotal >= image_thresold]), np.max(self.allTotal) * 5)
        ax.set_ylim(np.min(self.allNew[self.allNew >= image_thresold]), np.max(self.allNew) * 5)
        ax.set_title("COVID-19 uptake trajectory from day-zero")
        
        for i in range(0, self.allTotal.shape[1]):

            scatterList = [ax.scatter(self.allTotal[:,i], self.allNew[:,i], c='r')]
            plotList = []
            annotList = []
            # For each country being imaged
            for country_index in range(len(self.countriesList)):
                # Only bother with them above the xlim and ylim thresholds
                if (self.allTotal[country_index,i] > image_thresold and self.allNew[country_index,i] > image_thresold):
                    # Create country name annotations to draw in each iteration of animation
                    # Snapped onto the coordinates of current point and offset a little bit
                    annotList.append(ax.annotate(str(self.capCountriesList[country_index]),
                                xy = (self.allTotal[country_index,i], self.allNew[country_index,i]),
                                ha = "left", va = "bottom"))
                    # Define parameters to make snazzy vanishing line
                    lwidths = np.linspace(0, 2, i )
                    points = np.array([self.allTotal[country_index,:i+1], self.allNew[country_index,:i+1]]).T.reshape(-1,1,2)
                    segments = np.concatenate([points[:-1], points[1:]], axis=1)
                    # Create vanishing line collections to draw in each iteration of animation
                    plotList.append(ax.add_collection(LineCollection(segments, linewidths=lwidths, color='black')))
            # Get last two values of yyyy (20 for our case, again may cause issue if pandemic
            # spans multiple years, centuries or millenia).
            yy = str(self.yyyy)[-2:]
            # Convert to Gregorian calendar dates
            calendarDate = datetime.strptime(yy + str(i + self.earliestDate), '%y%j').date().strftime('%d/%m/%Y')
            # Create date annotations to draw in each iteration of animation
            dateList = [ax.annotate(calendarDate, xy = (np.min(self.allTotal[self.allTotal >= image_thresold]) + 5, np.max(self.allNew) * 4), va = "top")]
            image_all.append(plotList + scatterList + dateList + annotList)
        
        print("Preparing animation")
        # Create animation
        ani = anim.ArtistAnimation(fig, image_all, interval=1000, blit=False, repeat=False)
        # Save animation
        Writer = anim.writers['ffmpeg']
        writer = Writer(fps=7, metadata=dict(artist='Me'), bitrate=1600)
        ani.save(self.pathname + "COVID.mp4", writer=writer)
        plt.close(fig)  # prevent final frame plot from showing up inline below
