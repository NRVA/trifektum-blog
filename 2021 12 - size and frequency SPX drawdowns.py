import pandas as pd
import yfinance as yf

from models.my_equity_models import drawdowns


# Visit my blog for more like this: www.trifektum.no


d = yf.download("^GSPC", group_by="ticker", period="max")["Adj Close"].reset_index().rename(columns={'Date': 'dato', "Adj Close": "SP500"}).fillna(method="ffill")

df = drawdowns(250,d,"SP500")["data"]
df = pd.DataFrame(data=df.min(axis=0), columns=['drawdown'])

labels = ["-40% eller mer", "-30% eller mer", "-20% eller mer", "-15% eller mer", "-10% eller mer", "-5% eller mer"]

df["bin"] = pd.cut(df['drawdown'],
                      bins=[-.5, -.4, -.3, -.2, -.15, -.1, -.05],
                      labels=labels,
                      )
df = df.dropna()

resultat = df.groupby(["bin"]).count()["drawdown"].cumsum()

print(resultat)

