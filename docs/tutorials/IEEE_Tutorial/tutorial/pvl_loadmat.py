from datetime import datetime,timedelta
import pandas as pd
from scipy.io import loadmat
import pdb

def parse(yr, doy, hr, min, sec):
    dt = datetime(yr - 1, 12, 31)
    delta = timedelta(days=doy, hours=hr,
                      minutes=min, seconds=sec)
    return dt + delta

def importdict(Dict):
    Dict.pop('__globals__')
    Dict.pop('__header__')
    Dict.pop('__version__')
    DF=pd.DataFrame(Dict[Dict.keys()[1]])
    for item in Dict:
        DF[item]=Dict[item]
    return DF



def pvl_loadmat(FileName,parsedates=False):

    WeatherData=loadmat(FileName)
    
    Weather=importdict(WeatherData)
    
    if parsedates==True:                 
        date=[]
        for pos in range(Weather.shape[0]):
            date.append(parse(Weather.Year.astype(int).values[pos],
                  Weather.Days.astype(int).values[pos],
                  Weather.Hours.astype(int).values[pos],
                  Weather.Minutes.astype(int).values[pos],
                  Weather.Seconds.astype(int).values[pos]))

        Weather.index=pd.to_datetime(date)
  
    return Weather

