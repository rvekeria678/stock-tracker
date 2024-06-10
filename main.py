from config import STOCK, COMPANY_NAME, AV_URL, NEWSAPI_URL, EMAIL_PORT, EMAIL_TIMEOUT, SHIFT_LIMIT
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os, requests, smtplib

load_dotenv()

def major_shift(stock: str):
    parameters = {
        "function":"TIME_SERIES_DAILY",
        "symbol":stock,
        "outputsize":'compact',
        "apikey":os.environ['AV_API_KEY']
    }

    response = requests.get(url=AV_URL, params=parameters, timeout=120)
    response.raise_for_status()

    stock_data = response.json()
    if 'Information' in stock_data: return True
    dates = list(stock_data['Time Series (Daily)'].keys())
    first_close = float(stock_data['Time Series (Daily)'][dates[1]]['4. close'])
    second_close = float(stock_data['Time Series (Daily)'][dates[0]]['4. close'])
    difference = abs(first_close-second_close)
    return (difference / first_close) >= SHIFT_LIMIT

if major_shift(stock=STOCK):
    parameters = {
        'q': COMPANY_NAME,
        "from":str((datetime.now()-timedelta(days=3)).date()),
        "to":str(datetime.now().date()),
        "pageSize":3,
        "language":"en",
        "apiKey":os.environ['NEWS_API_KEY']
    }
    response = requests.get(url=NEWSAPI_URL, params=parameters,timeout=120)
    response.raise_for_status()

    article_data = response.json()
    articles = article_data['articles']

    content = ''
    for article in articles:
        content += f"Headline:{article['title']}\nBrief:{article['content']}\nLink:{article['url']}\n\n"

    with smtplib.SMTP('smtp.gmail.com', port=EMAIL_PORT, timeout=EMAIL_TIMEOUT) as connection:
        connection.starttls()
        connection.login(user=os.environ['EMAIL'], password=os.environ['PASSWORD'])
        connection.sendmail(from_addr=os.environ['EMAIL'], to_addrs=os.environ['EMAIL'], msg=f"Subject:{COMPANY_NAME} : {STOCK} [Alert]\n\n{content}".encode('utf-8'))

    


