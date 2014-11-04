
# coding: utf-8

## import pvlib library

# In[1]:

#Change this to plot in external windows
get_ipython().magic(u'matplotlib inline')

#import required packages
import sys
import os
sys.path.append(os.path.realpath('../../../')) #append the parent directory to the system path
import pvlib
import pandas as pd 


## Import TMY data

### Use Sandia standard data 

# In[2]:


fname='./data/723650TY.csv' #Use absolute path if the file is not in the local directory
TMY, meta=pvlib.tmy.readtmy3(filename=fname)


# In[3]:

meta['SurfTilt']=30
meta['SurfAz']=0
meta['Albedo']=0.2


# In[4]:

print meta['Name']
print meta['longitude']


## Create a location object

# In[5]:

alb_loc = pvlib.location.Location(meta['latitude'], meta['longitude'], tz='US/Mountain', 
                                     altitude=meta['altitude'], name=meta['Name'].replace('"',''))


## Get solar angles

# In[6]:


#Using Ephemeris Calculations
ephemeris=pvlib.solarposition.get_solarposition(time=TMY.index,location=alb_loc,method='pyephem')
#Using NRELS SPA Calculations
spa=pvlib.solarposition.get_solarposition(time=TMY.index,location=alb_loc,method='spa')

print 'ephemeris values:', ephemeris.columns.values
print 'spa values:', spa.columns.values

TMY['SunAz']=spa.azimuth
TMY['SunZen']=spa.zenith
TMY['SunZen'][TMY['SunZen']>90]=np.NaN


# In[7]:


TMY['HExtra']=pvlib.irradiance.extraradiation(doy=TMY.index.dayofyear)

TMY['AM']=pvlib.clearsky.relativeairmass(z=TMY.SunZen)


## Generate Clear Sky and DNI

#### Using DISC Model

# In[8]:


DFOut=pvlib.clearsky.disc(Time=TMY.index,GHI=TMY.GHI, SunZen=TMY.SunZen)

TMY['DNI_gen_DISC']=DFOut['DNI_gen_DISC']
TMY['Kt_gen_DISC']=DFOut['Kt_gen_DISC']
TMY['AM']=DFOut['AM']
TMY['Ztemp']=DFOut['Ztemp']


#### Using Ineichen model

# In[9]:

DFOut=pvlib.clearsky.clearsky_ineichen(Time=TMY.index, Location=alb_loc)

TMY['Inechien_GHI']=DFOut.ClearSkyGHI


# In[10]:

TMY.GHI['March 25th,1987'].plot()
TMY.Inechien_GHI['March 25th,1987'].shift(1,'30min').plot()


## Plane Transformation

# In[11]:


TMY['In_Plane_SkyDiffuse']=pvlib.irradiance.perez(SurfTilt=meta['SurfTilt'],
                                            SurfAz=meta['SurfAz'],
                                            DHI=TMY.DHI,
                                            DNI=TMY.DNI,
                                            HExtra=TMY.HExtra,
                                            SunZen=TMY.SunZen,
                                            SunAz=TMY.SunAz,
                                            AM=TMY.AM)


## Ground Diffuse reflection

# In[12]:


TMY['GR']=pvlib.irradiance.grounddiffuse(GHI=TMY.GHI,Albedo=meta['Albedo'],SurfTilt=meta['SurfTilt'])


## Get AOI

# In[13]:


TMY['AOI']=pvlib.pvsystem.getaoi(SunAz=TMY.SunAz,SunZen=TMY.SunZen,SurfTilt=meta['SurfTilt'],SurfAz=meta['SurfAz'])


## Calculate Global in-plane

# In[14]:


In_plane=pvlib.irradiance.globalinplane(AOI=TMY.AOI,
                                DNI=TMY.DNI,
                                In_Plane_SkyDiffuse=TMY.In_Plane_SkyDiffuse,
                                GR=TMY.GR,
                                SurfTilt=meta['SurfTilt'],
                                SurfAz=meta['SurfAz'])

TMY['E']=In_plane.E
TMY['Eb']=In_plane.Eb
TMY['EDiff']=In_plane.Ediff


## Calculate Cell Temperature

# In[15]:


Cell_temp=pvlib.pvsystem.sapmcelltemp(E=TMY.E,
                            Wspd=TMY.Wspd,
                            Tamb=TMY.DryBulb)


TMY['Tcell']=Cell_temp['Tcell']
TMY['Tmodule']=Cell_temp['Tmodule']


## Import module coefficients

# In[16]:


moddb=pvlib.pvsystem.retreiveSAM(name='SandiaMod')
module=moddb.Canadian_Solar_CS5P_220M___2009_
module


##  import inverter coefficients

# In[17]:

Invdb=pvlib.pvsystem.retreiveSAM(name='SandiaInverter')
inverter=Invdb.Advanced_Energy__Solaron_333_3159000_105_480V__CEC_2008_
inverter


## Sandia Model

# In[18]:


DFOut=pvlib.pvsystem.sapm(Eb=TMY['Eb'],
                    Ediff=TMY['EDiff'],
                    Tcell=TMY['Tcell'],
                    AM=TMY['AM'],
                    AOI=TMY['AOI'],
                    Module=module)

TMY['Imp']=DFOut['Imp']
TMY['Voc']=DFOut['Voc']
TMY['Vmp']=DFOut['Vmp']
TMY['Pmp']=DFOut['Pmp']
TMY['Ix']=DFOut['Ix']
TMY['Ixx']=DFOut['Ixx']


## Single Diode Model

# In[19]:


moddb=pvlib.pvsystem.retreiveSAM(name='CECMod')
module=moddb.Canadian_Solar_CS5P_220P

IL,I0,Rs,Rsh,nNsVth=pvlib.pvsystem.calcparams_desoto(S=TMY.GHI,
                                               Tcell=TMY.DryBulb,
                                               alpha_isc=.003,
                                               ModuleParameters=module,
                                               EgRef=1.121,
                                               dEgdT= -0.0002677)


sdDFOut= pvlib.pvsystem.singlediode(Module=module,
                               IL=IL,
                               I0=I0,
                               Rs=Rs,
                               Rsh=Rsh,
                               nNsVth=nNsVth)


TMY['sd_Imp']=sdDFOut['Imp']
TMY['sd_Voc']=sdDFOut['Voc']
TMY['sd_Vmp']=sdDFOut['Vmp']
TMY['sd_Pmp']=sdDFOut['Pmp']
TMY['sd_Ix']=sdDFOut['Ix']
TMY['sd_Ixx']=sdDFOut['Ixx']           


## Inverter Model

# In[20]:


TMY['ACPower']=pvlib.pvsystem.snlinverter(Vmp=TMY.Vmp,Pmp=TMY.Pmp,Inverter=inverter)



# In[21]:

TMY.Pmp['March 25th,1987'].plot()
TMY.sd_Pmp['March 25th, 1987'].plot()


# In[22]:

scatter(TMY.sd_Pmp,TMY.Pmp,c=TMY.Kt_gen_DISC,alpha=.2) #change the value of C to see the sensitivity of model accuracy to provided meterological ocnditions 
plot(range(250),range(250),'r',linewidth=5)
xlabel('Single Diode model')
ylabel('Sandia model')

