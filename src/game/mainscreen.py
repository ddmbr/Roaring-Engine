import random
import pygame
import socket
import json
import pymunk

import serge.actor
import serge.visual
import serge.events
import serge.common
import serge.blocks.utils
import serge.blocks.behaviours
import serge.blocks.actors

from theme import G

import player
import bg
import olctlhub
import track
import messager
import common
import startscreen
import waitingscreen

class MainScreen(serge.blocks.actors.ScreenActor):
    """ The logic for the main screen """
    def __init__(self, other_player_num = 0, isOLPlay = False):
        super(MainScreen, self).__init__('item', 'main-screen')
        self.other_player_num = other_player_num
        self.isOLPlay = isOLPlay
    def addedToWorld(self, world):
        super(MainScreen, self).addedToWorld(world)
        self.broadcaster.linkEvent(common.E_GAME_OVER, self.destroy)
        self.manager = world.findActorByName('behaviours')
        #
        #Now add actors to the world
        #
        #for example,
        #
        #   self.player = serge.blocks.utils.addActorToWorld(
        #       world,
        #       player.PlayerCar('player', 'player')
        #       )
        #
        self.sock = olctlhub.sock
        #
        # add bars to the track
        print track.start_pos
        self.player = serge.blocks.utils.addActorToWorld(
            world,
            player.Player(self.isOLPlay, True, self.sock),
            physics = serge.physical.PhysicalConditions(
                mass = 3,
                width = 48,
                height = 64,
                elasticity = 0.0,
                friction = 0.9,
                update_angle = True
                ),
            center_position = track.start_pos,
            origin = track.start_pos,
            )
        camera = serge.engine.CurrentEngine().renderer.getCamera()
        camera.setTarget(self.player)
        if self.isOLPlay:
            self.olctl = serge.blocks.utils.addActorToWorld(
                world,
                olctlhub.OLControlHub(self.sock)
                )
            self.log.info('Create OLCtl complete with players '+str(self.other_player_num))
            while len(world.findActorsByTag('player')) != self.other_player_num + 1:
                data = ['request-player']
                olctlhub.send(data)
                self.olctl.updateActor(1, world)
        self.ground = serge.blocks.utils.addActorToWorld(
            world,
            bg.Ground('ground', 'ground'),
            )
        serge.blocks.utils.addActorToWorld(
            world,
            bg.Background(),
            )

    def destroy(self, obj, arg):
        if self.isOLPlay == False:
            startscreen.main()
        elif self.isOLPlay == True:
            waitingscreen.main()

def main(other_player_num = 0, isOLPlay = False):
    engine = serge.engine.CurrentEngine()
    engine.setCurrentWorldByName('main-screen')
    world = engine.getWorld('main-screen')
    world.clearActors()
    track.addTrack(world)
    manager = serge.blocks.behaviours.BehaviourManager('behaviours', 'behaviours')
    world.addActor(manager)
    world.msgr = messager.Messager('messager', 'messager')
    world.addActor(world.msgr)
    s = MainScreen(other_player_num, isOLPlay)
    world.addActor(s)
