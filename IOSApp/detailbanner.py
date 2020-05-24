from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image
from kivy.graphics import Color,Rectangle
import kivy.utils
from kivy.app import App


class SummaryBanner(ButtonBehavior, GridLayout):

    def __init__(self, **kwargs):
        self.rows = 1
        self.app = App.get_running_app()
        self.ticker = kwargs['ticker']
        self.curr_price = '${:,.2f}'.format(kwargs['curr_price'])
        super(SummaryBanner, self).__init__()
        with self.canvas.before:
            if kwargs['percent'] > 0:
                Color(rgb=(kivy.utils.get_color_from_hex("#53C255")))
            else:
                Color(rgb=(kivy.utils.get_color_from_hex("#CF1E15")))
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)

        left = FloatLayout()
        # left_image = Image(source='icons/' + kwargs['image'], size_hint= (1, 0.8), pos_hint={"top": 1, "left": 1})
        left_label = Label(text=kwargs['ticker'], color=(0,0,0,1),markup=True,  bold=True, font_size=50,size_hint=(1, 1), pos_hint={"top": 1, "right": 1})
        # left.add_widget(left_image)
        left.add_widget(left_label)


        middle1 = FloatLayout()
        middle1_label = Label(text='${:,.2f}'.format(kwargs['purchase_price']), color=(0,0,0,1),markup=True,font_size=35, bold=True, size_hint=(1, 1), pos_hint={"top": 1, "right": 1})
        middle1.add_widget(middle1_label)


        middle2 = FloatLayout()
        middle2_label = Label(text='${:,.2f}'.format(kwargs['curr_price']), color=(0,0,0,1),markup=True,font_size=35,  bold=True, size_hint=(1, 1), pos_hint={"top": 1, "right": 1})
        middle2.add_widget(middle2_label)


        right = FloatLayout()
        right_label = Label(text=str(kwargs['percent']), color=(0,0,0,1),markup=True,  bold=True,font_size=35, size_hint=(1, 1), pos_hint={"top": 1, "right": 1})
        right.add_widget(right_label)


        self.add_widget(left)
        self.add_widget(middle1) 
        self.add_widget(middle2)               
        self.add_widget(right)
        self.bind(on_release=self.show_ticker_details)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def show_ticker_details(self, *args):
        self.app.change_screen('detail_screen')
        self.app.show_ticker_details(self.ticker)



class DetailBanner(ButtonBehavior, GridLayout):

    def __init__(self, **kwargs):
        self.rows = 1
        self.app = App.get_running_app()     
        self.prc = kwargs['price']
        self.qty = kwargs['qty']
        self.direction = kwargs['direction']   
        self.entry = kwargs['entry']
        super(DetailBanner, self).__init__()
        self.identifier = kwargs['identifier']
        with self.canvas.before:
            Color(rgb=(kivy.utils.get_color_from_hex("#18BACD")))
            # if kwargs['percent'] > 0:
            #     Color(rgb=(kivy.utils.get_color_from_hex("#53C255")))
            # else:
            #     Color(rgb=(kivy.utils.get_color_from_hex("#CF1E15")))
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)

        left = FloatLayout()
        left_label = Label(text=kwargs['direction'], color=(0,0,0,1),markup=True,  bold=True, font_size=50,size_hint=(1, 1), pos_hint={"top": 1, "right": 1})
        left.add_widget(left_label)

        middle1 = FloatLayout()
        middle1_label = Label(text=str(kwargs['qty']), color=(0,0,0,1),markup=True,font_size=35, bold=True, size_hint=(1, 1), pos_hint={"top": 1, "right": 1})
        middle1.add_widget(middle1_label)

        middle2 = FloatLayout()
        middle2_label = Label(text='${:,.2f}'.format(kwargs['price']), color=(0,0,0,1),markup=True,font_size=35,  bold=True, size_hint=(1, 1), pos_hint={"top": 1, "right": 1})
        middle2.add_widget(middle2_label)

        self.add_widget(left)
        self.add_widget(middle1) 
        self.add_widget(middle2)       
        self.bind(on_release=self.show_modify_delete_option)                

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size      

    def show_modify_delete_option(self, *args):
        self.app.show_delete_modify_popup()
        self.app.temp_prc = self.prc
        self.app.temp_qty = self.qty
        self.app.temp_entry = self.entry
        self.app.temp_dir = self.direction  
        self.app.temp_id = self.identifier    


class HistoryBanner(GridLayout):

    def __init__(self, **kwargs):
        self.rows = 1
        self.app = App.get_running_app()
        self.method = kwargs['method']
        super(HistoryBanner, self).__init__()
        with self.canvas.before:
            if self.method == 'insert':
                rgb = rgb=(kivy.utils.get_color_from_hex("#66E683"))
            elif self.method == 'modify':
                rgb = (kivy.utils.get_color_from_hex("#FEB33E"))
            else:
                rgb = (kivy.utils.get_color_from_hex("#F18888"))
                      

        left1 = FloatLayout()
        left1_label = Label(text=kwargs['ticker'], color=rgb,markup=True,  bold=True, font_size=40,size_hint=(1, 1), pos_hint={"top": 1, "right": 1})
        left1.add_widget(left1_label)

        left2 = FloatLayout()
        display_text = kwargs['direction']
        # if self.method == 'modify':
        #     display_text = kwargs['direction']+"(M)"
        # elif self.method == 'delete':
        #     display_text = kwargs['direction']+"(D)"
        # else:
        #     display_text = kwargs['direction']
                    
        left2_label = Label(text=display_text, color=rgb,markup=True,  bold=True, font_size=40,size_hint=(1, 1), pos_hint={"top": 1, "right": 1})
        left2.add_widget(left2_label)


        middle1 = FloatLayout()
        middle1_label = Label(text=str(kwargs['qty']), color=rgb,markup=True,font_size=35, bold=True, size_hint=(1, 1), pos_hint={"top": 1, "right": 1})
        middle1.add_widget(middle1_label)


        middle2 = FloatLayout()
        middle2_label = Label(text='${:,.2f}'.format(kwargs['price']), color=rgb,markup=True,font_size=35,  bold=True, size_hint=(1, 1), pos_hint={"top": 1, "right": 1})
        middle2.add_widget(middle2_label)


        right = FloatLayout()
        right_label = Label(text=kwargs['timestamp'], color=rgb ,markup=True,  bold=True,font_size=35, size_hint=(1, 1), pos_hint={"top": 1, "right": 1})
        right.add_widget(right_label)


        self.add_widget(left1)
        self.add_widget(left2)
        self.add_widget(middle1) 
        self.add_widget(middle2)               
        self.add_widget(right)