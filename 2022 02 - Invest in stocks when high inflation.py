import pandas as pd
import numpy as np
from datawrapper import Datawrapper

import config


# Get online data from Robert Shiller here: http://www.econ.yale.edu/~shiller/data.htm
# Visit my blog for more like this: www.trifektum.no


df = pd.read_excel("http://www.econ.yale.edu/~shiller/data/ie_data.xls",
                   sheet_name='Data',
                   skiprows = range(1,7),
                   usecols = "A:V",
                   header=1)

########################################
############# CLEANING #################
########################################

df.dropna(subset=['Date'], inplace=True)
df.rename(columns={"Price":"real price", "Price.1":"Real TR Price", "TR CAPE": "P/E 10"}, inplace=True)
df['Date'] = pd.to_datetime(df['Date'].mul(100).astype(int), format='%Y%m').dt.to_period('m')

df = df[["Date", "real price", "Real TR Price", "CPI", "P/E 10"]]


########################################
######### BEREGNE NYE DATA #############
########################################

df["CPI yoy"] = df["CPI"].pct_change(12) * 100

df["Aksjer Vol."] = df["Real TR Price"].pct_change()
df["Aksjer Vol."] = (df["Aksjer Vol."].rolling(12).std() * np.sqrt(12))*100

df["Infl. Vol. *"] = df["CPI"].pct_change()
df["Infl. Vol. *"] = (df["Infl. Vol. *"].rolling(12).std() * np.sqrt(12))*100 * 5

df.dropna(inplace=True)

########################################
#### FORDEL I LIKE STORE KATEGORIER ####
########################################

temp_bin_labels = list(np.arange(1, 13))

df['cpi_bins'] = pd.qcut(df['CPI yoy'],
                         q=12,
                         labels=temp_bin_labels)

df["bin_mean"] = np.nan
for i in temp_bin_labels:
    label = df[df["cpi_bins"] == i]["CPI yoy"].mean()
    df.loc[df['cpi_bins'] == i, 'bin_mean'] = label

dataofinterest = ["Infl. Vol. *", "Aksjer Vol.", "P/E 10"]
df = df.groupby(["bin_mean"])[dataofinterest].mean()
print(df)


########################################
############# GRAF #####################
########################################

dw = Datawrapper(access_token = config.datawrapper_key)

valuflation = dw.create_chart(title='Lav men positiv inflasjon gir høye aksjepriser',
                                 folder_id = '93704',
                                chart_type='d3-lines',
                                data = df.reset_index())

chart_id = config.dw_chart_ids['valuflation']

# add sources
dw.update_description(
    chart_id,
    source_name='Robert Shiller',
    source_url='http://www.econ.yale.edu/~shiller/data.htm',
    byline='www.trifektum.no')

dw.update_chart(
    chart_id,
    language='nb-NO',
)


dw.publish_chart(chart_id) #publish
