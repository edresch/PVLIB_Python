
## Python Basics

# The following covers some basic python functionality. This is by no means an exhaustive overview, but shows some of the main functionality of the platform 

#### Import modules 

# In[3]:

import sys
import os

sys.path.append(os.path.abspath('../')) #append the parent directory to the system path
sys.path.append(os.path.abspath('../pvlib')) #append the parent directory to the system path

import pvlib # imports pvlib into the namespace
import pandas as pd #imports pandas into the namespace and renames it to pd, for ease of use
from datetime import datetime #import functions for dealing with dates and times


#### Use modules

# In[4]:

pvlib.pvl_alt2pres     #try erasing __name__  and pressing tab, a list of available functions will appear that you can choose from 


# Out[4]:

#     'pvlib'

#### Use a Pandas DataFrame

# This block imports data from a .csv file and places it into a pandas DataFrame.

# In[7]:

TMY=pd.read_csv('Golden_mSi0251.csv',skiprows=2,index_col=0,parse_dates=True)
TMY['Isc (A)'].plot()
#TMY.info()    


# Out[7]:

#     <matplotlib.axes.AxesSubplot at 0x105f11790>

# Set the timezone, and shift time marker to UTC

# In[5]:

TMY=TMY.tz_localize('US/Mountain')
print 'Localized Time Zone'
print TMY.index


# Out[5]:

#     Localized Time Zone
#     <class 'pandas.tseries.index.DatetimeIndex'>
#     [2012-08-14 06:15:16-06:00, ..., 2013-09-24 17:30:17-06:00]
#     Length: 11887, Freq: None, Timezone: US/Mountain
# 

# In[6]:

TMY=TMY.tz_convert('UTC')
print 'Converted to UTC'
print TMY.index


# Out[6]:

#     Converted to UTC
#     <class 'pandas.tseries.index.DatetimeIndex'>
#     [2012-08-14 12:15:16+00:00, ..., 2013-09-24 23:30:17+00:00]
#     Length: 11887, Freq: None, Timezone: UTC
# 

# Resample to 10 min and hourly

# In[7]:

#perform the resampling
TMY_10min=TMY.resample('30min')
TMY_Hr=TMY.resample('H')
print TMY_Hr.index
print TMY.index


# Out[7]:

#     <class 'pandas.tseries.index.DatetimeIndex'>
#     [2012-08-14 12:00:00+00:00, ..., 2013-09-24 23:00:00+00:00]
#     Length: 9756, Freq: H, Timezone: UTC
#     <class 'pandas.tseries.index.DatetimeIndex'>
#     [2012-08-14 12:15:16+00:00, ..., 2013-09-24 23:30:17+00:00]
#     Length: 11887, Freq: None, Timezone: UTC
# 

# In[8]:

#plot the output
figure(1)
clf()  #clear Figure
TMY['Isc (A)'].plot(label='5min')
TMY_10min['Isc (A)'].plot(label='30min')
TMY_Hr['Isc (A)'].plot(label='hourly')

legend() #add a legend

xlim(datetime(2013,3,29),datetime(2013,3,31)) #limit the output to two days


# Out[8]:

#     (734956.0, 734958.0)

## Functions for importing Matlab code

# For the purpose of this tutorial we will not go into these in-depth, but they peform the required steps to import .mat data structures into python data structures. NOTE: This is not the default method of data import into python, and more typical will be the import of .csv or .tmy files, which is a simplified process

#### Define Functions

# In[9]:

from datetime import datetime,timedelta
def parse(yr, doy, hr, min, sec):
    dt = datetime(yr - 1, 12, 31)
    delta = timedelta(days=doy, hours=hr,
                      minutes=min, seconds=sec)
    return dt + delta


# In[10]:

def importdict(Dict):
    Dict.pop('__globals__')
    Dict.pop('__header__')
    Dict.pop('__version__')
    DF=pd.DataFrame(Dict[Dict.keys()[1]])
    for item in Dict:
        DF[item]=Dict[item]
    return DF




#### Import data

# In[1]:

import pandas as pd
from scipy.io import loadmat
import sys
import os

