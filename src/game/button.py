
""" This is class for button """

import pygame
import random
import math
import socket
import json

import serge.actor
import serge.common
import serge.visual
import serge.geometry
import serge.blocks.behaviours

from theme import G

class Button(serge.blocks.actors.ScreenActor):
    #TODO Warp the size
    def __init__(self, name, content="default", color='default', size = (80, 56)):
        super(Button, self).__init__('button', name)
        self.color = color
        self.size = size
        self.content = content
    def addedToWorld(self, world):
        super(Button, self).addedToWorld(world)
        self.setSpriteName(self.color+'-button')
        self.setLayerName('main')
        #self.moveTo(G('screen-width') / 2, G('screen-height') / 2)
        self.addChild(ButtonText(self.content, (self.x, self.y)))

class ButtonText(serge.actor.Actor):
    def __init__(self, content, pos):
        super(ButtonText, self).__init__('button-text', content)
        self.content = content
        self.x, self.y = pos
    def addedToWorld(self, world):
        text = serge.visual.Text(self.content, (0xff, 0xff, 0xff), font_size = 18)
        self.setVisual(text)
        self.setLayerName('status')
        self.move(-text.width/2, -text.height/2)
