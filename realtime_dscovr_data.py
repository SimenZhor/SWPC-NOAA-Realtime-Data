# -*- coding: utf-8 -*-
#This script is intended to eventually be some sort of Aurora warning/alert


import urllib
import json
from datetime import datetime 
from dateutil import tz
#Visual real time data can also be found here: 
#https://www.swpc.noaa.gov/products/real-time-solar-wind

#URL addresses to different datasets. 
#There are several others to be found at the base url, and at the products page
#that should be checked out. Especially because of the different resolutions
#the datasets are given in.
BASE_URL = "https://services.swpc.noaa.gov/"
products = BASE_URL+"products/"
mag_url = products+"solar-wind/mag-1-day.json" # ['time_tag', 'bx_gsm', 'by_gsm', 'bz_gsm', 'lon_gsm', 'lat_gsm', 'bt']
plasma_url = products+"solar-wind/plasma-1-day.json" #time_tag, density, speed, temperature
propagated_mag = products+"geospace/propagated-solar-wind-1-hour.json" #["time_tag", "speed", "density", "temperature", "bx", "by", "bz", "bt", "vx", "vy", "vz", "propagated_time_tag"]
k_index_dst = products+"/geospace/planetary-k-index-dst-1-hour.json" #["time_tag","planetary_k_index","dst"]
k_index_forecast = products+"noaa-planetary-k-index-forecast.json"
ten_cm_flux = products+"10cm-flux-30-day.json" #["time_tag","flux"]
alert_messages = products+"alerts.json" #Dictionary with entries: "product_id","issue_datetime","message"

#Download MAG data
space_weather_req = urllib.request.Request(mag_url)
opener = urllib.request.build_opener()
f = opener.open(space_weather_req)
dataset = json.loads(f.read())

def convert_time_tag_to_local_time(time_tag):
    t_utc = datetime.strptime(time_tag, "%Y-%m-%d %H:%M:%S.%f")
    # Convert timezone to the one on local computer:
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    t_utc = t_utc.replace(tzinfo=from_zone)
    return t_utc.astimezone(to_zone)

def extract_mag_datapoint(index):
    #Extract datapoint from the file
    datapoint = dataset[index]
    
    # Handle time_tag:    
    t = convert_time_tag_to_local_time(datapoint[0])
    
    #Handle B vector
    b = [float(datapoint[1]),float(datapoint[2]),float(datapoint[3])];
    return (t,b)
   
bz_neg = []
for i in range(1,len(dataset)):
    val = extract_mag_datapoint(i)
    t,b = val
    if(b[2]<0):
        bz_neg.append(val)

#print(bz_neg)
#t,b = extract_mag_datapoint(-1)
#print(b)