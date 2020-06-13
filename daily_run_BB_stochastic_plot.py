#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 19:21:20 2020

@author: Tung & Hao
"""

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import time
start_time = time.time()

import matplotlib.pyplot as plt
import pandas_datareader.data as web
from datetime import datetime
from datetime import timedelta
import pandas as pd
import numpy as np

import os
my_path = os.getcwd()
print(my_path)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)     
pd.set_option('display.column', -1)   
pd.set_option('display.expand_frame_repr', False)

####Live data package

#from yahoo_fin import stock_info as si
#from yahoo_fin import options
#def get_iv(symbol):
#  price = si.get_live_price(symbol)
#  df = options.get_puts(symbol)
#  index_value = (df["Strike"] - price).apply(abs).idxmin()
#  df_iv = df.loc[index_value,:]
#  return df_iv["Implied Volatility"]


def get_stochf(stock_df,k_period=5,avg=3,col_name='Close'):
    df= stock_df
    #Create the "Lp" column in the DataFrame
    df['Lp'] = df['Low'].rolling(window=k_period).min()
    #Create the "Hp" column in the DataFrame
    df['Hp'] = df['High'].rolling(window=k_period).max()
    #Create the "%K" column in the DataFrame
    df['%K'] = 100*((df[col_name] - df['Lp']) / (df['Hp'] - df['Lp']) )
    #Create the "FullK" (or %D) column in the DataFrame
    df['FullK'] = df['%K'].rolling(window=avg).mean() 
    #Create the "FullD" column in the DataFrame
    df['FullD'] = df['FullK'].rolling(window=3).mean()
 
    return stock_df
 
def get_bband(stock_df,no_of_std=2,col_name='Close'):
    """
    Return bollinger Bands of stock_df
    """
    #Set number of days and standard deviations to use for rolling lookback period for Bollinger band calculation
    window = 21
    #df = stock_df
    #Calculate rolling mean and standard deviation using number of days set above
    rolling_mean = stock_df[col_name].rolling(window).mean()
    rolling_std = stock_df[col_name].rolling(window).std()
    #create two new DataFrame columns to hold values of upper and lower Bollinger bands
    stock_df['BBM'] = rolling_mean
    stock_df['BBH'] = rolling_mean + (rolling_std * no_of_std)
    stock_df['BBL'] = rolling_mean - (rolling_std * no_of_std)
    stock_df['Volume_pct_change'] = stock_df['Volume'].pct_change()*100
    stock_df['Close_price_pct_change'] = stock_df['Close'].pct_change()*100
    return stock_df
 
def get_price_df(symbol, duration=0):
    """
    Get data from yahoo
    duration: number of days, 0: get data from default 2010
    """
    end =  datetime.today()
    #end = '02-26-2020'
    #end = datetime.strptime(end, '%m-%d-%Y').date()
    start = end-timedelta(days=duration)    
    return web.DataReader(symbol,'yahoo',start,end)
 
##Function to compare a column with a constant
    # price_df["OS"] = np.linspace(0, 0,price_df.shape[0])
    # matched_index = price_df[price_df.FullK <= KD_OS_threshold].index
    # price_df.loc[matched_index,"OS"]=1
    
def state_check (price_df):
    """
    Return data frame with added Checked cols like BBL_trig/BBH_trig, StL_t/StH_t, OB/OBa, OS/OSa   
 
    OS Oversold condition:
        0: Nothing hit
        1: either (K or D or BBL) hit
        2: (K hit & BBL hit) Or (K & D hit)
        3: D hit (K don't need to hit) and BBL hit
    OSa: 2-day rolling sum of OS
              
    OB Overbought condition:
        0: Nothing hit
        1: either (K or D or BBH) hit
        2: (K hit & BBH hit) Or (K & D hit)
        3: D hit (K don't need to hit) and BBH hit
    OBa: 2-day rolling sum of OB
 
        4: 2 consecutive 2 cond #TODO
        6: 2 consecutive 3 cond #TODO
    """
    KD_OS_threshold = 30 
    KD_OB_threshold = 100-KD_OS_threshold
    
    
    #########################################
    #########################################
    #Check Bollinger Low
    price_df["BBL_trig"] = price_df["BBL"] >= price_df["Close"]
    #Check Bollinger High
    price_df["BBH_trig"] = price_df["BBH"] <= price_df["Close"]
    
    #Check oversold condition
    price_df["StL_t"] = np.linspace(0, 0,price_df.shape[0])
    matched_index = price_df[(price_df.FullK <= KD_OS_threshold) & (price_df.FullD > KD_OS_threshold)].index
    price_df.loc[matched_index,"StL_t"]=1
    matched_index = price_df[(price_df.FullK <= KD_OS_threshold) & (price_df.FullD <= KD_OS_threshold)].index
    price_df.loc[matched_index,"StL_t"]=2
    matched_index = price_df[(price_df.FullK > KD_OS_threshold) & (price_df.FullD <= KD_OS_threshold)].index
    price_df.loc[matched_index,"StL_t"]=3
    
    #Check Overbought condition
    price_df["StH_t"] = np.linspace(0, 0,price_df.shape[0])
    matched_index = price_df[(price_df.FullK >= KD_OB_threshold) & (price_df.FullD < KD_OB_threshold)].index
    price_df.loc[matched_index,"StH_t"]=1
    matched_index = price_df[(price_df.FullK >= KD_OB_threshold) & (price_df.FullD >= KD_OB_threshold)].index
    price_df.loc[matched_index,"StH_t"]=2
    matched_index = price_df[(price_df.FullK < KD_OB_threshold) & (price_df.FullD >= KD_OB_threshold)].index
    price_df.loc[matched_index,"StH_t"]=3
    
    price_df["OS"] = np.linspace(0,0,price_df.shape[0])
    #matched_index = price_df[(price_df.StL_t >0) & (price_df.BBL_trig == True)].index
    #price_df.loc[matched_index,"OS"] = 1
    matched_index = price_df[((price_df.StL_t ==1 )|(price_df.StL_t ==3) & (price_df.BBL_trig == False)) | \
                             ((price_df.StL_t ==0 )                      & (price_df.BBL_trig == True)) ].index
    
    price_df.loc[matched_index,"OS"] = 1
     #FIXME add 10% for case OS = 2
    matched_index = price_df[((price_df.StL_t ==1 )                      & (price_df.BBL_trig == True)) | \
                             ((price_df.StL_t >=2 )                      & (price_df.BBL_trig == False))].index
    price_df.loc[matched_index,"OS"] = 2
    matched_index = price_df[((price_df.StL_t >=2 ) & (price_df.BBL_trig == True)) ].index
    price_df.loc[matched_index,"OS"] = 3
    
    #add the last 2  values only if the current value is non-zero
    price_df["OSa"] = price_df["OS"].rolling(2).sum()
    matched_index = price_df[(price_df.OS ==0)].index
    price_df.loc[matched_index,"OSa"] = 0
    
    ##Over bought
    price_df["OB"] = np.linspace(0,0,price_df.shape[0])
    #matched_index = price_df[(price_df.StH_t >0) & (price_df.BBH_trig == True)].index
    #price_df.loc[matched_index,"OB"] = 1
    matched_index = price_df[((price_df.StH_t ==1 )|(price_df.StH_t ==3) & (price_df.BBH_trig == False)) | \
                             ((price_df.StH_t ==0 )                      & (price_df.BBH_trig == True)) ].index
    price_df.loc[matched_index,"OB"] = 1
     #FIXME add 10% for case OB = 2
    matched_index = price_df[((price_df.StH_t ==1 )                      & (price_df.BBH_trig == True)) | \
                             ((price_df.StH_t >=2 )                      & (price_df.BBH_trig == False))].index
    price_df.loc[matched_index,"OB"] = 2
    matched_index = price_df[((price_df.StH_t >=2 ) & (price_df.BBH_trig == True)) ].index
    price_df.loc[matched_index,"OB"] = 3
    
    #add the last 2  values only if the current value is non-zero
    price_df["OBa"] = price_df["OB"].rolling(2).sum()
    matched_index = price_df[(price_df.OB ==0)].index
    price_df.loc[matched_index,"OBa"] = 0
 
    return price_df
 
def osb_check_db(watchlist,duration = 100):
    """
    Report oversold status of Nx1 watchlist of stock symbol
    
    1.Pass in symbol and reiturn sym_df from yahoo
    2.Get BB and create 2 new columns in sym_df
    3.Get Stoch and crete 2 new column in sym_df
    4.Post process sym_df
    """
    
    symbol_db = watchlist
    count = 0
    j = len(watchlist)
    df = pd.DataFrame()
    
    for symbol in symbol_db:
        #print(symbol)
        count += 1
        if count % 5 == 0:
          print(count)
        sdf = get_price_df(symbol,duration = duration)
        sdf = get_stochf(sdf)
        sdf = get_bband(sdf)
        state_check(sdf)
        df2 = pd.DataFrame({"symbol":[symbol],
                            "OSa":[sdf["OSa"].tail(1).values[0]*-1],
                            "OSb":[sdf["OBa"].tail(1).values[0]],
                            "Indicator":[sdf["OSa"].tail(1).values[0]*-1+sdf["OBa"].tail(1).values[0]]})
        df = df.append(df2)
        
    return df
 

watchlist_loop =['D05.SI']
watchlist_test =['C','MSFT','FB','AAPL','GOOG','CRM']
watchlist_full = ['MSFT','FB','AAPL','GOOG','CRM', #tech
           'GILD','PFE','MMM','BMY','ABBV','CVS','JNJ','MRK', #pharma
           'AMD','INTC','NVDA', #chip
           'V','MA','AXP','DFS','COF', #credit card
           'JPM','BAC','C','WFC','MS','GS','BK', 'AIG','BRK-B','HSBC', #banks
           'WMT','AMZN','PG','UL','CL', #FMCG
           'XOM','CVX','SLB', #oil
           'BA', 
           'TSLA','SPOT','ZM','UBER','LYFT',
           '^GSPC','GLD','TLT','HYG','SLV',
           'QQQ','IJR','TQQQ',
           'ASHR','NSRGY',
           'ADBE','SLAB','CDNS','SNPS','BKNG','VEEV','RMD','MCD','YUM','YUMC','NKE','UNH',
           'DIS','KO','CLX','EL','DPZ','KWEB','ITA','DIA','IHF','GXC',
           'LMT', 'SPGI', 'CME', 'COST', 'ACN', 'HON', 'CMCSA', 'PEP', 'INTU', 'EDU', 'SBUX', 'ILMN', 'NVDA', 'ISRG', 
           'XAR', 'IBUY', 'SKYY', 'VNQ','MRNA','QCOM'
           ]

watchlist_HK_SG = ['0700.HK','2328.HK','3690.HK','2318.HK','9988.HK','0700.HK',
           'BUOU.SI','A17U.SI','RW0U.SI','CRPU.SI','O39.SI','HMN.SI','CSFU.SI',
           'BWCU.SI','BUOU.SI','D05.SI','H02.SI','J69U.SI','C61U.SI','C38U.SI','HMN.SI','CJLU.SI','N2IU.SI','C2PU.SI','ME8U.SI','CLR.SI']
           
df = osb_check_db(watchlist_full)

unique_values = df["Indicator"].unique()
list_symbol = []
for i in unique_values:
  str1 = df.loc[df["Indicator"] == i ]["symbol"].values
  list_1 = [i, str1]
  list_symbol.append(list_1)

fig, ax = plt.subplots(figsize=(10,7), constrained_layout=True)
df['Indicator'].hist(rwidth=0.5, color='w',align='mid')
plt.xlim(xmin=-6, xmax = 6)
for i in range(0,len(list_symbol)):
  if list_symbol[i][0]>=3:
    colors="g"
    weight='normal'
  else:
    if list_symbol[i][0]<=-3:
      colors="r"
      weight='normal'
    else:
      colors="b"
      weight='normal'
    
  for j in range(0,len(list_symbol[i][1])):
    ax.annotate(list_symbol[i][1][j],xy=(list_symbol[i][0],j+1),color=colors,weight=weight)
labels = ['Deep Oversold','Deep Oversold','Oversold','Oversold','Mild Oversold','Mild Oversold',0,'Mild Overbought','Mild Overbought','Overbought','Overbought','Deep Overbought','Deep Overbought']
ax.set_xticklabels(labels)
start, end = ax.get_xlim()
ax.xaxis.set_ticks(np.arange(start, end, 1))
plt.xticks(rotation=45)

plt.title('Stochastic & BB indicators', weight ='bold')
plt.xlabel('Oversold - Overbought Indicators',weight = 'bold')
plt.ylabel('# of securities', weight='bold')

plt.savefig(my_path + '/static/st_bb.png')
print("My program took", time.time() - start_time, "to run")