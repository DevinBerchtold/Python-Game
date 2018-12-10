#!/usr/bin/env python

# - - - - - - - - - - - #
#  Devin's Pygame Demo  #
# - - - - - - - - - - - #
# [Functions]
#   Miscellaneous
# [Game]
#   Imports
#   Constants
# [Classes]
#   Object
#     Bullet
#       PBullet
#       EBullet
#     Character
#       Player
#       Enemy
# [Main]
#   Initialization
#   Game Loop


###################################################
##                                               ##
##    ######       ###     ##     ##  ########   ##
##   ##    ##     ## ##    ###   ###  ##         ##
##   ##          ##   ##   #### ####  ##         ##
##   ##   ####  ##     ##  ## ### ##  ######     ##
##   ##    ##   #########  ##     ##  ##         ##
##   ##    ##   ##     ##  ##     ##  ##         ##
##    ######    ##     ##  ##     ##  ########   ##
##                                               ##
###################################################


# - - - - - #
#  Imports  #
# - - - - - #

import os.path
import sys
import math

# pygame modules
import pygame as pg
from pygame import Surface
from pygame import Rect
from pygame import gfxdraw
from pygame.sprite import Sprite
from pygame.sprite import Group
from pygame.locals import *

# see if we can load more than standard BMP
if not pg.image.get_extended():
    raise SystemExit("Sorry, extended image module required")


# - - - - - - #
#  Constants  #
# - - - - - - #

# game constants
SCREENRECT  = Rect(0, 0, 640, 480)  # dimensions of screen
GAME_TITLE  = "Charlie's Python Game"
BACKGROUND  = Surface(SCREENRECT.size)
SUPERSCALE  = 2  # 0: none, 1: aa, 2+: aa and ss
TRANSPARENT = (255, 0, 255)
FPS         = 30
BACKGROUND.fill( (64, 64, 64) )

main_dir = os.path.split( os.path.abspath(__file__) )[0]




######## ##     ## ##    ##  ######  ######## ####  #######  ##    ##  ######
##       ##     ## ###   ## ##    ##    ##     ##  ##     ## ###   ## ##    ##
##       ##     ## ####  ## ##          ##     ##  ##     ## ####  ## ##
######   ##     ## ## ## ## ##          ##     ##  ##     ## ## ## ##  ######
##       ##     ## ##  #### ##          ##     ##  ##     ## ##  ####       ##
##       ##     ## ##   ### ##    ##    ##     ##  ##     ## ##   ### ##    ##
##        #######  ##    ##  ######     ##    ####  #######  ##    ##  ######


# - - - - - - #
#  Decorator  #
# - - - - - - #

def print_args(func):
    def wrapper(*args, **kwargs):
        # before function call
        print('sstart:', func)
        if (args):
            print('   arg:', args)
        if (kwargs):
            print('   kws:', kwargs)
        # call function and save result
        ret = func(*args, **kwargs)
        # print function information
        if (ret):
            print('   ret:', ret)
        print('ending:', func)
        return ret
    return wrapper


# - - - - - - - - #
#  Miscellaneous  #
# - - - - - - - - #

def angle_to_tuple(deg):
    rad = math.radians(deg)                 # convert angle to radians
    return (math.cos(rad), math.sin(rad))   # return x and y tuple

def tuple_to_angle(tup):
    rad = math.atan(tup[1] / tup[0])    # get angle in radians
    return math.degrees(rad)            # convert to degrees and return

def point_direction(a, b):
    return normalized_tuple((b[0] - a[0], b[1] - a[1]))     # normalize to just get angle

def point_distance(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])  # return distance from a to b

def normalized_tuple(tup):
    size = math.hypot(*tup)
    if size > 0:
        return (tup[0] / size, tup[1] / size)
    else:
        return (0.0, 0.0)

def dir_speed(tup, spd):
    size = math.hypot(*tup)
    if size > 0:
        mult = spd / size
        return (tup[0] * mult, tup[1] * mult)
    else:
        return (0.0, 0.0)




 ######  ##          ###     ######   ######  ########  ######
##    ## ##         ## ##   ##    ## ##    ## ##       ##    ##
##       ##        ##   ##  ##       ##       ##       ##
##       ##       ##     ##  ######   ######  ######    ######
##       ##       #########       ##       ## ##             ##
##    ## ##       ##     ## ##    ## ##    ## ##       ##    ##
 ######  ######## ##     ##  ######   ######  ########  ######


