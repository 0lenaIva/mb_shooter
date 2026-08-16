from kivy.uix.bubble import Image
from kivymd.app import MDApp
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.image import Image
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from random import randint
from kivy.clock import Clock
from kivy.graphics import Color
from kivy.animation import Animation
from kivy.metrics import dp

YELLOW_COLOR = (1,1,0,0.7)
RED_COLOR = (1,0,0,0.5)

LIFE_TIME_DEF = 3

DIRECTION_UP = 1
DIRECTION_DOWN = -1

SPEED_DEF = 100

class Particle(Image):
    def __init__(self, direction = DIRECTION_DOWN, life = LIFE_TIME_DEF,
                 speed = SPEED_DEF, **kwargs):
        super().__init__(**kwargs)
        self.direction = direction
        self.life = life
        self.speed = self.direction * dp(randint(int(speed * self.life/2), 
                                                 int(speed * self.life)))
        self.size_hint = (None, None)

        anim = Animation(color=YELLOW_COLOR, duration=self.life * 0.3)+\
        Animation(color = RED_COLOR, duration=self.life *0.7, transition='out_quad')
        anim &=Animation(width = 20, duration=self.life)
        center_x = self.center_x
        anim &=Animation(center_x = center_x, duration=self.life)
        anim &=Animation(y=self.y+self.speed, duration=self.life)

        anim.start(self)#<----------------------------------

        anim.on_complete = self.destroy

    def destroy(self, *args):
        if self.parent:
            self.parent.remove_widget(self)
