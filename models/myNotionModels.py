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

def get_stock_data_yfinance(ticker, usdnok):
    #alternative to fastAPI
    stock = yf.Ticker(ticker)
    info = stock.info

    current_price = info['regularMarketPrice']
    gross_margin = info['grossMargins']
    dividend = info['dividendRate']
    dividend_yield = info['dividendYield']
    avg_dividend_yield_5y = info['fiveYearAvgDividendYield']
    pb = info['priceToBook']
    trailing_pe = info['trailingPE']
    payout_ratio = info['payoutRatio']
    total_debt = info['totalDebt']
    mcap = info["sharesOutstanding"]*current_price

    return {
        'currentPrice': current_price,
        'grossMargins': gross_margin,
        'dividend': dividend,
        'dividendYield': dividend_yield,
        'fiveYearAvgDividendYield': avg_dividend_yield_5y,
        'pb': pb if financialCurrency=="NOK" else pb/usdnok,,
        'PE': trailing_pe if trailing_pe != None else None,
        'payoutRatio': payout_ratio,
        'debtToMcap': total_debt
    }
    
    
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
                "fiveYearAvgDividendYield": dividend_yield / 100 if dividend_yield is not None else None, 
                "pb":d["data"].get("priceToBook", None) if financialCurrency=="NOK" else d["data"].get("priceToBook", None)/usdnok, 
                "PE":d["data"].get("trailingPE", None)
                "payoutRatio":d["data"].get("payoutRatio", None), 
                "debtToMcap":d["data"].get("totalDebt", None), 
                "ROC":ROE * (1-debtToEquity/100) if ROE is not None else None, 
            }

            return mydataset
        except Exception as e:
            print(f"StockData error: API not working: {ticker}: {e}")
    except Exception as e:
        print(f"StockData error {ticker}: {e}")
