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
            "Pris": p,
            "Utbytte": d,
            "Yield":y,
            'Yield (MA5Y)': y5,
            "P/B": round(pb,2),
            "P/E": round(pe,2),
            'Payout Ratio (%)': round(pr,1),
            'KcGe':round(dr,1),
        }
    }
    response = requests.patch(updateUrl, json=updateData, headers=headers)
    print(response)


def StockData(ticker):
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


        return {
            "currentPrice":d["data"]["currentPrice"],
            "dividend":d["data"]["dividendRate"],
            "dividendYield": round(d["data"]["dividendYield"], 2),
            "fiveYearAvgDividendYield": d["data"]["fiveYearAvgDividendYield"] / 100 if d["data"]["fiveYearAvgDividendYield"] != None else None,
            "pb":d["data"]["priceToBook"],
            "fwdPE":d["data"]["forwardPE"],
            "payoutRatio":d["data"]["payoutRatio"],
            "debtToMcap":d["data"]["totalDebt"]/d["data"]["marketCap"],
        }
    except Exception as e:
        print(f"StockData error: {e}")
