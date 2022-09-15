from fredapi import Fred
import chart_studio.plotly as py
import chart_studio
import numpy as np
import pandas as pd
import os
from pandas.tseries.offsets import MonthEnd
import plotly.graph_objects as go
import plotly.express as px
import datetime

#if int(datetime.datetime.now().strftime("%d")) == 15:
try:
    chart_studio.tools.set_credentials_file(username=os.environ['CHARTSTUDIO-USER'], 
                                            api_key=os.environ['CHARTSTUDIO-KEY'])
    chart_studio.tools.set_config_file(world_readable=True, sharing='public')
    fred = Fred(api_key=os.environ['FRED-API-KEY'])

    df = fred.get_series_all_releases('CPILFESL') #Consumer Price Index for All Urban Consumers: All Items Less Food and Energy in U.S. City Average
    latest_cpi = df["date"].iloc[-1]

    df = df.set_index("realtime_start").resample("M").last().reset_index()
    df["value"] = df["value"].pct_change(12)*100
    df["6m_mean_cpi"] = df["value"].rolling(6).mean()
    df["10y_mean_cpi"] = df["value"].rolling(12*10).mean()
    df["cpi_paradigme"] = np.where(df['6m_mean_cpi'] < df["10y_mean_cpi"], "avtagende", "aksellererende")
    df["Divergence (bp)_cpi"] = (df["6m_mean_cpi"]-df["10y_mean_cpi"])

    baa = fred.get_series('DBAA').reset_index().rename(columns={'index': 'dato', 0: "BAA yield"})
    baa = baa.set_index("dato").resample("M").last().reset_index()

    df = pd.merge(df.assign(grouper=df['realtime_start'].dt.to_period('M')),
                 baa.assign(grouper=baa['dato'].dt.to_period('M')),
                 how='left', on='grouper')
    df["BAA real yield"] = df["BAA yield"] - df["10y_mean_cpi"]
    df["activity_paradigme"] = np.where(df['BAA real yield'] <= 5, "aksellererende", "avtagende")
    df["month"] = df["date"].dt.strftime("%B %Y")
    print("GaveKal model: datacollection OK!")
except Exception as e:
    print(f"GaveKal model: datacollection failed: {e}")


    ##########################################
    ################## MATRIX ################
    ##########################################

try:
    hover_data = {"activity_paradigme": True, "cpi_paradigme": True, "BAA real yield": False,
                      "Divergence (bp)_cpi": False, "month": True}

    annot = [
            dict(x=7.5, y=2.5, xref="x", yref="y", text="TILTAGENDE INFLASJON<br>OG LAV AKTIVITET", xanchor="center",
                 showarrow=False, font=dict(color="white", size=16, )),
            dict(x=7.5, y=-2.5, xref="x", yref="y", text="AVTAGENDE INFLASJON<br>OG LAV AKTIVITET", xanchor="center",
                 showarrow=False, font=dict(color="white", size=16)),
            dict(x=2.5, y=2.5, xref="x", yref="y", text="TILTAGENDE INFLASJON<br>OG HØY AKTIVITET", xanchor="center",
                 showarrow=False, font=dict(color="white", size=16)),
            dict(x=2.5, y=-2.5, xref="x", yref="y", text="AVTAGENDE INFLASJON<br>OG HØY AKTIVITET", xanchor="center",
                 showarrow=False, font=dict(color="white", size=16)),
            dict(x=1, y=0, xref="paper", yref="paper", text="www.trifektum.no", xanchor="right", yanchor="bottom",
                 align="right", showarrow=False, font=dict(color='rgba(122, 122, 122, 0.6)', size=10))]

    fig = px.scatter(df.tail(6), x="BAA real yield", y="Divergence (bp)_cpi",
                         # range_y=[-5,5], range_x=[10,0],
                         width=600, height=600,
                         color_discrete_sequence=["#fc5661"],
                         hover_data=hover_data,
                         labels={"activity_paradigme": "Økonomisk aktivitet", "cpi_paradigme": "Inflasjonspress",
                                 "month": "Dato"},
                         title="<b>Per " + df["dato"].iloc[-1].strftime("%B %Y") + " er USA i ett regime med " +
                               df["cpi_paradigme"].iloc[-1] + " inflasjonspress <br>og med forholdene til rette for " +
                               df["activity_paradigme"].iloc[-1] + " økonomisk aktivitet",
                         )

    fig.update_traces(mode="lines",
                          # hovertemplate='%{activity_paradigme}',
                          line=dict(shape='spline'))

    fig.add_trace(go.Scatter(x=list(df[['BAA real yield']].iloc[-1]),
                                 y=list(df[['Divergence (bp)_cpi']].iloc[-1]),
                                 mode='markers', hoverinfo="skip",
                                 marker=dict(color='#fc5661', size=12, ), showlegend=False))

    fig.update_layout(
            margin=dict(l=0, r=0, t=90, b=0),
            paper_bgcolor='rgba(0, 0, 0, 0)',
            plot_bgcolor='rgba(122, 122, 122, 0.2)',
            xaxis={'showgrid': False, 'zeroline': False, "showticklabels": False, "title": ""},
            yaxis={'showgrid': False, 'zeroline': False, "showticklabels": False, "title": ""},
            annotations=annot, separators=",", font_family="sans-serif",
        )

    fig.add_vline(x=5, line_width=10, line_color="white", layer='below', )
    fig.add_hline(y=0, line_width=10, line_color="white", layer='below', )
    py.plot(fig, filename='investeringsmatrisen.html', auto_open=False, link=True)

