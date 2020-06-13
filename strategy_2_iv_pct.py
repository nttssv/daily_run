#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 19:57:39 2020

@author: Tung
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

from yahoo_fin import stock_info as si
from yahoo_fin import options
def get_iv(symbol):
  price = si.get_live_price(symbol)
  df = options.get_puts(symbol)
  index_value = (df["Strike"] - price).apply(abs).idxmin()
  df_iv = df.loc[index_value,:]
  return df_iv["Implied Volatility"]

def get_price_df(symbol, duration=1):
    """
    Get data from yahoo
    duration: number of days, 0: get data from default 2010
    """
    end =  datetime.today()
    #end = '02-26-2020'
    #end = datetime.strptime(end, '%m-%d-%Y').date()
    start = end-timedelta(days=duration)    
    return web.DataReader(symbol,'yahoo',start,end)['Close'].pct_change()[1]

watchlist= ['MSFT','FB','AAPL','GOOG','CRM', #tech
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
           'ASHR','ADBE','SLAB','CDNS','SNPS','BKNG','VEEV','MCD','YUM','YUMC','NKE','UNH',
           'DIS','KO','CLX','EL','DPZ','KWEB','ITA','DIA','IHF','GXC',
           'LMT', 'SPGI', 'CME', 'COST', 'ACN', 'HON', 'CMCSA', 'PEP', 'INTU', 'EDU', 'SBUX', 'ILMN', 'NVDA', 'ISRG', 
           'XAR', 'IBUY', 'SKYY', 'VNQ','MRNA','QCOM'
           ]

iv_list = []
for symbol in watchlist:
    iv = get_iv(symbol)
    iv = float(iv.strip('%'))/100
    symbol_pct_change = get_price_df(symbol)
    add_iv = [symbol, iv, symbol_pct_change]
    iv_list.append(add_iv)
    
    #print(symbol,iv,symbol_pct_change)

iv_list = pd.DataFrame(iv_list,columns = ['Symbol','IV','Change vs. previous close'])
print(iv_list.sort_values(by = ['IV']))


# reference https://python-graph-gallery.com/193-annotate-matplotlib-chart/

import matplotlib.patches as patches
import matplotlib.pyplot as plt

x = iv_list["IV"]
y = iv_list["Change vs. previous close"]
z = iv_list["Symbol"]

fg1 = plt.figure(figsize=(15,10))
ax1 = fg1.add_subplot(111)

plt.title("IV vs. Change from last close",fontsize= 30)
plt.xlabel("IV",fontsize= 20)
plt.ylabel("Change vs. previous close",fontsize= 20)
colors =[]
for i in y:
  if i<0:
    colors.append("r")
  else:
    colors.append("g")
plt.scatter(x, y,c=colors)

for i, txt in enumerate(z):
    plt.annotate(txt, (x[i], y[i]))

plt.axvline(0.6)
plt.axhline(-0.02)

ax1.add_patch(patches.Rectangle(
(0.6, -0.02), # (x,y)
2, # width
-0.1, # height
# You can add rotation as well with 'angle'
alpha=0.3, facecolor="green", edgecolor="black", linewidth=3, linestyle='solid'
)
)

plt.savefig(my_path + '/static/iv_price.png')
print("My program took", time.time() - start_time, "to run")