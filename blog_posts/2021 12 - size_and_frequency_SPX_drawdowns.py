import pandas as pd
import yfinance as yf

from models.my_equity_models import drawdowns


# Visit my blog for more like this: www.trifektum.no


d = yf.download("^GSPC", group_by="ticker", period="max")["Adj Close"].reset_index().rename(columns={'Date': 'dato', "Adj Close": "SP500"}).fillna(method="ffill")

df = drawdowns(250,d,"SP500")["summarytable"]

print(df)