except Exception as e:
    print(f"GaveKal model: investeringsmatrise failed: {e}")


    #############################################
    ################## INFLATION ################
    #############################################

try:
    fig = px.area(df, x="dato", y="cpi", color_discrete_sequence=["#fc5661"], range_x=[datetime.datetime(1958, 3, 1),df["realtime_start"].iloc[-1]])

    fig.add_trace(go.Scatter(x=df["realtime_start"],
                            y=df["10y_mean_cpi"],
                            mode='lines',
                            name="10 år gjennomsnitt",
                            hoverinfo="name",
                            showlegend=False,
                            line=dict(
                                color="blue",
                                width=1.5, dash='dash'
                                   )))

    # function to set background color for a
    # specified variable and a specified level
    def highLights(fig, variable, level, mode, fillcolor, layer):
        if mode == 'above':
            m = df[variable]==level
        if mode == 'below':
            m = df[variable].lt(level)
        df1 = df[m].groupby((~m).cumsum())['dato'].agg(['first','last'])

        for index, row in df1.iterrows():
            #print(row['first'], row['last'])
            fig.add_shape(type="rect",
                            xref="x",
                            yref="paper",
                            x0=row['first'],
                            y0=0,
                            x1=row['last'],
                            y1=1,
                            line=dict(color="rgba(0,0,0,0)",width=3,),
                            fillcolor=fillcolor,
                            layer=layer)
        return(fig)

    fig = highLights(fig = fig, variable = 'cpi_paradigme', level = "aksellererende", mode = 'above',
                   fillcolor = 'rgba(122, 122, 122, 0.3)', layer = 'below')

    fig.update_layout(showlegend=False,
                     #hoverlabel = dict(bgcolor = "#aab2bd"),
                      xaxis=dict(title="",
                                showline=True,
                                showgrid=False,
                                showticklabels=True,
                                linecolor="rgba(204,204,204, 0.7)",
                                linewidth=2,
                                ticks="outside",
                                rangeslider=dict(visible=True, range=[-120,1]),
                                tickfont=dict(family="Arial", size=12, color="rgb(150,150,150)"),
                                titlefont=dict(family="Arial", size=12, color="rgb(150,150,150)"),),
                      yaxis=dict(title="",
                                side="right",
                                showticklabels=True,
                                showgrid=False,
                                tickfont=dict(family="Arial", size=12, color="rgba(150,150,150,0.6)")),
                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor='rgba(0, 0, 0, 0)',
                      margin=dict(l=0, r=0, t=0, b=0),
                     )

    annotations = []
    annotations.append(dict(xref="paper", yref="paper", x=0.0, y=1.17,
                           xanchor="left", yanchor="bottom",
                           #text="Handleregel for inflasjon",
                           font=dict(family="Arial",
                                    size=22,
                                    color="rgb(37,37,37)"),
                           showarrow=False))

    annotations.append(dict(xref="paper", yref="paper", x=1, y=0,
                           xanchor="right", yanchor="bottom", align="right",
                           text="Sist oppdatert per "+ df["dato"].iloc[-1].strftime("%B %Y")+", som gav oss inflasjonsdata fra "+ latest_cpi.strftime("%B %Y"),
                           font=dict(family="Arial",
                                    size=12,
                                    color="rgba(82,82,82,0.9)"),
                           showarrow=False,))

    fig.update_layout(annotations=annotations)

    # Add range slider
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(visible=True),
            type="date"
        )
    )
    print("inflation plot OK!")
    #py.plot(fig, filename='investeringsmatrisen_inflasjon.html', auto_open=False, link=True)


    ##########################################
    ################## GROWTH ################
    ##########################################

    fig = px.area(df, x="dato", y="BAA real yield", color_discrete_sequence=["#fc5661"], range_x=[datetime.datetime(1986, 1, 1),df["dato"].iloc[-1]])

    fig.update_layout(shapes=[dict(type="line",
                         x0=datetime.datetime(1958, 3, 1), y0=5,
                         x1=df["dato"].iloc[-1], y1=5,
                         line=dict(color="blue", dash='dash', width=1.5), layer='below',)])

    fig = highLights(fig = fig, variable = 'activity_paradigme', level = "avtagende", mode = 'above',
                   fillcolor = 'rgba(122, 122, 122, 0.3)', layer = 'below')

    fig.update_layout(showlegend=False,
                      xaxis=dict(title="",
                                showline=True,
                                showgrid=False,
                                showticklabels=True,
                                linecolor="rgba(204,204,204, 0.7)",
                                linewidth=2,
                                ticks="outside",
                                tickfont=dict(family="Arial", size=12, color="rgb(150,150,150)"),
                                titlefont=dict(family="Arial", size=12, color="rgb(150,150,150)"),),
                      yaxis=dict(title="",
                                side="right",
                                showticklabels=True,
                                showgrid=False,
                                tickfont=dict(family="Arial", size=12, color="rgba(150,150,150,0.6)")),
                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor='rgba(0, 0, 0, 0)',
                      margin=dict(l=0, r=0, t=0, b=0),
                     )
    annotations = []

    annotations.append(dict(xref="paper", yref="paper", x=1, y=0,
                           xanchor="right", yanchor="bottom", align="right",
                           text="Sist oppdatert per "+ df["dato"].iloc[-1].strftime("%B %Y"),
                           font=dict(family="Arial",
                                    size=12,
                                    color="rgba(82,82,82,0.9)"),
                           showarrow=False))

    fig.update_layout(annotations=annotations)
    py.plot(fig, filename='investeringsmatrisen_aktivitet.html', auto_open=False, link=True)
except Exception as e:
    print(e)
