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

import widget
import text
import track
import olctlhub
import mainscreen
import bg

class WaitingScreen(serge.blocks.actors.ScreenActor):
    def __init__(self):
        super(WaitingScreen, self).__init__('item', 'waiting-screen')
    def addedToWorld(self, world):
        super(WaitingScreen, self).addedToWorld(world)
        serge.blocks.utils.addActorToWorld(
            world,
            widget.Button("refresh", content = "Refresh"),
            center_position = (200, 190)
            )
        serge.blocks.utils.addActorToWorld(
            world,
            widget.Button("new", content = "New"),
            center_position = (200, 250)
            )
        serge.blocks.utils.addActorToWorld(
            world,
            widget.Button("start", content = "Start"),
            center_position = (200, 310)
            )
        serge.blocks.utils.addActorToWorld(
            world,
            widget.Button("back", content = "Back"),
            center_position = (200, 370)
            )
        self.roomList = serge.blocks.utils.addActorToWorld(
            world,
            widget.SelectList('room #'),
            center_position = (500, 200)
            )
        serge.blocks.utils.addActorToWorld(
            world,
            text.Text('Current Room:'),
            center_position = (240, 440)
            )
        self.current_room_num = serge.blocks.utils.addActorToWorld(
            world,
            text.Text('null'),
            center_position = (200, 500)
            )
        self.current_room_track = serge.blocks.utils.addActorToWorld(
            world,
            widget.Scalar(pos = (240, 560), value = track.track_num, maxValue = 3),
            center_position = (240, 560)
            )
        self.current_room_players = serge.blocks.utils.addActorToWorld(
            world,
            text.Text('0 players'),
            center_position = (240, 600)
            )
        serge.blocks.utils.addActorToWorld(
            world,
            bg.Background('bg-waiting'),
            )
        self.manager = world.findActorByName('behaviours')
        self.manager.assignBehaviour(
            self, widget.ClickCheck(), 'click-check-waiting')

    def updateActor(self, interval, world):
        try:
            recieved = olctlhub.sock.recv(1024, socket.MSG_DONTWAIT)
        except:
            return
        recieved = json.loads(recieved)
        if recieved[1] == 'room-list':
            self.roomList.updateList(recieved[2])
        elif recieved[1] == 'my-room':
            # DEBUG
            print recieved
            if recieved[2][0] == -1: return

            self.current_room_num.updateText('room #'+str(recieved[2][0]))
            self.current_room_players.updateText(str(recieved[2][1])+' players')
            self.current_room_track.value = [recieved[2][2]]
            self.current_room_track.updateText()
        elif recieved[1] == 'start':
            self.log.info('we will start')
            # param: players number and track
            mainscreen.main(int(recieved[2][0]) - 1, recieved[2][1], True)
        elif recieved[1] == 'keys':
            self.log.info('Other players have started but I\'m not. Trying to start...')
            olctlhub.send(["start-me"])
    

def main():
    engine = serge.engine.CurrentEngine()
    engine.setCurrentWorldByName('waiting-screen')
    world = engine.getWorld('waiting-screen')
    world.clearActors()
    manager = serge.blocks.behaviours.BehaviourManager('behaviours', 'behaviours')
    world.addActor(manager)
    s = WaitingScreen()
    world.addActor(s)
