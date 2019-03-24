# SWPC-NOAA-Realtime-Data

A not very well developed class for extracting data from the NOAA SWPC real time space weather data API at [link](https://services.swpc.noaa.gov/)

There is no credentials needed to use this API, so please use it responsibly.

## Functional approach:
- `s = swpc()` returns a object containing all currently supported datasets as dictionaries. Currently available:
  - `s.mag`
  - `s.plasma`
  - `s.propagated_solar_wind`
  - `s.ephemerides`
  - `s.10cm_flux`
  - `s.planetary_k_index_dst`
  - `s.noaa_planetary_k_index`
- Some datasets will have several resolutions, and the first key of the dataset will be the full name of the corresponding .json file
  - ex `s.mag['mag-1-day']`
- The keys will continue to follow the naming conventions of the original file. If you are unsure of the key names check [link](https://services.swpc.noaa.gov/) and locate your given file.

### TODO:
- Write functions that makes it possible to refresh only 1 dataset, so the user can choose which values are necessary to download.
- Implement ways to handle other .json files from the source ([link](https://services.swpc.noaa.gov/))
- Should probably change from lists to numpy-arrays as the data holder class.
  - This would also mean that np.nan should be default for invalid values


### Acknowledgements:
Data extracted from NOAA's SWPC service
- SWPC = Space Weather Prediction Center
- NOAA = National Oceanic and Atmosphere Administration
