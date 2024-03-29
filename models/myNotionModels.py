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


def updatePage(pageId, headers, p, d, y, y5, pb, pe, pr, dr, roc):
    updateUrl = f"https://api.notion.com/v1/pages/{pageId}"
    updateData = {
        "properties": {
            "Pris": round(p, 2) if p is not None else None,
            "Utbytte": d if d is not None else None,
            "Yield": round(y,3) if y is not None else None,
            'Yield (MA5Y)': y5 if y5 is not None else None,
            "P/B": round(pb,2) if pb is not None else None,
            "P/E": round(pe,2) if pe is not None else None,
            'Payout Ratio (%)': round(pr,1) if pr is not None else None,
            'KcGe':round(dr,1)  if dr is not None else None,
            'ROC':round(roc,2) if roc is not None else None,
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

            quote = d["data"].get("currentPrice", None)
            financialCurrency = d["data"]["financialCurrency"]
            avgyield = d["data"].get("fiveYearAvgDividendYield", None)
            mcap = d["data"]["sharesOutstanding"]*quote
            ROE = d["data"].get("returnOnEquity", None)
            debtToEquity = d["data"].get("debtToEquity", None)

            mydataset = {
                "ticker":ticker,
                "currentPrice": quote,
                "grossMargins":d["data"].get("grossMargins", None),
                "dividend":d["data"].get("dividendRate", None),
                "dividendYield": d["data"].get("dividendYield", None),
                "fiveYearAvgDividendYield": avgyield / 100 if avgyield is not None else None, 
                "pb":d["data"].get("priceToBook", None) if financialCurrency=="NOK" else d["data"].get("priceToBook", None)/usdnok, 
                "PE":d["data"].get("trailingPE", None),
                "payoutRatio":d["data"].get("payoutRatio", None), 
                "debtToMcap":d["data"].get("totalDebt", None) / mcap if d["data"].get("totalDebt", None) is not None else None, 
                "ROC":ROE * (1-debtToEquity/100) if ROE is not None else None, 
            }
            return mydataset
        except Exception as e:
            print(f"StockData error: API not working: {ticker}: {e}")
    except Exception as e:
        print(f"StockData error {ticker}: {e}")