# Sprite
#   Object
#     Bullet
#       PBullet
#       Ebullet
#     Person
#       Player
#       Enemy

# - - - - - - - - - - - - #
#  OBJECT extends SPRITE  #
# - - - - - - - - -  -  - #

class Object(Sprite):
    radius      = 16.0
    color       = (255, 255, 255, 255)  # RGB
    alpha       = 255  # 100% OPAQUE
    containers  = None

    # every object drawn needs 'image'
    image = None
    rect = SCREENRECT

    def __init__(self):
        super().__init__(self.containers)
        self.set_radius(self.radius)

    def __repr__(self):
        return "<%s Object>" % (self.__class__.__name__)

    def set_position(self, position):
        self.rect.center = position

    def set_radius(self, value):
        # update radius and redraw circle sprite
        r = int(value)
        final_size = (r*2 + 1, r*2 + 1)
        self.radius = r

        if SUPERSCALE == 0:  # don't do superscale or anti-aliasing
            self.image = Surface(final_size)
            self.image.fill(TRANSPARENT)
            self.image.set_colorkey(TRANSPARENT)
            pg.draw.circle(self.image, self.color, (r, r), r, 0)
        else:  # SUPERSCALE >= 1
            # setup temporary, superscaled circle
            r *= SUPERSCALE
            temp_image = Surface( (r*2 + 1, r*2 + 1), pg.SRCALPHA, 32)
            temp_image.fill( (255, 255, 255, 0) )
            # draw circle
            gfxdraw.aacircle(temp_image, r, r, r, self.color)
            gfxdraw.filled_circle(temp_image, r, r, r, self.color)
            # resize temp image and place into self.image
            self.image = Surface(final_size, pg.SRCALPHA, 32)
            self.image = pg.transform.smoothscale(temp_image, final_size)

        self.rect = self.image.get_rect(center=self.rect.center)

    def direction_to(self, position):
        return point_direction(self.rect.center, position)


# - - - - - - - - - - - - #
#  BULLET extends OBJECT  #
# - - - - - - - - - - - - #

class Bullet(Object):
    radius      = 10.0
    direction   = (0.0, 0.0)
    speed       = 10.0

    @print_args
    def __init__(self, position, direction):
        super().__init__()
        self.rect.center = position
        self.direction = dir_speed(direction, self.speed)

    def update(self):
        self.rect.move_ip(self.direction)
        if not self.rect.colliderect(SCREENRECT):
            self.kill()


# - - - - - - - - - - - - #
# PBULLET extends BULLET  #
# - - - - - - - - - - - - #

class PBullet(Bullet):
    radius = 12.0

    @print_args
    def __init__(self, pos, dir):
        super().__init__(pos, dir)

    def update(self):
        super().update()


# - - - - - - - - - - - - #
# EBULLET extends BULLET  #
# - - - - - - - - - - - - #

class EBullet(Bullet):
    radius = 8.0
    speed = 5.0

    def __init__(self, pos, dir):
        super().__init__(pos, dir)

    def update(self):
        super().update()


# - - - - - - - - - - - - - #
#  CHARACTER extends OBJECT #
# - - - - - - - - -  -  - - #

class Character(Object):
    radius          = 20.0
    health          = 10.0
    speed           = 8.0
    reload_time     = 4.0
    reload_count    = 0.0
    bull            = Bullet

    @print_args
    def __init__(self, position):
        super().__init__()
        # start in the center of the screen
        self.rect = self.image.get_rect(center=position)

    def try_fire(self, direction):
        if self.reload_count > 0:  # count not up; still reloading
            self.reload_count -= 1  # keep counting...
        else:  # fire bullet
            self.bull(self.rect.center, direction)  # create the bullet
            self.reload_count = self.reload_time  # reset reload counter

    def update(self):
        super().update()


# - - - - - - - - - - - - - -#
#  PLAYER extends CHARACTER  #
# - - - - - - - - - - - - - -#