sys.path.append(os.path.abspath('../')) #append the parent directory to the system path
sys.path.append(os.path.abspath('../pvlib')) #append the parent directory to the system path
import pvlib


SystemInfo=loadmat('SystemInformation (1).mat')
SystemPerformance=loadmat('SystemPerformance (1).mat')
WeatherData=loadmat('WeatherData (1).mat')

Weather=importdict(WeatherData)
System=importdict(SystemPerformance)           
                        


# Out[1]:


    ---------------------------------------------------------------------------
    NameError                                 Traceback (most recent call last)

    <ipython-input-1-cc239123992c> in <module>()
         13 WeatherData=loadmat('WeatherData (1).mat')
         14 
    ---> 15 Weather=importdict(WeatherData)
         16 System=importdict(SystemPerformance)
         17 


    NameError: name 'importdict' is not defined


# In[2]:

# Date parser for column date inputs

date=[]
for pos in range(Weather.shape[0]):
    date.append(parse(Weather.Year.astype(int).values[pos],
          Weather.Days.astype(int).values[pos],
          Weather.Hours.astype(int).values[pos],
          Weather.Minutes.astype(int).values[pos],
          Weather.Seconds.astype(int).values[pos]))

Weather.index=pd.to_datetime(date)
System.index=pd.to_datetime(date)
Data=Weather.join(System,rsuffix='_sys')


