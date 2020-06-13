#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 14:22:22 2020

@author: Tung
"""

# lấy data từ YF
import time
start_time = time.time()

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from pandas_datareader import data  #https://pandas-datareader.readthedocs.io/en/latest/remote_data.html
import datetime as day 
from datetime import timedelta
import matplotlib.dates as mdates

import os
my_path = os.getcwd()
print(my_path)

end_date = day.date.today()
tickers = ['MSFT','FB','AAPL','GOOG','crm'
          ,'CVS','JNJ','MRK','DIS',
           'GILD','PFE','MMM','BMY','ABBV',
           'AMD','INTC','NVDA',
           'V','MA','AXP','DFS','COF',
           'JPM','BAC','C','WFC','MS','GS','BK', 'AIG','BRK-B','HSBC',
           'WMT','AMZN','PG','UL',
           'XOM','CVX','SLB','BA',
           'TSLA','SPOT','ZM','UBER','LYFT',
           '^GSPC','GLD','TLT','HYG','SLV']
start_date = end_date - timedelta(20)
Adj_close = data.DataReader(tickers, 'yahoo',start_date, end_date)["Adj Close"].pct_change().dropna()*100
Adj_close.index = Adj_close.index.date

for i, (name, row) in enumerate(Adj_close.iterrows()):
    colors = []
    for value in row:
      if value < 0:
        colors.append('r')
      else:
        colors.append('g')
    ax = plt.subplot(20,1, i+1)
    ax = plt.bar(row.index,row, color= colors)
    plt.xticks(rotation=45)
    row.name = row.name.strftime('%A %x')    
    for idx, v in enumerate(row):
      text = str(v)
      truncated_text = text[0:4]
      plt.text(idx , v + 0.02, truncated_text)
    plt.title(row.name)
    plt.gcf().set_size_inches(15, 50)
    plt.tight_layout()
    plt.savefig(my_path + '/static/pct_change.png',bbox_inches='tight',pad_inches=0)

print("My program took", time.time() - start_time, "to run")