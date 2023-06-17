import importlib
from datetime import datetime
#from dotenv import load_dotenv

#load_dotenv() 

weekdaynum = datetime.today().weekday()

#dd = importlib.import_module('blog_posts.2021 12 - size_and_frequency_SPX_drawdowns')
korreksjon_i_aksjemarkedene = importlib.import_module("blog_posts.2022 02 - Tracking equity meltdowns") if datetime.today().weekday() <= 4 else print("No new stock data to get today") # only run on weekdays
#gavekal_model = importlib.import_module("blog_posts.2020 10 - strukturelle_skift_med_gavekal-modellen")
notion_dividendscreener = importlib.import_module("myNotionDividendScreener") if weekdaynum==5 else print(f"Today is day {weekdaynum}: No screener set up for today") # only screen on fridays



if __name__ == '__main__':
    #korreksjon_i_aksjemarkedene
    notion_dividendscreener
    #gavekal_model
