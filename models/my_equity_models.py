import numpy as np
import pandas as pd

def drawdowns(window, dataframe, columnsname):
    window = window
    temp = dataframe.copy()
    temp["rollmax"] = temp[columnsname].rolling(window, min_periods=1).max()  # SPY_Dat['SP500'].cummax()
    temp["Daily_Drawdown"] = temp[columnsname] / temp["rollmax"] - 1.0

    temp["trend"] = np.where(temp['Daily_Drawdown'] < 0, "korrigering", np.nan)
    temp['count'] = temp.groupby((temp['trend'] != temp['trend'].shift(1)).cumsum()).cumcount()
    temp.loc[temp['trend'] != temp["trend"].shift(1), 'start'] = temp["dato"]
    temp["start"].ffill(inplace=True)

    current = temp["start"].max().strftime("%B %Y")  # lagre merkelapp på nåværend korreksjon
    temp["start"] = temp["start"].dt.strftime("%B %Y")  # endre datofortmat så det blir lettere å lese

    temp = temp[temp["trend"] == "korrigering"].groupby(["count", "start"])["Daily_Drawdown"].min().reset_index()
    temp = pd.pivot_table(temp, values='Daily_Drawdown', index=["count"], columns=['start'])

    print("Drawdowns calculated! Flink gutt!")

    return {"data": temp,
            "current": current}