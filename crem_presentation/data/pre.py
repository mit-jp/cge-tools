
# coding: utf-8

# In[24]:

# Load all the GDX files
from collections import OrderedDict
from os import makedirs as mkdir
from os.path import join

import gdx
import pandas as pd
import xray

GDX_DIR = 'gdx'
OUT_DIR = '../../../cecp-cop21-data'
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


# ## TODO: further variables
# 
# - CO2 price: `report('PTCARB',t,'CHN')`
# - Primary energy `egyreport2('egycons',t,'COL',rs)`
# - Consumption: `report(c,t,rs)`
# - Population
# - Share of coal in production inputs
# - "(In)efficiency" of coal

# In[106]:

# Combine all variables into a single xray.Dataset and truncate time
data = xray.Dataset(arrays).sel(t=time)
# National totals
national = data.sum('r')
data


# In[149]:

# TODO: output a README file along with the data files

# Create directories
for r in CREM.set('r'):
    mkdir(join(OUT_DIR, r))
mkdir(join(OUT_DIR, 'national'))

# Serialize to CSV
for c in cases:
    # Provincial data
    for r in CREM.set('r'):
        data.sel(case=c, r=r).drop(['case', 'r']).to_dataframe().to_csv(
            join(OUT_DIR, r, '{}.csv'.format(c)))
    # National data
    national.sel(case=c).drop('case').to_dataframe()             .to_csv(join(OUT_DIR, 'national', '{}.csv'.format(c)))

