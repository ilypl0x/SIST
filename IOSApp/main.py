import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button, ButtonBehavior
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Rectangle, Color, Line
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.dropdown import DropDown
import requests
import json
import re
import concurrent.futures
from firebase import Firebase
from detailbanner import DetailBanner
from gatherdata import get_symbol,get_ticker_price

class HomeScreen(Screen):
    pass

class ImageButton(ButtonBehavior, Image):
    pass

class LabelButton(ButtonBehavior, Label):
    pass

class SettingsScreen(Screen):
    pass

class LoginScreen(Screen):
    pass

class InputScreen(Screen):
    pass

class SetPopup(Popup):
    pass



kv = Builder.load_file("main.kv")

class WindowsApp(App):

    def build(self):
        self.firebase = Firebase()
        return kv

    def on_start(self):

        try:
            #Try to read the persisting sign in credentials
            with open("refresh_token.txt", 'r') as f:
                refresh_token = f.read()

            self.id_token, self.local_id = self.firebase.exchange_refresh_token(refresh_token)
            self.update()
            self.change_screen("home_screen")

        except Exception as e:
            print("Error is:{}".format(e))
            pass
            
    def convert_to_dict(self):
        raw_data = {}
        result = requests.get("https://investmentsummary-94034.firebaseio.com/%s.json?auth=%s" % (self.local_id, self.id_token))
        data = json.loads(result.content.decode())
        buy_keys = data['buy'].keys()
        buy = data['buy']
        for buy_key in buy_keys:
            stock_purchase = buy[buy_key]
            vwap = 0
            stock = stock_purchase["ticker"]; price = float(stock_purchase["price"]); qty=int(stock_purchase["qty"])
            if stock not in raw_data.keys():
                raw_data[stock] = {'price': [price] ,
                                    'qty': [qty],
                                    'total': qty,
                                    'vwap' : vwap
                                    }
            else:
                raw_data[stock]['price'].append(price)
                raw_data[stock]['qty'].append(qty)
                raw_data[stock]['total'] += qty
        for stock in raw_data:
            sum_of_price = 0
            for i in range(len(raw_data[stock]['price'])):
                cost = raw_data[stock]['price'][i]*raw_data[stock]['qty'][i]
                sum_of_price += cost
            raw_data[stock]['vwap'] = sum_of_price/raw_data[stock]['total']

        ticker_list  = raw_data.keys()
        total_dict  = {'total':
                            {'orig_total': 0,
                            'new_total': 0,
                            'close': '',
                            'percent': 0,
                            'pnl': 0}
                            }           

        def calc_percent(new,old):
            percent = round(((new-old)/old)*100,2)
            return percent

        def float_to_money(value):
            money = '${:,.2f}'.format(value)
            return money

        def vwap_edit(ticker):
            close,name, curr_price = get_ticker_price(ticker)
            raw_data[ticker]['curr_price'] = curr_price
            raw_data[ticker]['name'] = name
            raw_data[ticker]['orig_total'] = raw_data[ticker]['total']* raw_data[ticker]['vwap']
            raw_data[ticker]['new_total'] = raw_data[ticker]['total']* raw_data[ticker]['curr_price']  
            raw_data[ticker]['percent'] = calc_percent(raw_data[ticker]['new_total'], raw_data[ticker]['orig_total'])
            
            total_dict['total']['orig_total'] += raw_data[ticker]['orig_total']
            total_dict['total']['new_total'] += raw_data[ticker]['new_total']
            total_dict['total']['close'] = close    
        with concurrent.futures.ThreadPoolExecutor() as executor:
                [executor.submit(vwap_edit,ticker) for ticker in ticker_list]
        total_dict['total']['pnl'] = total_dict['total']['new_total'] - total_dict['total']['orig_total']
        total_dict['total']['percent'] = calc_percent(total_dict['total']['new_total'],total_dict['total']['orig_total'])
        total_dict['total']['new_total'] = float_to_money(total_dict['total']['new_total'])
        total_dict['total']['orig_total'] = float_to_money(total_dict['total']['orig_total'])
        return total_dict,raw_data            
        
    def update(self):

        total_dict, final_data = self.convert_to_dict()
        post_request = requests.patch("https://investmentsummary-94034.firebaseio.com/%s.json?auth=%s" %(self.local_id,self.id_token),
            data = json.dumps(total_dict))
        #Update total pnl for portfolio
        pnl_label = self.root.ids['home_screen'].ids['pnl_label']
        if total_dict['total']['pnl'] > 0:
            pnl_label.text = "Profit: \n" + '${:,.2f}'.format(total_dict['total']['pnl'])
        else:
            pnl_label.text = "Loss: \n" + '${:,.2f}'.format(total_dict['total']['pnl'])

        # Update total Percent for portfolio
        percent_label = self.root.ids['home_screen'].ids['percent_label']
        if total_dict['total']['percent'] > 0:
            percent_label.text = "+ " + str(total_dict['total']['percent'])+ '%'
        else:
            percent_label.text = str(total_dict['total']['percent']) +'%'

        #Update last updated time 
        asof_label = self.root.ids['home_screen'].ids['asof_label']
        raw_asof = total_dict['total']['close'].split('.')[0] 
        asof_label.text =  "Updated: \n" + re.split(r'(^[^\d]+)',raw_asof)[-1]

        #Update total invested 
        totalinvest_label = self.root.ids['home_screen'].ids['totalinvest_label']
        totalinvest_label.text = "Total Invested: \n" + total_dict['total']['orig_total']     

        detail_grid = self.root.ids['home_screen'].ids['detail_grid']  
        detail_grid.clear_widgets()  
        for k,v in final_data.items():
            W = DetailBanner(ticker=k,purchase_price=v['vwap'],curr_price=v['curr_price'],percent=v['percent'])
            detail_grid.add_widget(W)

    def change_screen(self, screen_name):
        #get the screen manager from the kv file
        screen_manager = self.root.ids['screen_manager']

        if screen_name == 'home_screen':
            screen_manager.transition.direction = "right"
        if screen_name == 'settings_screen':
            screen_manager.transition.direction = "left"  
        if screen_name == 'input_screen':
            screen_manager.transition.direction = "left"                
        screen_manager.current = screen_name

    def blank_input_fields(self):
        transaction_ids = self.root.ids['input_screen'].ids
        transaction_ids['price'].text = ""
        transaction_ids['qty'].text = ""
        transaction_ids['ticker'].text = ""

    def show_popup(self):

        valid = True
        transaction_ids = self.root.ids['input_screen'].ids
        self.ticker = (transaction_ids['ticker'].text.strip()).upper()
        self.price = transaction_ids['price'].text
        self.qty = transaction_ids['qty'].text
        self.ticker_name = get_symbol(self.ticker)        

        try:
            self.direction
        except AttributeError:
            transaction_ids['direction_error'].text = "[color=CF1E15]SELECT DIRECTION[/color]"
            transaction_ids['submit_error'].text = "[color=CF1E15]FIX ERRORS BELOW[/color]"             
            valid = False
            return
        
        if self.ticker == "":
            transaction_ids['ticker_error'].text = "[color=CF1E15]ENTER TICKER[/color]"
            transaction_ids['submit_error'].text = "[color=CF1E15]FIX ERRORS BELOW[/color]"             
            valid = False
            # transaction_ids["ticker"].background_color = (1,0,0,1)            
            return
        if get_symbol(self.ticker) == None:
            valid = False            
            transaction_ids['ticker_error'].text = "[color=CF1E15]INVALID TICKER[/color]"
            transaction_ids['submit_error'].text = "[color=CF1E15]FIX ERRORS BELOW[/color]"             
            return
        else:
            transaction_ids['ticker_name'].text = self.ticker_name
        try:
            self.price = float(self.price)
        except:
            transaction_ids['price_error'].text = "[color=CF1E15]INVALID PRICE[/color]"
            transaction_ids['submit_error'].text = "[color=CF1E15]FIX ERRORS BELOW[/color]"             
            valid = False            
            # transaction_ids["price"].background_color = (1,0,0,1)
            return
        try:
            self.qty = int(self.qty)
        except:
            transaction_ids['qty_error'].text = "[color=CF1E15]INVALID QTY[/color]"    
            transaction_ids['submit_error'].text = "[color=CF1E15]FIX ERRORS BELOW[/color]"                   
            valid = False              
            # transaction_ids["qty"].background_color = (1,0,0,1)
            return

        if valid:
            self.confirm_add = self.direction.upper() + ' ' + str(self.qty) + ' ' + self.ticker + " @ $" + str(self.price)
            popupwindow = SetPopup()
            popupwindow.ids['confirm_label'].text = self.confirm_add
            popupwindow.open()


    def add_transaction(self):
                    
        #if all data is okay, send the data to firebase real time database
        my_data = { "ticker": self.ticker,
                    "price": self.price,
                    "qty":self.qty}
        post_request = requests.post("https://investmentsummary-94034.firebaseio.com/%s/%s.json?auth=%s" %(self.local_id,self.direction,self.id_token),
                        data = json.dumps(my_data))                          
        pass


if __name__ == "__main__":
    WindowsApp().run()