# Out[2]:


    ---------------------------------------------------------------------------
    NameError                                 Traceback (most recent call last)

    <ipython-input-2-acb9e0d46303> in <module>()
          2 
          3 date=[]
    ----> 4 for pos in range(Weather.shape[0]):
          5     date.append(parse(Weather.Year.astype(int).values[pos],
          6           Weather.Days.astype(int).values[pos],


    NameError: name 'Weather' is not defined


#### Define site metadata and module parameters

####### NOTE: When importing TMY files, the 'meta' data structure is automatically populated. When importing custom data it must be defined explicitly.   Module parameters can also be imported automatically using the pvl_retreiveSAM function, if it exists in the SAM sandia module database. Otherwise they must be imported manually as below: 

# In[13]:

meta={'aziumth':0,
      'tilt':35,
      'parallelStrings':1,
      'seriesModules':5,
      'latitude':35.05,
      'longitude':-106.54,
      'TZ':-7,
      'albedo':.2}
meta=pvlib.pvl_tools.repack(meta)
      

module={'name'		: 'Sample Module',	
        'vintage'	: 2006,		
        'material' 	:'x-csi',			
        'area'		: 1.244,		
        'Aisc'	    : 0.000232,	
        'Aimp'	    : -0.00036,		
        'Isco'		: 5.988,		
        'Impo'		: 5.56,	
        'Voco'		: 48.53,	
        'Vmpo'		: 40.03,	
        'Bvoco'	   : -0.152,	
        'Bvmpo'	: -0.162,		
        'Mbvoc'	: 0,		
        'Mbvmp'	: 0,		
        '#Series'		: 72,		
        '#Parallel'		: 1,	
        'delT'		: 3,	
        'fd'		: 1,	
        'N'		: 1.241,	
        'IXO'		: 5.93,
        'IXXO'		: 4.12,	
        'a_wind'	: -3.62,	
        'b_wind'	: -0.075,		
        'C0'	        : 1.0072,
        'C1'            : -0.0072,
        'C2'            : 0.323035,
        'C3'            : -3.49839,
        'C4'            : 0.9966,
        'C5'            : 0.0034,
        'C6'            : 1.0827,
        'C7'            : -0.0827,		
        'A4'		: -0.0001223,
        'A3'            : 0.002416,
        'A2'            : -0.01912,
        'A1'            : 0.07365,
        'A0'            : 0.9259,
        'B5'		: -2.99e-09,
        'B4'            : 5.35e-07,
        'B3'            : -3.4e-05,
        'B2'            : 0.000862,
        'B1'            : -0.00699,
        'B0'            : 1.0,
        'FD'            :1}
module=pd.Series(module)


## Processing

##### This section includes the calls to pvlib required to process from raw meterological data to system performance. 

###### Import required modules. 

# In[14]:

import pvlib
import pandas as pd


###### NOTE: As a Developer, if you have changed any of the underlying pvlib files, you must reload them manually using the code below, or by restarting the kernel

# In[15]:

reload(pd) # reload the pvl_perez module


# Out[15]:

#     <module 'pandas' from '/usr/local/Cellar/python/2.7.5/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/pandas/__init__.pyc'>

##### Functions covered in the MATLAB Tutorial:

# These functions import the site location, and available DNI and DHI information in order to calculate the in-plane irradiance, E, and its diffuse, Ediff, and direct, Eb, components

# In[16]:

Data['SunAz'],Data['SunEl'],Data['ApparentSunEl'],Data['SolarTime'], Data['SunZen']=pvlib.pvl_ephemeris(Time=Data.index,Location=meta)
Data['HExtra']=pvlib.pvl_extraradiation(doy=Data.index.dayofyear)
Data['AM']=pvlib.pvl_relativeairmass(z=Data.SunZen)
Data['AOI']=pvlib.pvl_getaoi(SunAz=Data.SunAz,SunZen=Data.SunZen,SurfTilt=meta.tilt,SurfAz=meta.aziumth)

Data['In_Plane_SkyDiffuse']=pvlib.pvl_perez(SurfTilt=meta.tilt, #Problems with repeated minutes in the data!
                                            SurfAz=meta.aziumth,
                                            DHI=Data['DHI'],
                                            DNI=Data['DNI'],
                                            HExtra=Data.HExtra,
                                            SunZen=Data.SunZen,
                                            SunAz=Data.SunAz,
                                            AM=Data.AM)
Data['GR']=pvlib.pvl_grounddiffuse(GHI=Data['GHI'],Albedo=meta.albedo,SurfTilt=meta.tilt)
Data['E'],Data['Eb'],Data['EDiff']=pvlib.pvl_globalinplane(AOI=Data.AOI,
                                DNI=Data['DNI'],
                                In_Plane_SkyDiffuse=Data.In_Plane_SkyDiffuse,
                                GR=Data.GR,
                                SurfTilt=meta.tilt,
                                SurfAz=meta.aziumth)



#### Calcualte Cell Temperature

# In[17]:

Data.info()


# Out[17]:

#     <class 'pandas.core.frame.DataFrame'>
#     DatetimeIndex: 5040 entries, 2008-10-20 00:00:07 to 2008-10-26 23:58:09
#     Data columns (total 40 columns):
#     0                      5040 non-null float64
#     RefCellEeEAST          5040 non-null float64
#     WindSpeed              5040 non-null float64
#     Month                  5040 non-null uint8
#     GHI                    5040 non-null float64
#     AirTemp                5040 non-null float64
#     GNI                    5040 non-null float64
#     Seconds                5040 non-null uint8
#     Hours                  5040 non-null uint8
#     Pressure               5040 non-null float64
#     RefCellEeWEST          5040 non-null float64
#     RelativeHumidity       5040 non-null float64
#     DHI                    5040 non-null float64
#     RMBTime                5040 non-null float64
#     DNI                    5040 non-null float64
#     Days                   5040 non-null uint16
#     Minutes                5040 non-null uint8
#     Year                   5040 non-null uint16
#     POA                    5040 non-null float64
#     WindDirection          5040 non-null float64
#     0_sys                  5040 non-null float64
#     ACVoltage              5040 non-null float64
#     ACPower                5040 non-null float64
#     DCVoltage              5040 non-null float64
#     DCCurrent              5040 non-null float64
#     ArrayTemp              5040 non-null float64
#     ACCurrent              5040 non-null float64
#     SunAz                  5040 non-null float64
#     SunEl                  5040 non-null float64
#     ApparentSunEl          5040 non-null float64
#     SolarTime              5040 non-null float64
#     SunZen                 5040 non-null float64
#     HExtra                 5040 non-null float64
#     AM                     5040 non-null float64
#     AOI                    5040 non-null float64
#     In_Plane_SkyDiffuse    2304 non-null float64
#     GR                     5040 non-null float64
#     E                      2304 non-null float64
#     Eb                     5040 non-null float64
#     EDiff                  2304 non-null float64
#     dtypes: float64(34), uint16(2), uint8(4)

##### pvl_sapmcelltemp takes the total in-plane irradiance, wind speed, and ambient temperature

# Possible temperature models are: 
#           * 'Open_rack_cell_glassback' (DEFAULT)
#           * 'Roof_mount_cell_glassback'
#           * 'Open_rack_cell_polymerback'
#           * 'Insulated_back_polumerback'
#           * 'Open_rack_Polymer_thinfilm_steel'
#           * '22X_Concentrator_tracker'

# In[18]:

Data['Tcell'],Data['Tmodule']=pvlib.pvl_sapmcelltemp(E=Data.E,
                            Wspd=Data.WindSpeed,
                            Tamb=Data['AirTemp'],
                            modelt='Open_rack_cell_polymerback')



# Create a plot showing a timeseries comparison of temperature outputs

# In[19]:

clf()
plot(Data.index,Data.Tmodule,label='Calculated Temp')
plot(Data.index,Data.ArrayTemp,label='Actual Temp')
legend()


# Out[19]:

#     <matplotlib.legend.Legend at 0x105bce390>

# Create a plot showing a scatter plot comparison of module and cell temperature 

# In[20]:

clf()
plot(Data.Tmodule,Data.ArrayTemp,'.',label='Module Temp')
plot(Data.Tcell,Data.ArrayTemp,'.',label='Cell Temp')
xlabel('Calulated')
ylabel('Actual')
plot(range(-10,70),range(-10,70))
legend()


# Out[20]:

#     <matplotlib.legend.Legend at 0x1054becd0>

#### Model system output using SAPM model 

# The first lines of this section generate the in-plane beam and diffuse irradiance from measured POA and DNI values.
# 
# These are then input into the samp model, along with the module coefficients given at the beginning of this script

# In[31]:

Eb=Data.DNI*cos(np.radians(Data.AOI))
Ediff=Data.POA-Eb
DFOut=pvlib.pvl_sapm(Eb=Eb,
                    Ediff=Ediff,
                    Tcell=Data['Tcell'],
                    AM=Data['AM'],
                    AOI=Data['AOI'],
                    Module=module)


Data['Imp']=DFOut['Imp']*meta.parallelStrings
Data['Voc']=DFOut['Voc']
Data['Vmp']=DFOut['Vmp']*meta.seriesModules
Data['Pmp']=Data.Imp*Data.Vmp
Data['Ix']=DFOut['Ix']
Data['Ixx']=DFOut['Ixx']


#### Apply inverter model to system output

# Retrieve inverter characteristics from the online sandia inverter database. The Inverter used on this system is: 'SunPower_Corp__Original_Mfg___PV_Powered___SPR_2500_240V__CEC_2006_'
# 
# Try erasing this name, setting the cursor beside Invdb. and pressing tab. You will see a list of all possible inverters in the database

# In[23]:

Invdb=pvlib.pvl_retreiveSAM(name='SandiaInverter')
inverter=Invdb.SunPower_Corp__Original_Mfg___PV_Powered___SPR_2500_240V__CEC_2006_


# Calculate AC power output

# In[ ]:

Data['ACPower_modelled']=pvlib.pvl_snlinverter(Vmp=Data.Vmp,Pmp=Data.Pmp,Inverter=inverter)


##### Plot a timeseries of DC and AC system outputs

# In[36]:

clf()
plot(Data.index,Data.Pmp,label='Modelled DC Power')
plot(Data.index,Data.DCVoltage*Data.DCCurrent, label='Measured DC power')
plot(Data.index,Data.ACPower,label='Measured AC Power')
plot(Data.index,Data.ACPower_modelled,label='Modelled AC Power')
legend()


# Out[36]:

#     <matplotlib.legend.Legend at 0x105c886d0>

##### Investigate the relative difference in Power output as a function of AM and AOI 

# In[46]:

Relative_difference=(Data.Pmp-Data.DCVoltage*Data.DCCurrent)/Data.DCVoltage*Data.DCCurrent
clf()
scatter(Data.AM,Relative_difference,c=Data.AOI)
cb=colorbar()
ylim([-2,6])
xlim([1.3,3])
xlabel('Air Mass')
ylabel('Normalized Error')
cb.set_label('AOI')


# In[ ]:



