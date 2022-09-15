import numpy as np
import pandas as pd


def days_to_new_high(df, peak_date):
    try:
        t = df[df.dato >= peak_date]  # serie as of peak
        localMax = t.rollmax.iloc[0]  # peak value
        maxpos = t.rollmax.index[0]  # peak index position
        try:
            ndays = t[t.SP500 > localMax].index[0] - maxpos  # rows (days) between peak and new high
        except Exception as e:
            ndays = np.nan
            print(e)
        return ndays
    except Exception as e:
        print(e)


def drawdowns(window, dataframe, columnsname):
    from fractions import Fraction
    try:
        window = window
        temp = dataframe.copy()
        temp["rollmax"] = temp[columnsname].rolling(window, min_periods=1).max()  # SPY_Dat['SP500'].cummax()
        temp["Daily_Drawdown"] = temp[columnsname] / temp["rollmax"] - 1.0

        temp["trend"] = np.where(temp['Daily_Drawdown'] < 0, "korrigering", np.nan)
        temp['count'] = temp.groupby((temp['trend'] != temp['trend'].shift(1)).cumsum()).cumcount()
        temp.loc[temp['trend'] != temp["trend"].shift(1), 'start'] = temp["dato"]
        temp["start"].ffill(inplace=True)

        datarange = int(temp.dato.max().year - temp.dato.min().year)  # find years of data

        # Group data by drawdown in new df:
        grouped = temp[temp["trend"] == "korrigering"].groupby(["start"]).agg({"rollmax": "max",
                                                                               'Daily_Drawdown': 'min',
                                                                               'count': 'max'}).rename(
            columns={"rollmax": "peak_value",
                     "Daily_Drawdown": "max_drawdown",
                     "count": "n days peak-trough"})

        grouped.reset_index(inplace=True)
        grouped['days_to_new_high'] = grouped.start.apply(
            lambda x: days_to_new_high(temp, x))  # use function to calculate days to new high
        grouped["start"] = grouped["start"].dt.strftime("%B %Y")  # endre datofortmat så det blir lettere å lese

        # label the size of drawdown:
        grouped["bin"] = pd.cut(grouped['max_drawdown'],
                                bins=[-1, -.5, -.4, -.3, -.2, -.15, -.1, -.05, 0],
                                labels=["-50% eller mer", "-40% eller mer", "-30% eller mer", "-20% eller mer",
                                        "-15% eller mer", "-10% eller mer", "-5% eller mer", "mindre enn 5%"],
                                )
        summarytable = grouped.groupby(["bin"]).agg({"max_drawdown": "count",
                                                     "n days peak-trough": "mean",
                                                     'days_to_new_high': "mean",
                                                     }).reset_index()

        summarytable['fraction'] = summarytable.apply(lambda x: Fraction(x.max_drawdown / datarange).limit_denominator(),
                                                      axis=1)

        print("Drawdowns calculated! Flink gutt!")
        #print(summarytable)

        current = temp["start"].max().strftime("%B %Y")  # lagre merkelapp på nåværend korreksjon
        temp["start"] = temp["start"].dt.strftime("%B %Y")  # endre datofortmat så det blir lettere å lese

        temp = temp[temp["trend"] == "korrigering"].groupby(["count", "start"])["Daily_Drawdown"].min().reset_index()
        temp = pd.pivot_table(temp, values='Daily_Drawdown', index=["count"], columns=['start'])

        return {"data": temp,
                "current": current,
                "list_of_drawdowns": grouped,
                "summarytable": summarytable}

    except Exception as e:
        print(e)