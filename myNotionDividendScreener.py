import numpy as np
import os
from models.myNotionModels import readDatabase, getPageTitle, StockData, updatePage

#My medium article: https://medium.datadriveninvestor.com/creating-an-automated-stock-screener-in-notion-with-python-43df78293bb4
#stockapi: https://rapidapi.com/asepscareer/api/yahoo-finance97/

token = os.environ['NOTION-DIVIDEND-SCREENER']
databseID = os.environ["NOTION-DIVIDEND-DB-ID"]


headers = {
    "Accept": "application/json",
    "Notion-Version": "2022-06-28",
    "Authorization": "Bearer " +token
}


notionDatabase = readDatabase(databseID, headers)


for i in np.arange(len(notionDatabase["data"]["results"])):
    try:
        #get pages (rows) in datbase:
        pageId = notionDatabase["data"]["results"][i]["id"]
        pageTitle = getPageTitle(pageId, headers)

        # get data from Yahoo Finance:
        d = StockData(pageTitle)

        #update Notion database:
        updatePage(pageId, headers,
                   p=d["currentPrice"],
                   d=d["dividend"],
                   y=d["dividendYield"],
                   y5=d["fiveYearAvgDividendYield"],
                   pb=d["pb"],
                   pe=d["fwdPE"],
                   pr=d["payoutRatio"],
                   dr=d["debtToMcap"]
                  )

    except Exception as e:
        print(e)