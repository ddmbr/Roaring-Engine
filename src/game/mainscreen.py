import random
import pygame
import socket
import json

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

class MainScreen(serge.blocks.actors.ScreenActor):
    """ The logic for the main screen """
    def __init__(self, other_player_num = 1):
        super(MainScreen, self).__init__('item', 'main-screen')
        self.other_player_num = other_player_num
    def addedToWorld(self, world):
        super(MainScreen, self).addedToWorld(world)
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
        self.player = serge.blocks.utils.addActorToWorld(
            world,
            player.Player(True, True, self.sock),
            physics = serge.physical.PhysicalConditions(
                mass = 3,
                width = 1,
                height = 2,
                update_angle = True
                ),
            center_position = (300, 300),
            origin = (300, 300),
            )
        # TODO add a condition statement for non-network
        self.olctl = serge.blocks.utils.addActorToWorld(
            world,
            olctlhub.OLControlHub(self.sock)
            )
        self.log.info('Create OLCtl complete with players '+str(self.other_player_num))
        self.log.info(len(world.findActorsByTag('player')))
        while len(world.findActorsByTag('player')) != self.other_player_num + 1:
            data = json.dumps(['request-player'])
            olctlhub.sock.sendto(data, (G('host'), G('port')))
            self.olctl.updateActor(1, world)
        camera = serge.engine.CurrentEngine().renderer.getCamera()
        camera.setTarget(self.player)
        self.bg = serge.blocks.utils.addActorToWorld(
            world,
            bg.Background('bg', 'bg'),
            )
        self.ground = serge.blocks.utils.addActorToWorld(
            world,
            bg.Ground('ground', 'ground'),
            )

def main(other_player_num = 1):
    engine = serge.engine.CurrentEngine()
    engine.setCurrentWorldByName('main-screen')
    world = engine.getWorld('main-screen')
    manager = serge.blocks.behaviours.BehaviourManager('behaviours', 'behaviours')
    world.addActor(manager)
    s = MainScreen(other_player_num)
    world.addActor(s)
