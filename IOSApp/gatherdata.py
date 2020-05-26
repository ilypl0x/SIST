from bs4 import BeautifulSoup
import requests
import json

# def get_ticker_pricev2(ticker):

#     price_code = 'span[data-reactid="32"]'
#     name_code = 'h1[data-reactid="7"]'
#     close_code = 'span[data-reactid="35"]'

#     url = 'https://in.finance.yahoo.com/quote/' + ticker
#     session = requests_html.HTMLSession()
#     r = session.get(url)
#     soup = BeautifulSoup(r.content, 'lxml')
#     price_location = soup.find("div", {"id":"Lead-3-QuoteHeader-Proxy"})

#     close = price_location.select(close_code)[0].text
#     name = price_location.select(name_code)[0].text
#     curr_price = float(price_location.select(price_code)[0].text)

#     return close,name,curr_price


def get_ticker_price(ticker):

    price_code = 'span[data-reactid="14"]'
    # name_code = 'h1[data-reactid="7"]'
    # close_code = 'span[data-reactid="18"]'

    url = 'https://in.finance.yahoo.com/quote/' + ticker
    html_page = requests.get(url).content
    soup = BeautifulSoup(html_page, 'html.parser')
    price_location = soup.find("div", attrs={"id":"Col1-2-QuoteHeader-Proxy"})

    # close = price_location.select(close_code)[0].text
    # name = price_location.select(name_code)[0].text
    curr_price = float(price_location.select(price_code)[0].text)

    # return close,name,curr_price
    return curr_price


def get_symbol(symbol):
    try:
        url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(symbol)

        result = requests.get(url).json()


        for x in result['ResultSet']['Result']:
            if x['symbol'] == symbol:
                return x['name']
    except:
            return None

class AlphaVantage():

    def __init__(self):
        self.apiKey = 'MKGNASVKLJ2I9C77'
        self.url = "https://www.alphavantage.co/query"
        self.payload = {"function": "TIME_SERIES_INTRADAY",
                    "symbol": "",
                    "interval": "1min",
                    "apikey": self.apiKey}

    def getStockPrice(self,symbol):

        self.payload['symbol'] = symbol
        av_api = json.loads(requests.get(self.url, params=self.payload).text)

        all_value = av_api['Time Series (1min)'].values()
        iter_value = iter(all_value)
        first_value = next(iter_value)
        close = float(first_value['4. close'])

        return close
        

class FinnhubIO():

    def __init__(self):
        self.token = 'br65e2frh5rdamtp6r9g'
        self.url = "https://finnhub.io/api/v1/quote"
        self.payload = {"symbol": "",
                    "token": self.token}

    def getStockPrice(self,symbol):

        self.payload['symbol'] = symbol
        fio_api = json.loads(requests.get(self.url, params=self.payload).text)

        close = float(fio_api['c'])

        return close
        





# if __name__ in "__main__":
#     print(get_ticker_price("JPM"))
