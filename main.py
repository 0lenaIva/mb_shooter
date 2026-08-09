from kivy.uix.accordion import NumericProperty
from kivymd.uix.banner.banner import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.bottomsheet.bottomsheet import MDWidget
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivy import platform
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import sp, dp
from random import randint
from kivy.core.window import Keyboard
from kivy.uix.image import Image
from kivymd.uix.fitimage import fitimage
from kivymd.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty

FPS = 60
BULLET_SPEED = dp(10)
SHIP_SPEED = dp(5)
DIR_UP = 1
DIR_DOWN = -1
HP_DEF = 3

class Shot(MDWidget):
    def __init__(self, direction,owner, **kwargs):
        super().__init__( **kwargs)
        self.direction = direction
        self.owner = owner 

class MainScreen(MDScreen):
    ...
class Ship(Image):
    def __init__(self,direction = DIR_UP ,hp=HP_DEF,**kwargs):
        super().__init__(**kwargs)
        self.direction = direction
        self.hp = self.max_hp = hp

    def moveLeft(self):
        self.pos[0] -= SHIP_SPEED
    def moveRight(self):
        self.pos[0] += SHIP_SPEED

    def shot(self):
        shot = Shot(self.direction, owner=self)#<____________________________________--
        shot.center_x = self.center_x
        shot.y = self.top if self.direction == DIR_UP else self.y - shot.height
        self.parent.parent.parent.parent.bullets.append(shot)
        self.parent.add_widget(shot)
    def update(self):#<----------------------------------
        pass
class PlayerShip(Ship):
    def __init__(self, direction=DIR_UP, **kwargs):
        super().__init__(direction, **kwargs)

    def update(self, keys):
        for key in keys:
            if keys[key] == True:
                if key == 'left' and self.center_x >0:
                    self.moveLeft()
                if key == 'right' and self.center_x<Window.width:
                    self.moveRight()
                if key == 'shot':
                    self.shot()
                    keys[key] = False
class EnemyShip(Ship):
    def __init__(self, direction=DIR_DOWN, **kwargs):
        super().__init__(direction, **kwargs)
        self.frame = 0

    def update(self):
        self.pos[1] -= dp(3)
        if self.frame % 100 == 0:
            self.shot()
        self.frame += 1

class GameScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.eventkeys = {}
        self.bullets = []# список пуль
        self.ship = self.ids.ship
        self.enemyShips = []
        self.pauseMenu = None

        Window.bind(on_key_down=self._on_key_down)
        Window.bind(on_key_up=self._on_key_up)

    def on_enter(self, *args):
        self.updateEvent = Clock.schedule_interval(self.update, 1/FPS)#<---------------------------------
        self.spawnEvent = Clock.schedule_interval(self.spawn_enemy, 2)#<<<<<<<<<<<<<<<<<<<<<<<<<<<

        return super().on_enter(*args)
    def spawn_enemy(self,dt):#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        ship = EnemyShip()
        ship.pos = (
            randint(0, int(Window.size[0] - ship.size[0])),
            Window.size[1]
        )
        self.enemyShips.append(ship)
        self.ids.front.add_widget(ship)
    def update(self, dt):
        self.ship.update(self.eventkeys)
        for ship in self.enemyShips:
            ship.update()
        self.manage_bullets()
        
    def manage_bullets(self):
        for bullet in self.bullets[:]:
            bullet.y += BULLET_SPEED * bullet.direction
            self.check_collisions(bullet)#<_______________________________________
            if bullet.y > Window.height or bullet.top < 0:
                self.ids.front.remove_widget(bullet)
                self.bullets.remove(bullet)

    def remove_bullet(self, bullet):
        if bullet in self.bullets:
            self.bullets.remove(bullet)
            self.ids.front.remove_widget(bullet)

    def check_collisions(self, bullet):
        if bullet.owner == self.ship:
            for enemy in self.enemyShips[:]:
                if bullet.collide_widget(enemy):
                    self.enemyShips.remove(enemy)
                    self.ids.front.remove_widget(enemy)

                    self.remove_bullet(bullet)
                    break
        else:
            if bullet.collide_widget(self.ship):
                self.remove_bullet(bullet)
                self.ship.hp -= 1
                if self.ship.hp <= 0:
                    self.game_over()
                    
    def game_over(self):
        self.updateEvent.cancel()
        self.spawnEvent.cancel()
        for bullet in self.bullets[:]:
            self.remove_bullet(bullet)
        self.manager.current = 'game_over'

    def pressKey(self, key):
        self.eventkeys[key] = True
    def releaseKey(self, key):
        self.eventkeys[key] = False
    def _on_key_down(self, window, keycode, *args, **kwargs):
        key = key if (key:=Keyboard.keycode_to_string(window, keycode))!='spacebar' else 'shot'
        self.eventkeys[key] = True
    def _on_key_up(self, window, keycode, *args, **kwargs):
        key = key if (key:=Keyboard.keycode_to_string(window, keycode))!='spacebar' else 'shot'
        self.eventkeys[key] = False

    def show_menu(self):
        if self.updateEvent:#<----------------------------------------
            self.updateEvent.cancel()
        if self.spawn_enemy:#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
            self.spawnEvent.cancel()
        if not self.pauseMenu:
            self.pauseMenu = MDDialog(
                title='Game Paused',
                text='Resume the game?',
                on_dismiss = self.resumeGame,buttons=[MDFlatButton(
                    text='RESUME',
                    theme_text_color='Custom',
                    text_color=app.theme_cls.primary_color,
                    on_press=self.pauseStop
                )]
            )
        self.pauseMenu.open()
    def pauseStop(self,*args):
        self.pauseMenu.dismiss()
    def resumeGame(self, *args):
        self.updateEvent = Clock.schedule_interval(self.update, 1/FPS)
        self.spawnEvent = Clock.schedule_interval(self.spawn_enemy, 2)
class GameOverScreen(MDScreen):
    pass
class ShooterApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'Orange'
        self.sm = MDScreenManager()
        self.sm.add_widget(MainScreen(name='main'))
        self.sm.add_widget(GameScreen(name='game'))
        self.sm.add_widget(GameOverScreen(name='game_over'))#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        return self.sm


if platform != 'android':
    Window.size = (400,700)
    Window.top = 100
    Window.left = 500

app = ShooterApp()
app.run()
