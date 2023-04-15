import requests
import os

def readDatabase(databseID, headers):
    readUrl = f"https://api.notion.com/v1/databases/{databseID}/query"

    response = requests.post(readUrl, headers=headers)
    print(f"readDatabase status: {response.status_code}")
    data = response.json()
    properties = data["results"][0]["properties"]

    return {"data": data,
            "properties": properties}


def getPageTitle(pageId, headers):
    propUrl = f"https://api.notion.com/v1/pages/{pageId}/properties/title"
    try:
        response = requests.get(propUrl, headers=headers)
        data = response.json()
        title = data["results"][0]["title"]["plain_text"]
        return title
    except Exception as e:
        print(f"getPageTitle error: {e}: {propUrl}")


def updatePage(pageId, headers, p, d, y, y5, pb, pe, pr, dr):
    updateUrl = f"https://api.notion.com/v1/pages/{pageId}"
    updateData = {
        "properties": {
            "Pris": round(p, 2),
            "Utbytte": d,
            "Yield": round(y,3),
            'Yield (MA5Y)': y5,
            "P/B": round(pb,2),
            "P/E": round(pe,2),
            'Payout Ratio (%)': round(pr,1),
            'KcGe':round(dr,1),
        }
    }
    response = requests.patch(updateUrl, json=updateData, headers=headers)
    print(response)


def FXfetcher():
    try:
        url = "https://yahoo-finance97.p.rapidapi.com/price"
        rapidApi = os.environ["RAPIDAPI"]

        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "X-RapidAPI-Key": rapidApi,
            "X-RapidAPI-Host": "yahoo-finance97.p.rapidapi.com"
        }

        payload = "symbol=NOK%3DX&period=1d"
        response = requests.request("POST", url, data=payload, headers=headers)
        data = response.json()
        close = data["data"][0]["Close"]
        print(close)
        return close
    except Exception as e:
        print(f"FXfetcher klarte ikke hente valutakurs: returnerer usdnok=10 som workaround!: {e}")
        return 10

"""
def StockQuote(ticker):
    try:
        url = "https://yahoo-finance97.p.rapidapi.com/price"
        rapidApi = os.environ["RAPIDAPI"]

        payload = f"symbol={ticker}&period=1d"
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "X-RapidAPI-Key": rapidApi,
            "X-RapidAPI-Host": "yahoo-finance97.p.rapidapi.com"
        }

        response = requests.request("POST", url, data=payload, headers=headers)
        data = response.json()
        quote = data["data"][0]["Close"]
        return quote
    except Exception as e:
        print(f"StockQuote klarte ikke hente aksjeprisen: {e}")
        return None
"""
    
    
def StockData(ticker, usdnok):
    try:
        url = "https://yahoo-finance97.p.rapidapi.com/stock-info"
        payload = f"symbol={ticker}"
        rapidApi = os.environ["RAPIDAPI"]

        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "X-RapidAPI-Key": rapidApi,
            "X-RapidAPI-Host": "yahoo-finance97.p.rapidapi.com"
        }
        try:
            response = requests.request("POST", url, data=payload, headers=headers)
            d = response.json()

            quote = d["data"]["currentPrice"]
            financialCurrency = d["data"]["financialCurrency"]
            mcap = d["data"]["sharesOutstanding"]*quote

            mydataset = {
                "ticker":ticker,
                "currentPrice": quote,
                "grossMargins":d["data"]["grossMargins"],
                "dividend":d["data"]["dividendRate"],
                "dividendYield": d["data"]["dividendYield"],
                "fiveYearAvgDividendYield": d["data"]["fiveYearAvgDividendYield"] / 100 if d["data"]["fiveYearAvgDividendYield"] != None else None,
                "pb":d["data"]["priceToBook"] if financialCurrency=="NOK" else d["data"]["priceToBook"]/usdnok,
                "PE":d["data"]["trailingPE"] if d["data"]["trailingPE"] != None else None,
                "payoutRatio":d["data"]["payoutRatio"],
                "debtToMcap":d["data"]["totalDebt"]/mcap,
            }

            return mydataset
        except Exception as e:
            print(f"StockData error: API not working: {ticker}: {e}")
    except Exception as e:
        print(f"StockData error {ticker}: {e}")
