
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
import mainscreen
import waitingscreen
import text
import olctlhub
import track

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
        self.setLayerName('status')
        self.addChild(text.Text(self.content, (self.x, self.y)))


class Scalar(serge.blocks.actors.ScreenActor):
    def __init__(self, pos, value, name = 'scalar', maxValue = 5):
        super(Scalar, self).__init__('scalar', name)
        self.maxValue = maxValue
        self.pos = pos
        self.value = value
    def addedToWorld(self, world):
        super(Scalar, self).addedToWorld(world)
        self.incButton = IncButton(self)
        self.decButton = DecButton(self)
        self.text = text.Text(str(self.value[0]), self.pos)
        self.world.addActor(self.text)
        self.world.addActor(self.incButton)
        self.incButton.moveTo(self.pos[0] + 30, self.pos[1])
        self.world.addActor(self.decButton)
        self.decButton.moveTo(self.pos[0] - 30, self.pos[1])
    def dec(self):
        self.value[0] -= 1
        if self.value[0] < 0:
            self.value[0] = self.maxValue
        self.updateText()
        if self.value == track.track_num and self.world.name == 'waiting-screen':
            olctlhub.send(['chg-track', track.track_num[0]])
    def inc(self):
        self.value[0] += 1
        if self.value[0] > self.maxValue:
            self.value[0] = 1
        self.updateText()
        if self.value == track.track_num and self.world.name == 'waiting-screen':
            olctlhub.send(['chg-track', track.track_num[0]])
    def updateText(self):
        self.world.removeActor(self.text)
        self.text = text.Text(str(self.value[0]), self.pos)
        self.world.addActor(self.text)

class IncButton(serge.blocks.actors.ScreenActor):
    def __init__(self, control):
        super(IncButton, self).__init__('button', 'inc')
        self.control = control
    def addedToWorld(self, world):
        super(IncButton, self).addedToWorld(world)
        self.setSpriteName('inc-button')
        self.setLayerName('status')

class DecButton(serge.blocks.actors.ScreenActor):
    def __init__(self, control):
        super(DecButton, self).__init__('button', 'dec')
        self.control = control
    def addedToWorld(self, world):
        super(DecButton, self).addedToWorld(world)
        self.setSpriteName('dec-button')
        self.setLayerName('status')

class ClickCheck(serge.blocks.behaviours.Behaviour):
    def __call__(self, world, actor, interval):
        mouse = serge.engine.CurrentEngine().getMouse()
        if mouse.isClicked(serge.input.M_LEFT):
            for button in mouse.getActorsUnderMouse(world):
                self.log.info('button type:'+button.tag)
                if button.tag == 'list-item':
                    # join in a room
                    button.hightlight()
                    olctlhub.send(['join-room', int(button.name)])
                else:
                    if button.name == 'refresh':
                        olctlhub.send(['view-rooms'])
                        olctlhub.send(['my-room'])
                    elif button.name == 'new':
                        olctlhub.send(['new-room']
                            )
                        olctlhub.send(['view-rooms'])
                    elif button.name == 'start':
                        olctlhub.send(['start'])
                    elif button.name == 'practice':
                        mainscreen.main()
                    elif button.name == 'play-online':
                        waitingscreen.main()
                    elif button.name == 'inc':
                        button.control.inc()
                    elif button.name == 'dec':
                        button.control.dec()

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
            self.log.info('add a child to list '+str(each))
            self.addChild(SingleListItem(str(each), self.prefix+str(each), pos))
            pos[1] += 30

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

class Text(serge.actor.Actor):
    def __init__(self, content, pos):
        super(Text, self).__init__('text', content)
        self.content = content
        self.x, self.y = pos
    def addedToWorld(self, world):
        super(Text, self).addedToWorld(world)
        text = serge.visual.Text(self.content, (0xff, 0xff, 0xff), font_size = 18)
        self.setVisual(text)
        self.setLayerName('message')
        self.move(-text.width/2, -text.height/2)
    def updateText(self, content):
        self.content = content
        text = serge.visual.Text(self.content, (0xff, 0xff, 0xff), font_size = 18)
        self.setVisual(text)
