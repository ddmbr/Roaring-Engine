
""" This is class for button """

import pygame
import random
import math
import socket
import json
import time

import serge.actor
import serge.common
import serge.visual
import serge.geometry
import serge.blocks.behaviours

from theme import G
import text

class Messager(serge.blocks.actors.ScreenActor):
    def displayMsg(self, content, time = 1):
        self.addChild(Message(content, time))

class Message(serge.blocks.actors.ScreenActor):
    def __init__(self, content, time):
        super(Message, self).__init__('msg', 'msg')
        self.setSpriteName('default-msg')
        self.setLayerName('message')
        self.content = content
        self.during = time

    def addedToWorld(self, world):
        super(Message, self).addedToWorld(world)
        self.status = 'up'
        self.moveTo(G('screen-width') / 2, G('screen-height') + G('msg-height') / 2)
    def updateActor(self, interval, world):
        if self.status == 'up':
            self.y -= 8
            if self.y <= G('screen-height') - G('msg-height') / 2:
                self.status = 'keep'
                self.startTime = time.time()
                self.addChild(text.Text(self.content, (self.x, self.y)))
        elif self.status == 'keep':
            if time.time() >= self.startTime + self.during:
                self.status = 'down'
                self.removeChildren()
        elif self.status == 'down':
            self.y += 8
            if self.y >= G('screen-height') + G('msg-height') / 2:
                world.removeActor(self)
