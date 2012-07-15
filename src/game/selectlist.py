
""" This is class for select list """

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

class SelectList(serge.blocks.actors.ScreenActor):
    def __init__(self, prefix):
        # init a empty list
        super(SelectList, self).__init__('select-list', 'select-list')
        self.selected = None
        self.container = []
        self.prefix = prefix

    def selectItem(self, container):
        for item in self.container:
            if item.content == content:
                # TODO hightlight it
                return item 

    def updateList(self, container):
        #
        # update the list
        # and the selected item
        self.log.info(container)
        self.log.info('update list')
        self.removeChildren()
        self.container = container
        pos = [self.x, self.y]
        for each in self.container:
            # TODO set pos
            self.log.info('add a child to list '+str(each))
            self.addChild(SingleListItem(str(each), self.prefix+str(each), pos))
            pos[1] += 30
        #for each in self.getChildren():
        #    self.log.info('add a child to world')
        #    each.addToWorld(self.world)

class SingleListItem(serge.actor.Actor):
    def __init__(self, name, content, pos):
        super(SingleListItem, self).__init__('list-item', name)
        self.content = content
        self.x, self.y = pos
    def addedToWorld(self, world):
        text = serge.visual.Text(self.content, (0xff, 0xff, 0xff), font_size = 18)
        self.log.info(self.content)
        self.setVisual(text)
        self.setLayerName('status')
        self.rect[2], self.rect[3] = text.width, text.height
    def hightlight(self):
        text = serge.visual.Text(self.content, (0x64, 0x95, 0xed), font_size = 18)
        self.setVisual(text)
