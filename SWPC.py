# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 16:27:23 2019

Data extracted from NOAA's SWPC service
SWPC = Space Weather Prediction Center
NOAA = National Oceanic and Atmosphere Administration

@author: Simen
"""

import urllib
import re
import json
from datetime import datetime 
from dateutil import tz
#Visual real time data can also be found here: 
#https://www.swpc.noaa.gov/products/real-time-solar-wind

class swpc():
    BASE_URL = "https://services.swpc.noaa.gov/"
    SUPPORTED_TOP_LEVEL_FOLDERS = ["products"]
    SUPPORTED_SUBFOLDERS = ["solar-wind","geospace"]
    SUPPORTED_APIS = ["mag","plasma","propagated-solar-wind","ephemerides",
                      "planetary-k-index-dst","10cm-flux",
                      "noaa-planetary-k-index"] #name of the supported API's (excluding resolution and filetype)
    
    first_level_urls = {}
    sub_level_urls = {}
    api_urls = {}
    unsupported = {}
    
    def __init__(self, debug=False):
        self.debug = debug
        #Extract all the currently supported URLs into the api_urls variable:
        first_level_list = re.findall(r"""<\s*a\s*href=["']([^=]+)["']""", urllib.request.urlopen(self.BASE_URL).read().decode("utf-8"))
        for sub_url in first_level_list:
            key = sub_url[0:-1] #remove the ending '/'
            self.first_level_urls[key] = self.BASE_URL+sub_url
            #Check if the folder is currently supported by this class
            if key in self.SUPPORTED_TOP_LEVEL_FOLDERS:
                sub_level_list = re.findall(r"""<\s*a\s*href=["']([^=]+)["']""", urllib.request.urlopen(self.first_level_urls[key]).read().decode("utf-8"))
                for sub_sub in sub_level_list:
                    if sub_sub.endswith(".json"):
                        api_name = sub_sub[0:sub_sub.find(".json")]
                        if self.__is_supported(self.first_level_urls[key],api_name):
                            self.api_urls[api_name] = self.first_level_urls[key]+sub_sub
                    else:
                        sub_key = sub_sub[0:-1]
                        self.sub_level_urls[sub_key] = self.first_level_urls[key]+sub_sub
                        #This is currently assumed to be the "bottom level" because I haven't encountered API's "further down" than this that I've needed (yet)
                        if sub_key in self.SUPPORTED_SUBFOLDERS:
                            bottom_level_list = re.findall(r"""<\s*a\s*href=["']([^=]+)["']""", urllib.request.urlopen(self.sub_level_urls[sub_key]).read().decode("utf-8"))
                            for api in bottom_level_list:
                                if api.endswith(".json"):
                                    api_name = api[0:api.find(".json")]
                                    if self.__is_supported(self.sub_level_urls[sub_key],api_name):
                                        self.api_urls[api_name] = self.sub_level_urls[sub_key]+api
                                else:
                                    if self.debug and not api.startswith("/"):
                                        # links starting with '/" is the link to the parent directory and should be ignored
                                        print("There are more folders or files existing in '"+sub_key+"'. Namely: '"+api+"'")
                
                            
                        else:
                            if self.debug and not sub_key.startswith("/") and len(sub_key) > 0:
                                print("Sub level folder '"+sub_key+"' currently not supported")
            else:
                if self.debug and len(key) > 0:
                    print("Top level folder '"+key+"' currently not supported")
        
        #Done extracting supported URLS
        #Unpack the supported API's
        for dataset_name in self.SUPPORTED_APIS:
            dataset_dict = {} # This dictionary will contain all resolutions of the given dataset when extraction is done
            self.__initialize_dataset(dataset_dict,dataset_name)
            setattr(self,dataset_name.replace("-","_"),dataset_dict) # Apply the dataset_dict as a variable of the class
     
    def __is_supported(self,parent_address, api_name):
        api = api_name+".json"
        supported = False
        for supported_api in self.SUPPORTED_APIS:
            #TODO: Find a better way to identify supported API's
            if api.startswith(supported_api):
                supported = True
                break
        if not supported and not api.startswith("/") and len(api) > 0:
            self.unsupported[api_name] = parent_address+api
            if self.debug:
                print("Found unsupported API: '"+api+"'")
        return supported
            
    def __initialize_dataset(self, dataset_dict, dataset_name):
        for api_key in self.api_urls:
            if api_key.startswith(dataset_name):
                #There will be several matches for datasets that are provided in more than one resolution
                url = self.api_urls[api_key];
                #Download dataset 
                space_weather_req = urllib.request.Request(url)
                opener = urllib.request.build_opener()
                f = opener.open(space_weather_req)
                temp_dataset =  json.loads(f.read())
                #extract all data for this resolution of the dataset_name
                dataset_dict[api_key] = self.__extract_dataset(temp_dataset) 
        
    def __extract_dataset(self,temp_dataset):
        dataset = {"time_tag_local_datetime": []}
        dataset_format = temp_dataset[0]
        for key in dataset_format:
            #init list to hold data for each type of data given
            #TODO: Maybe np.arrays should be used here. I don't remember how dictionaries and np.arrays cooperate at the time of writing.
            #but we DO know the length of the dataset at this point (len(temp_dataset)), so it could be done.
            dataset[key] = [] 
        for i in range(1,len(temp_dataset)):
            self.__extract_mag_datapoint(dataset_format,dataset,temp_dataset,i)
             
        return dataset
                
    def __extract_mag_datapoint(self,dataset_format,dataset,temp_dataset,index):
        #Extract datapoint from the file
        datapoint = temp_dataset[index]
        
        # Handle time_tag:    
        internal_i = 0
        for key in dataset_format:
            if key.count("time_tag") > 0:
                #Should be handled as datetime
                if key+"_local_datetime" not in dataset:
                    #If unexpected time_tag entries occur
                    dataset[key+"_local_datetime"] = []
                dataset[key+"_local_datetime"].append(self.__convert_time_tag_to_local_time(datapoint[internal_i]))
                dataset[key].append(datapoint[internal_i])
            elif key.count("noaa_scale") > 0 or key.count("observed") > 0:
                #Should be handled as string
                dataset[key].append(datapoint[internal_i])
            else:
                try:
                    dataset[key].append(float(datapoint[internal_i]))
                except ValueError as e:
                    try:
                        #Some dst values would be marked as follows: '-0.00021257800\x00'
                        dataset[key].append(float(datapoint[internal_i].replace("\x00","")))
                    except ValueError:
                        print("Found error in: '"+key+"', added -9999999 instead. Original error message:")
                        print(e)
                        dataset[key].append(-9999999)
                except TypeError as e:
                    print("Found error in: '"+key+"', added -9999999 instead. Original error message:")
                    print(e)
                    dataset[key].append(-9999999)
            internal_i = internal_i + 1

    def __convert_time_tag_to_local_time(self,time_tag):
        try:
            t_utc = datetime.strptime(time_tag, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            # 'planetary-k-index-dst.json' found to have different datetime fmt
            t_utc = datetime.strptime(time_tag, "%Y-%m-%d %H:%M:%S")            
        # Convert timezone to the one on local computer:
        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        t_utc = t_utc.replace(tzinfo=from_zone)
        return t_utc.astimezone(to_zone)
    
   


if __name__ == "__main__":
    s = swpc(debug = True)