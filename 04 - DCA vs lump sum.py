df = pd.read_excel("div/spx.xlsx", thousands=',')

# 3 month rate: https://fred.stlouisfed.org/series/TB3MS
# pengemarkedsrente + 2% margin
    
mth_in = 1000
df["bank"] = 0
df["dca"] = 0
r = .05

for row in range(1, len(df)):
    mth_chg = df["Adj Close**"].iloc[row]/df["Adj Close**"].iloc[row-1]
    cv = df["dca"].iloc[row-1] * mth_chg
    df["dca"].iloc[row] = cv + mth_in
    
    df["bank"].iloc[row] = df["bank"].iloc[row-1]*(1+(r/12)) + mth_in
    
df
