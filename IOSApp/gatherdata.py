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

# if __name__ in "__main__":
#     print(get_ticker_price("JPM"))
