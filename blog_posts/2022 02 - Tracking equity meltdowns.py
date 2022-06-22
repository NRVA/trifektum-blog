import numpy as np
import pandas as pd
import yfinance as yf
from datawrapper import Datawrapper
import os

from models.my_equity_models import drawdowns

datawrapper_key = os.environ['DATAWRAPPER-KEY']
# Visit my blog for more like this: www.trifektum.no


spx = yf.download("^GSPC", group_by="ticker", period="20y")["Adj Close"].reset_index().rename(columns={'Date': 'dato', "Adj Close": "SP500"}).fillna(method="ffill")

latest = spx["dato"].max() # timestamp for siste data

data = drawdowns(250,spx,"SP500")
current = data["current"]
df = data["data"]
df = df.loc[:, (df.min()<-.05)] # filtrere korreksjoner <5% for å spare lagringsplass

for col in df.loc[:, df.columns != current].columns: # stop etter bunn
    df[col] = df[col].mask(lambda x: x.shift(1).eq(df[col].min()).cummax())

df2 = data["list_of_drawdowns"]

print(f"Siste korreksjon startet {current}")



########################################
############# MAKE GRAPH 1 #############
########################################

try:
    dw = Datawrapper(access_token = datawrapper_key)

    dw.add_data("LAsCJ", df.mul(100).reset_index())
    dw.publish_chart("LAsCJ")

    print("datawrapper linechart updated!")
except Exception as e:
    print("datawrapper linjegraf korreksjoner feilet!")
    print(e)


########################################
############# MAKE GRAPH 2 #############
########################################

df2 = df2[(df2["bin"] != "mindre enn 5%")]
df2['color'] = df2.start.apply(lambda x: False if x != current else True)

graphdata = df2.set_index("start")["max_drawdown"]

try:
    dw.add_data("50EXY", graphdata.mul(100).reset_index())
    dw.publish_chart("50EXY")

    print("datawrapper barplot updated!")
except Exception as e:
    print("datawrapper drawdown døyler feilet!")
    print(e)