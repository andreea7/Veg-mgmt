# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 16:11:35 2017

@author: a3dp
"""

#match work complete work categories to 2017 VM Contracts_Table based on contractor, division and work category (need all 3 to find an accurate match)
#also need to filter for 2017 contracts
#input trim types
#merge rates & trim types to VM Contracts_Table based on contract number

import pandas as pd
from glob import glob
import numpy as np
import datetime as dt

table = pd.read_excel('2017 VM Contracts_Table.xlsx')
rates = pd.read_excel('RateCode_2017_mod.xlsx')

rates = rates.loc[rates['contract_group'] == 'Distribution'] 
rate_dist = rates.groupby(['contract_group']).size().reset_index()
print(rate_dist)

#match up work complete divs, etc
#create a df "frame" with work complete csv files for 2016 ONLY
csv_files = glob('WC_2016*.csv')    
frame = pd.DataFrame()
list_ = []
for file_ in csv_files:
    df1 = pd.read_csv(file_,index_col=None, header=0, low_memory=False)
    list_.append(df1)
frame = pd.concat(list_)

frame = frame.sort_values('WORK_DATE', ascending= False)  #sort in ascending order

#clean up frame data
x = frame
x = x.loc[x['T_D'] == 'D'] #sort for Distribution only
x.loc[x.TRIM_TYPE == 'td ','TRIM_TYPE'] = 'TD ' #convert td to TD

#sort work categories in work complete (i.e. frame)
work = x.groupby(['sWorkCat']).size().reset_index()
#x = x.rename(columns = {'sWorkCat':'sWorkCat'})
x.loc[x.sWorkCat == 'FIRST PATROL ','sWorkCat'] = 'FIRST PATROL' #consolidate FIRST PATROL CATEGORIES
#exclude following Work Categories:
x = x[x.sWorkCat != 'UR'] #unit reduction - no longer used
x = x[x.sWorkCat != 'WT'] #Trow - for Transmission only
x = x[x.sWorkCat != 'DV'] #Division / Non-VM (work for other divisions)
x = x[x.sWorkCat != 'EM'] #Emergency - done on T&M basis
work = x.groupby(['sWorkCat']).size().reset_index()

#import ratekey to match x
ratekey = pd.read_csv('VM_rate_codes.csv')
ratekey.drop(ratekey.index[[40,41]], inplace=True)
ratekey.reset_index()

r = ratekey
r = r.rename(columns = {'TRIM\r\nCODE':'TrimCode'})
r = r.rename(columns = {'RATE\r\nCODE':'RateCode'})

#NOT ALL TRIM TYPES MERGED, ALTHOUGH ALL ARE IN THE VM RATE CODES. 
#--> LIKELY, ISSUES WITH WHITE SPACES in x
x = pd.merge(x,r,left_on = ('TRIM_TYPE'), right_on = ('TrimCode'))


#clean up work types to merge with work complete
#filter for 2017 codes only
table["dtEndDate"] = pd.to_datetime(table["dtEndDate"])
table['Year'] = table['dtEndDate'].dt.year
table1 = table.loc[table['Year'] == int('2017')] #| int('2016')] want to filter for 2016 too
table1.groupby(['Year']).size().reset_index()

#clean up non-standard work category rates: C1, CM, FIRST PATROL and YS
'''
C1 = x.loc[x['sWorkCat'] == 'C1']
C1work = C1.groupby(['sWorkCat','TT_CONTRACTOR','DIVISION']).size().reset_index()
CM = x.loc[x['sWorkCat'] == 'CM']  #CE IN CONTRACTS_TABLE
FIRST_PATROL = x.loc[x['sWorkCat'] == 'FIRST PATROL']
FIRST_PATROLCode = pd.merge(table, FIRST_PATROL, left_on = ('sContCode', 'sDivCode', 'sDistrict'), right_on = ('TT_CONTRACTOR', 'DIVISION', 'sWorkCat'), how = 'inner')
#added rows (22081 compared to 23751 after merge)
FIRST_PATROLwork = FIRST_PATROLCode.groupby(['sWorkCat','TT_CONTRACTOR','DIVISION', 'work type']).size().reset_index()

CECode = pd.merge(table, CE, left_on = ('sContCode', 'sDivCode', 'sDistrict'), right_on = ('TT_CONTRACTOR', 'DIVISION', 'sWorkCat'), how = 'inner')
CEwork = CE.groupby(['sWorkCat']).size().reset_index()
CEwork = CECode.groupby(['sWorkCat','TT_CONTRACTOR','DIVISION', 'work type']).size().reset_index()
'''

table.loc[table.sWorkCat == 'CE','sDistrict'] = 'CM' #convert CE to CM in table to match frame
#convert FIRST PATROL to C1 to match table rates
x.loc[x.sWorkCat == 'FIRST PATROL','sWorkCat'] = 'C1'

#match YS
YS = x.loc[x['sWorkCat'] == 'YS']  
YSCode = pd.merge(table, YS, left_on = ('sContCode', 'sDivCode', 'sDistrict'), right_on = ('TT_CONTRACTOR', 'DIVISION', 'sWorkCat'), how = 'inner')
YSwork = YSCode.groupby(['sWorkCat','TT_CONTRACTOR','DIVISION', 'work type']).size().reset_index()

#merge on 3 criteria (sContCode, sDivCode, and sDistrict [work type]) 
wc_contracts = pd.merge(table, x, left_on = ('sContCode', 'sDivCode', 'sDistrict'), right_on = ('TT_CONTRACTOR', 'DIVISION', 'sWorkCat'), how = 'inner')

x.shape[0]
wc_contracts.shape[0]
table.shape[0]

#CEMA and YO Routine
#separate out contractor = "OTH" (other) for Erik to review and fill in
z = x.loc[x['TT_CONTRACTOR'] == 'OTH']#convert td to TD
zwork = z.groupby(['TT_CONTRACTOR','DIVISION','sWorkCat']).size().reset_index()
writer = z.to_csv('Other.csv')


#call out specific districts with uniqure rates as divisions
#needs to be based on division and district
x.loc[x.District == 'SO','Code'] = 'NC - SANTA ROSA'
x.loc[x.District == 'Va','Code'] = 'NB - VALLEJO'
x.loc[x.District == 'MA','Code'] = 'NB - MARIN'
x.loc[x.District == 'NA','Code'] = 'Nb - NAPA'
x.loc[x.District == 'SO','Code'] = 'NC - SANTA ROSA'
'''

