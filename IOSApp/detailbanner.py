from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Color,Rectangle
import kivy.utils

class DetailBanner(GridLayout):

    def __init__(self, **kwargs):
        self.rows = 1
        super(DetailBanner, self).__init__()
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

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size