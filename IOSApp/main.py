import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button, ButtonBehavior
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Rectangle, Color, Line
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.utils import platform
from kivy.uix.dropdown import DropDown
import requests
import json
import re
from datetime import datetime
import concurrent.futures
from firebase import Firebase
from detailbanner import SummaryBanner,DetailBanner,HistoryBanner
from gatherdata import get_symbol, FinnhubIO

class HomeScreen(Screen):
    pass

class ImageButton(ButtonBehavior, Image):
    pass

class GridButton(ButtonBehavior, GridLayout):
    pass

class LabelButton(ButtonBehavior, Label):
    pass

class SettingsScreen(Screen):
    pass

class LoginScreen(Screen):
    pass

class InputScreen(Screen):
    pass

class DetailScreen(Screen):
    pass

class AccountScreen(Screen):
    pass

class HistoryScreen(Screen):
    pass

class SetPopup(Popup):
    pass

class EditPopup(Popup):
    pass

kv = Builder.load_file("main.kv")

class WindowsApp(App):

    refresh_token_file = "refresh_token.txt"
    firebase = None

    def build(self):
        self.firebase = Firebase()
        if platform == "ios":
            self.refresh_token_file = App.get_running_app().user_data_dir + self.refresh_token_file
        return Builder.load_file("main.kv")

    def refresh_user(self):

        with open(self.refresh_token_file, 'r') as f:
            refresh_token = f.read()
        self.id_token, self.local_id = self.firebase.exchange_refresh_token(refresh_token)        

    def on_start(self):

        try:
            # self.refresh_user()
            self.update()
            self.change_screen("home_screen")

        except Exception as e:
            print("Error is:{}".format(e))
            pass
            
    def convert_to_dict(self):
        #do something that goes through and adds vwap and qty before data is fetched

        data = self.firebase.getData()
        raw_data = {}
        
        for stock,val in data.items():
            if stock not in ("total","history"):
                try:
                    raw_data[stock] = {'total': val['qty'],
                                        'vwap': val['vwap']}

                except:
                    self.calc_vwap_qty(stock) 
                    raw_data[stock] = {'total': val['qty'],
                                        'vwap': val['vwap']}
                    pass

        ticker_list  = raw_data.keys()
        total_dict  = {'total':
                            {'orig_total': 0,
                            'new_total': 0,
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
            curr_price = FinnhubIO().getStockPrice(ticker)
            raw_data[ticker]['curr_price'] = curr_price
            raw_data[ticker]['orig_total'] = raw_data[ticker]['total']* raw_data[ticker]['vwap']
            raw_data[ticker]['new_total'] = raw_data[ticker]['total']* raw_data[ticker]['curr_price']  
            raw_data[ticker]['percent'] = calc_percent(raw_data[ticker]['new_total'], raw_data[ticker]['orig_total'])
            
            total_dict['total']['orig_total'] += raw_data[ticker]['orig_total']
            total_dict['total']['new_total'] += raw_data[ticker]['new_total']

            
        with concurrent.futures.ThreadPoolExecutor() as executor:
                [executor.submit(vwap_edit,ticker) for ticker in ticker_list]
        total_dict['total']['pnl'] = total_dict['total']['new_total'] - total_dict['total']['orig_total']
        total_dict['total']['percent'] = calc_percent(total_dict['total']['new_total'],total_dict['total']['orig_total'])
        total_dict['total']['new_total'] = float_to_money(total_dict['total']['new_total'])
        total_dict['total']['orig_total'] = float_to_money(total_dict['total']['orig_total'])
        return total_dict,raw_data            
        

    def show_ticker_details(self,ticker):
        try:
            data = self.firebase.getTickerData(ticker)
            detail_screen_ids = self.root.ids['detail_screen']
            detail_grid = detail_screen_ids.ids['detail_grid']  
            detail_grid.clear_widgets() 

            detail_screen_ids.ids['ticker_detail'].text = ticker
            # detail_screen_ids.ids['ticker_detail'].text = ticker + " - " + curr_price
            detail_screen_ids.ids['ticker_name_detail'].text = get_symbol(ticker)
            totalqty = 0
            #now I have the ticker information while on the page
            self.detail_ticker = ticker
            for entry,val in data.items():
                if isinstance(val,dict):
                    D = DetailBanner(direction=val['direction'].title(),identifier=val['id'],qty=val['qty'],price=val['price'],entry=entry)
                    detail_grid.add_widget(D)  
                    if val['direction'] == "buy":
                        totalqty += val['qty']
                    else:
                        totalqty -= val['qty']
            detail_screen_ids.ids['total_qty'].text = "Total Owned: " + str(totalqty)  
        except:
            self.change_screen('home_screen')
            self.update()        
         
    def update_detail(self):
        self.show_ticker_details(self.detail_ticker)

    def update(self):

        self.refresh_user()
        total_dict, self.final_data = self.convert_to_dict()
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
        asof_label.text = "Updated: \n" + datetime.now().strftime('%I:%M %p')

        #Update total invested 
        totalinvest_label = self.root.ids['home_screen'].ids['totalinvest_label']
        totalinvest_label.text = "Total Invested: \n" + total_dict['total']['orig_total']     

        summary_grid = self.root.ids['home_screen'].ids['summary_grid']  
        summary_grid.clear_widgets()  
        for k,v in self.final_data.items():
            S = SummaryBanner(ticker=k,purchase_price=v['vwap'],curr_price=v['curr_price'],percent=v['percent'])
            summary_grid.add_widget(S)


    def change_screen(self, screen_name):
        #get the screen manager from the kv file
        screen_manager = self.root.ids['screen_manager']
        self.prev_screen = screen_manager.current
        if screen_name == 'home_screen':
            screen_manager.transition.direction = "right"
        if screen_name == 'settings_screen':
            screen_manager.transition.direction = "left"  
        if screen_name == 'input_screen':
            screen_manager.transition.direction = "left"   
        if screen_name == 'detail_screen':
            screen_manager.transition.direction = "left" 
        if screen_name == 'history_screen':
            screen_manager.transition.direction = "left"                            
        screen_manager.current = screen_name
        self.curr_screen = screen_manager.current

    def blank_input_fields(self):
        transaction_ids = self.root.ids['input_screen'].ids
        transaction_ids['price'].text = ""
        transaction_ids['qty'].text = ""
        transaction_ids['ticker'].text = ""
        transaction_ids['ticker'].readonly = False
        transaction_ids['ticker_name'].text = ""

    def show_delete_modify_popup(self):
        popupwindow = EditPopup()
        popupwindow.open()

    def on_delete(self):
        self.firebase.removeData(self.detail_ticker,self.temp_entry)
        self.calc_vwap_qty(self.detail_ticker)

    def populate_ticker_name(self):
        transaction_ids = self.root.ids['input_screen'].ids     
        self.ticker = (transaction_ids['ticker'].text.strip()).upper() 
        self.ticker_name = get_symbol(self.ticker)

        if self.ticker_name == None:        
            transaction_ids['ticker_error'].text = "[color=CF1E15]INVALID TICKER[/color]"
            transaction_ids['submit_error'].text = "[color=CF1E15]FIX ERRORS BELOW[/color]"         
            return 

        transaction_ids['ticker_name'].text = self.ticker_name
        return 

    def show_popup(self):

        valid = True
        transaction_ids = self.root.ids['input_screen'].ids
        self.ticker = (transaction_ids['ticker'].text.strip()).upper()
        self.price = transaction_ids['price'].text
        self.qty = transaction_ids['qty'].text
        # self.ticker_name = get_symbol(self.ticker)        

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
        # else:
        #     transaction_ids['ticker_name'].text = self.ticker_name
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

    def add_or_modify_transaction(self):
        if self.add_or_modify == "add":
            #add transaction to firebase db
            self.firebase.add_detail(self.direction,self.price,self.qty,self.ticker)   
            self.calc_vwap_qty(self.ticker)             
        else:
            self.firebase.modifyData(self.detail_ticker,self.temp_entry, self.direction,self.price, self.qty, self.temp_id)      
            self.calc_vwap_qty(self.detail_ticker) 
        pass 

    def calc_vwap_qty(self,ticker):
        all_data = self.firebase.getTickerData(ticker)
        temp_vwap = 0
        vwap_qty = {"qty": 0,
                    "vwap": 0}
        try:
            for k,v in all_data.items():
                if k not in ("nextId",'vwap','qty'):
                    if v["direction"] == "buy":
                        vwap_qty["qty"] += v["qty"]
                        temp_vwap += (v["qty"]*v["price"])
                    #put in what happens for sells
            vwap_qty["vwap"] = temp_vwap/vwap_qty["qty"]
            self.firebase.addVwapQty(ticker,vwap_qty)   

        except:
            print("ticker was deleted")
            pass

         




    def fill_in_input(self,option):
        transaction_ids = self.root.ids['input_screen'].ids
        transaction_ids['ticker'].text = self.detail_ticker
        transaction_ids['ticker'].readonly = True
        transaction_ids['ticker_name'].text = get_symbol(self.detail_ticker)
        if option == 'modify':
            transaction_ids['price'].text = str(self.temp_prc)
            transaction_ids['qty'].text = str(self.temp_qty) 

    def show_history(self):
        data = self.firebase.getHistoryData()
        history_screen_ids = self.root.ids['history_screen']
        history_grid = history_screen_ids.ids['history_grid']  
        history_grid.clear_widgets() 

        for entry,val in data.items():
            if isinstance(val,dict):
                timestamp = datetime.strptime(val['timestamp'], "%Y-%m-%d %H:%M:%S").strftime("%m-%d-%y")
                H = HistoryBanner(direction=val['direction'].title(),ticker=val['ticker'],qty=val['qty'],price=val['price'], method=val['method'],timestamp=timestamp)
                history_grid.add_widget(H)                   

if __name__ == "__main__":
    WindowsApp().run()