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
import olctlhub
import mainscreen
import track
import bg

class StartScreen(serge.blocks.actors.ScreenActor):
    def __init__(self):
        super(StartScreen, self).__init__('item', 'start-screen')
    def addedToWorld(self, world):
        super(StartScreen, self).addedToWorld(world)
        serge.blocks.utils.addActorToWorld(
            world,
            widget.Button("practice", content = "Practice"),
            center_position = (400, 300)
            )
        serge.blocks.utils.addActorToWorld(
            world,
            widget.Button("play-online", content = "Go Online"),
            center_position = (400, 380)
            )
        serge.blocks.utils.addActorToWorld(
            world,
            widget.Button("help", content = "Help"),
            center_position = (400, 460)
            )
        serge.blocks.utils.addActorToWorld(
            world,
            widget.Scalar((500, 300), track.track_num, maxValue = 3),
            )
        serge.blocks.utils.addActorToWorld(
            world,
            bg.Background('bg-start'),
            )
        self.manager = world.findActorByName('behaviours')
        self.manager.assignBehaviour(
            self, widget.ClickCheck(), 'click-check-start')

    def updateActor(self, interval, world):
        pass

def main():
    engine = serge.engine.CurrentEngine()
    world = engine.getWorld('start-screen')
    world.clearActors()
    engine.setCurrentWorldByName('start-screen')
    manager = serge.blocks.behaviours.BehaviourManager('behaviours', 'behaviours')
    world.addActor(manager)
    s = StartScreen()
    world.addActor(s)
