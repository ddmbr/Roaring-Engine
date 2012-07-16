import random
import pygame
import json
import socket

import serge.actor
import serge.visual
import serge.events
import serge.common
import serge.blocks.utils
import serge.blocks.behaviours
import serge.blocks.actors

from theme import G

import button
import olctlhub
import selectlist
import mainscreen

class WaitingScreen(serge.blocks.actors.ScreenActor):
    def __init__(self):
        super(WaitingScreen, self).__init__('item', 'waiting-screen')
    def addedToWorld(self, world):
        super(WaitingScreen, self).addedToWorld(world)
        serge.blocks.utils.addActorToWorld(
            world,
            button.Button("refresh", content = "Refresh"),
            center_position = (200, 200)
            )
        serge.blocks.utils.addActorToWorld(
            world,
            button.Button("new", content = "New"),
            center_position = (200, 280)
            )
        serge.blocks.utils.addActorToWorld(
            world,
            button.Button("start", content = "Start"),
            center_position = (200, 360)
            )
        self.roomList = serge.blocks.utils.addActorToWorld(
            world,
            selectlist.SelectList('Room #'),
            center_position = (500, 200)
            )
        self.manager = world.findActorByName('behaviours')
        self.manager.assignBehaviour(
            self, ClickCheck(), 'click-check')
    def updateActor(self, interval, world):
        try:
            recieved = olctlhub.sock.recv(1024, socket.MSG_DONTWAIT)
        except:
            return
        recieved = json.loads(recieved)
        if recieved[1] == 'room-list':
            self.roomList.updateList(recieved[2])
        elif recieved[1] == 'start' or recieved[1] == 'keys':
            self.log.info('we will start')
            mainscreen.main(int(recieved[2]) - 1)
    
class ClickCheck(serge.blocks.behaviours.Behaviour):
    def __call__(self, world, actor, interval):
        mouse = serge.engine.CurrentEngine().getMouse()
        if mouse.isClicked(serge.input.M_LEFT):
            for button in mouse.getActorsUnderMouse(world):
                self.log.info('button type:'+button.tag)
                if button.tag == 'list-item':
                    # join in a room
                    button.hightlight()
                    olctlhub.send(json.dumps(['join-room', int(button.name)]))
                else:
                    if button.name == 'refresh':
                        olctlhub.send(json.dumps(['view-rooms']))
                    elif button.name == 'new':
                        olctlhub.send(json.dumps(['new-room'])
                            )
                        olctlhub.send(json.dumps(['view-rooms']))
                    elif button.name == 'start':
                        olctlhub.send(json.dumps(['start']))

def main():
    engine = serge.engine.CurrentEngine()
    engine.setCurrentWorldByName('main-screen')
    world = engine.getWorld('waiting-screen')
    if world.findActorByName('waiting-screen') != None:
        return
    manager = serge.blocks.behaviours.BehaviourManager('behaviours', 'behaviours')
    world.addActor(manager)
    s = WaitingScreen()
    world.addActor(s)
