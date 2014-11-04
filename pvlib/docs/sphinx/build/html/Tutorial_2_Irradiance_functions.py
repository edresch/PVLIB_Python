
# coding: utf-8

## Time series to irradiance tutorial

# In[1]:

get_ipython().magic(u'matplotlib inline')
import sys
import os
sys.path.append(os.path.realpath('../../../')) #append the parent directory to the system path
import pvlib
reload(pvlib)
import pandas as pd 
import matplotlib.pyplot as plt
try:
    import seaborn
    seaborn.set_context('paper')
except ImportError:
    pass


# In[2]:

datapath = os.path.join(pvlib.__path__[0], 'test', 'data')
fname = '703165TY.csv' #Use absolute path if the file is not in the local directory
TMY, meta = pvlib.tmy.readtmy3(filename=os.path.join(datapath, fname))
TMY.index.name = 'Time'
meta['SurfTilt'] = 30
meta['SurfAz'] = 0
meta['Albedo'] = 0.2

# create pvlib Location object
sand_point = pvlib.location.Location(meta['latitude'], meta['longitude'], tz='US/Alaska', 
                                     altitude=meta['altitude'], name=meta['Name'].replace('"',''))
print(sand_point)

# TMY data seems to be given as hourly data with time stamp at the end
# shift the index 30 Minutes back for calculation of sun postions
TMY = TMY.shift(freq='-30Min')


# In[3]:

meta


## Retreive required parameters

# Calculate the solar position for all times in the TMY file. Requires either PyEphem or a compiled spa_c library.

# In[4]:

solpos = pvlib.solarposition.get_solarposition(TMY.index, sand_point, method='pyephem')
solposspa = pvlib.solarposition.get_solarposition(TMY.index, sand_point, method='spa')


# In[5]:

# append solar position data to TMY DataFrame
TMY['SunAz'] = solpos['azimuth']
TMY['SunZen'] =  solpos['zenith']
TMY['SunZen'][TMY['SunZen']>90]=np.NaN
TMY['HExtra'] = pvlib.irradiance.extraradiation(doy=TMY.index.dayofyear)

TMY['AM'] = pvlib.atmosphere.relativeairmass(z=TMY.SunZen)

DFOut = pvlib.clearsky.disc(Time=TMY.index,GHI=TMY.GHI, SunZen=TMY.SunZen)

TMY['DNI_gen_DISC'] = DFOut['DNI_gen_DISC']
TMY['Kt_gen_DISC'] = DFOut['Kt_gen_DISC']
TMY['AM'] = DFOut['AM']
TMY['Ztemp'] = DFOut['Ztemp']


## Perez

# In[6]:

models = ['Perez', 'Hay-Davies', 'Isotropic', 'King', 'Klucher', 'Reindl']
TMY['Perez'] = pvlib.irradiance.perez(SurfTilt=meta['SurfTilt'],
                               SurfAz=meta['SurfAz'],
                               DHI=TMY.DHI,
                               DNI=TMY.DNI,
                               HExtra=TMY.HExtra,
                               SunZen=TMY.SunZen,
                               SunAz=TMY.SunAz,
                               AM=TMY.AM)


### HayDavies

# In[7]:

TMY['Hay-Davies'] = pvlib.irradiance.haydavies1980(SurfTilt=meta['SurfTilt'],
                                            SurfAz=meta['SurfAz'],
                                            DHI=TMY.DHI,
                                            DNI=TMY.DNI,
                                            HExtra=TMY.HExtra,
                                            SunZen=TMY.SunZen,
                                            SunAz=TMY.SunAz)                                


### Isotropic

# In[8]:

TMY['Isotropic'] = pvlib.irradiance.isotropicsky(SurfTilt=meta['SurfTilt'],
                                          DHI=TMY.DHI)


### King Diffuse model

# In[9]:

TMY['King'] = pvlib.irradiance.kingdiffuse(SurfTilt=meta['SurfTilt'],
                                    DHI=TMY.DHI,
                                    GHI=TMY.GHI,
                                    SunZen=TMY.SunZen)


### Klucher Model

# In[10]:

TMY['Klucher'] = pvlib.irradiance.klucher1979(SurfTilt=meta['SurfTilt'],
                                       SurfAz=meta['SurfAz'],
                                       DHI=TMY.DHI,
                                       GHI=TMY.GHI,
                                       SunZen=TMY.SunZen,
                                       SunAz=TMY.SunAz)                                


### Reindl

# In[11]:

TMY['Reindl'] = pvlib.irradiance.reindl1990(SurfTilt=meta['SurfTilt'],
                                     SurfAz=meta['SurfAz'],
                                     DHI=TMY.DHI,
                                     DNI=TMY.DNI,
                                     GHI=TMY.GHI,
                                     HExtra=TMY.HExtra,
                                     SunZen=TMY.SunZen,
                                     SunAz=TMY.SunAz)


# In[12]:

yearly = TMY[models].resample('A', how='sum').squeeze() / 1000.0  # kWh
monthly = TMY[models].resample('M', how='sum', kind='period') / 1000.0
daily = TMY[models].resample('D', how='sum') / 1000.0


### Plot Results

# In[13]:

ax = TMY[models].plot(title='Modelled in-plane diffuse irradiance')
# ax.legend(ncol=3, loc='upper center', title='In-plane diffuse irradiance')
ax.set_ylim(0, 800)
ylabel = ax.set_ylabel('Diffuse Irradiance [W]')


# In[14]:

TMY[models].describe()


# In[15]:

TMY[models].dropna().plot(kind='density')


# In[16]:

ax_monthly = monthly[models].plot(title='Monthly diffuse irradiation', kind='bar')
ylabel = ax_monthly.set_ylabel('Irradiation [kWh]')


# In[17]:

yearly.ix[1].plot(kind='barh')


#### Compute the mean deviation from average for each model and display as a function of the model

# In[18]:

mean_yearly = yearly.ix[1].mean()
yearly_mean_deviation = (yearly.ix[1] - mean_yearly) / yearly.ix[1] * 100.0
yearly_mean_deviation.plot(kind='bar')


# In[18]:




# In[18]:




# In[ ]:



