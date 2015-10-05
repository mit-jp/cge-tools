
# coding: utf-8

# In[24]:

# Load all the GDX files
from collections import OrderedDict

import gdx
import pandas as pd
import xray

FILES = [
    ('bau', 'result_urban_exo.gdx'),
    ('3', 'result_cint_n_3.gdx'),
    ('4', 'result_cint_n_4.gdx'),
    ('5', 'result_cint_n_5.gdx'),    
    ]

raw = OrderedDict()
for case, fn in FILES:
    raw[case] = gdx.File('gdx/' + fn)

CREM = raw['bau']
cases = pd.Index(raw.keys(), name='case')
time = pd.Index(filter(lambda t: int(t) <= 2030, CREM.set('t')))


# In[82]:

# List of all the parameters available in each file
#CREM.parameters()


# In[99]:

arrays = {}

# GDP
temp = [raw[case].extract('gdp_ref') for case in cases]
arrays['GDP'] = xray.concat(temp, dim=cases).sel(rs=CREM.set('r'))                     .rename({'rs': 'r'})


# In[100]:

# CO2 emissions
temp = []
for case in cases:
    temp.append(raw[case].extract('sectem').sum('g') +
        raw[case].extract('houem'))
arrays['CO2_emi'] = xray.concat(temp, dim=cases)


# In[104]:

# Air pollutant emissions
temp = []
for case in cases:
    temp.append(raw[case].extract('urban').sum('*'))
temp = xray.concat(temp, dim=cases).sel(rs=CREM.set('r')).rename({'rs': 'r'})
for u in temp['urb']:
    if u in ['PM10', 'PM25']:
        continue
    arrays['{}_emi'.format(u.values)] = temp.sel(urb=u).drop('urb')


# In[106]:

# Combine all variables into a single xray.Dataset; truncate time
data = xray.Dataset(arrays).sel(t=time)
data


# In[107]:

# Serialize to CSV: national totals
national = data.sum('r')

for c in cases:
    national.sel(case=c).drop('case').to_dataframe().to_csv('out/{}.csv'
                                                            .format(c))

