import pandas as pd
import numpy as np
import chart_studio
import chart_studio.plotly as py
import plotly.graph_objects as go

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

cols = ["#4582ec", "#f0ad4e", "#02b875"]
xs = plotdata.index/100

fig = go.Figure()

color_n = 0

for c in dataofinterest:
    fig.add_trace(go.Scatter(
            x=xs, 
            y=plotdata[c]["mean"],
            mode='lines',
            name = str(c),
            line=dict(width=2, color=cols[color_n]),
    ))
    
    color_n += 1
    
fig.update_layout(showlegend=False,
                  xaxis=dict(title="Inflasjon (år-over-år)",
                            showline=True,
                            showgrid=False,
                            showticklabels=True,
                            tickformat= '%',
                            #tickangle=-90,
                            linecolor="rgba(150,150,150,0.8)",
                            linewidth=1,
                            ticks="outside",
                            tickfont=dict(family="Arial", size=12, color="#6c757d"),
                            titlefont=dict(family="Arial", size=12, color="rgb(150,150,150)"),),
                  yaxis=dict(title="Gjennomsnittlig P/E10 og volatilitet",
                             titlefont=dict(family="Arial", size=12, color="rgb(150,150,150)"),
                            side="left",
                             linewidth=1,
                            linecolor="rgba(150,150,150,0.8)",
                            showgrid=False,
                            showticklabels=True,
                            tickfont=dict(family="Arial", size=12, color="rgba(150,150,150,0.6)")),
                  plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor='rgba(0, 0, 0, 0)',
                  margin=dict(l=0, r=0, t=0, b=0),
                  hovermode = "x"
                 )

fig.update_xaxes(showspikes=True, spikecolor="rgba(150,150,150,0.8)", spikesnap="cursor", spikemode="across"),
fig.update_yaxes(showspikes=True, spikecolor="rgba(150,150,150,0.5)", spikethickness=2)


fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide',
                 spikedistance=1000, hoverdistance=100,
                 )


fig.show()