class Player(Character):
    speed   = 8.0
    health  = 100.0
    bull    = PBullet

    @print_args
    def __init__(self, position):
        super().__init__(position)

    def update(self):
        # get keyboard info
        keystate = pg.key.get_pressed()

        # move player
        move_direction = (keystate[K_d] - keystate[K_a], keystate[K_s] - keystate[K_w])
        self.rect.move_ip( *dir_speed(move_direction, self.speed) )
        self.rect = self.rect.clamp(SCREENRECT)  # don't move out of the screen

        # do firing
        fire_key = keystate[K_RIGHT] or keystate[K_LEFT] or keystate[K_DOWN] or keystate[K_UP]
        if fire_key:
            fire_direction = (keystate[K_RIGHT] - keystate[K_LEFT], keystate[K_DOWN] - keystate[K_UP])
            direction = [x * 0.4 + y for x, y in zip(move_direction, fire_direction)]
            self.try_fire(direction)


# - - - - - - - - - - - - - - #
#   ENEMY extends CHARACTER   #
# - - - - - - - - - - - - - - #

class Enemy(Character):
    speed       = 3.0
    reload_time = 15.0
    bull        = EBullet
    target      = None

    @print_args
    def __init__(self, position, target):
        super().__init__(position)
        self.target = target

    def update(self):
        target_dir = self.direction_to(self.target.rect.center)
        self.try_fire(target_dir)  # reload and fire when ready
        self.rect.move_ip( *dir_speed(target_dir, self.speed) )


##     ##    ###    #### ##    ##
###   ###   ## ##    ##  ###   ##
#### ####  ##   ##   ##  ####  ##
## ### ## ##     ##  ##  ## ## ##
##     ## #########  ##  ##  ####
##     ## ##     ##  ##  ##   ###
##     ## ##     ## #### ##    ##


def main(winstyle=0):

    # - - - - - - - - #
    #  Initial Setup  #
    # - - - - - - - - #

    pg.init()  # initialize pygame

    # setup display mode and window
    winstyle = 0  # |FULLSCREEN
    bestdepth = pg.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pg.display.set_mode(SCREENRECT.size, winstyle, bestdepth)
    pg.display.set_caption(GAME_TITLE)
    # clock to keep track of time
    clock = pg.time.Clock()

    # add background
    screen.blit(BACKGROUND, (0, 0))
    pg.display.flip()

    # groups
    player_group    = Group()  # group of 'players' (there's just 1)
    bullet_group    = Group()  # group of all bullets
    pbullet_group   = Group()  # group of player bullets
    ebullet_group   = Group()  # group of enemy bullets
    enemy_group     = Group()  # group of enemys
    all_groups      = pg.sprite.RenderUpdates()  # things updated this frame

    # connect groups to sprite classes
    Player.containers   = player_group, all_groups
    Enemy.containers    = enemy_group, all_groups
    Bullet.containers   = pbullet_group, ebullet_group, bullet_group, all_groups
    PBullet.containers  = pbullet_group, bullet_group, all_groups
    EBullet.containers  = ebullet_group, bullet_group, all_groups

    # create player and enemies
    player = Player(SCREENRECT.center)

    e1 = Enemy(SCREENRECT.midright, player)
    e2 = Enemy(SCREENRECT.midbottom, player)
    e3 = Enemy(SCREENRECT.midleft, player)
    e4 = Enemy(SCREENRECT.midtop, player)

    e1.target = e2
    e2.target = e3
    e3.target = e4
    e4.target = e1


    # - - - - - - - - - - - - #
    #  Main Player Game Loop  #
    # - - - - - - - - - - - - #

    while player.alive():
        # check if player is trying to exit...
        for event in pg.event.get():
            if event.type == QUIT or \
                    (event.type == KEYDOWN and event.key == K_ESCAPE):
                    sys.exit()

        # update sprites and objects
        all_groups.clear(screen, BACKGROUND)  # clear/erase the last drawn sprites
        all_groups.update()  # update all the sprites

        # enemy bullet collidese with player   One Instance    Group of Instances
        # for bullet in pg.sprite.spritecollide(player, ebullet_group, False):
            # player.kill()

        #                                     collider  collisions[collider]
        cols = pg.sprite.groupcollide(ebullet_group, player_group, True, False, pg.sprite.collide_circle)
        for col in cols:
            cols[col].health -= col.damage

        cols = pg.sprite.groupcollide(pbullet_group, enemy_group, True, False, pg.sprite.collide_circle)
        for col in cols:
            cols[col].health -= col.damage

        # redraw game updates
        dirty = all_groups.draw(screen)
        pg.display.update(dirty)  # draw the scene

        # cap the framerate using the clock
        clock.tick(FPS)

    # one second delay then quit
    pg.time.wait(1000)
    pg.quit()

# just run main to run the game
main()