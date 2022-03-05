import numpy as np
import pandas as pd
import yfinance as yf
from datawrapper import Datawrapper

import config
from models.my_equity_models import drawdowns


# Visit my blog for more like this: www.trifektum.no


spx = yf.download("^GSPC", group_by="ticker", period="20y")["Adj Close"].reset_index().rename(columns={'Date': 'dato', "Adj Close": "SP500"}).fillna(method="ffill")

latest = spx["dato"].max() # timestamp for siste data

data = drawdowns(250,spx,"SP500")
df = data["data"]
current = data["current"]
print(f"Siste korreksjon startet {current}")

df = df.loc[:, (df.min()<-.05)] # filtrere korreksjoner <5% for å spare lagringsplass

for col in df.loc[:, df.columns != current].columns: # stop etter bunn
    df[col] = df[col].mask(lambda x: x.shift(1).eq(df[col].min()).cummax())

print(df)


########################################
############# MAKE GRAPH 1 #############
########################################

dw = Datawrapper(access_token = config.datawrapper_key)

dw.add_data(config.dw_chart_ids['korreksjon_linje'],
            df.mul(100).reset_index())

dw.publish_chart(config.dw_chart_ids['korreksjon_linje'])

print("datawrapper linechart updated!")


########################################
############# MAKE GRAPH 2 #############
########################################

duration = pd.DataFrame()

for c in df.columns:
    d = {'index': c, 'varighet': df[c].dropna().reset_index()["count"].max()}
    duration = duration.append(d, ignore_index=True)

graphdata = df.reset_index().melt(id_vars=["count"])
graphdata["color"] = graphdata["start"] == current

df2 = graphdata.groupby(["start"])["value"].min().reset_index()
df2["value"] = df2["value"]
df2["color"] = df2["start"] == current
df2 = df2.merge(duration, how="left", left_on="start", right_on="index").drop("index", axis=1)

graphdata = df2.set_index("start")["value"]

dw.add_data(config.dw_chart_ids['korreksjon_underwater_bars'],
            graphdata.mul(100).reset_index())

dw.publish_chart(config.dw_chart_ids['korreksjon_underwater_bars'])

print("datawrapper barplot updated!")