
""" This is the handler for all network msg """

import pygame
import random
import math
import socket
import json

import serge.actor
import serge.common
import serge.visual
import serge.blocks.behaviours
import serge.blocks.utils
import serge.blocks.actors

from theme import G

import player

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

class OLControlHub(serge.actor.Actor):
    def __init__(self, sock):
        self.sock = sock
        super(OLControlHub, self).__init__('olctl', 'olctl')
    def updateActor(self, interval, world):
        # TODO will they queued?
        while True:
            try:
                recieved = self.sock.recv(1024, socket.MSG_DONTWAIT)
            except:
                break
            recieved = json.loads(recieved)
            if recieved[1] == 'keys':
                actor = world.findActorByName(recieved[0])
                actor.keys = recieved[2]
            elif recieved[1] == 'create-player':
                self.log.info('have to create player')
                if world.findActorByName(str(recieved[0])) == None:
                    self.log.info('actually create player to', recieved[2])
                    serge.blocks.utils.addActorToWorld(
                        world,
                        player.Player(True, False, self.sock, name = str(recieved[0])),
                        physics = serge.physical.PhysicalConditions(
                            mass = 4,
                            width = 48,
                            height = 64,
                            elasticity = 0.2,
                            friction = 0.02,
                            update_angle = True,
                            ),
                        center_position = recieved[2],
                        origin = recieved[2],
                        )
                    self.log.info('create player '+recieved[0]+' successfully')
                else:
                    self.log.info('but player '+recieved[0]+' created')
            elif recieved[1] == 'adjust-pos':
                p = world.findActorByName(str(recieved[0]))
                if p != None:
                    p.moveTo(*tuple(recieved[2]))
            elif recieved[1] == 'adjust-physical':
                p = world.findActorByName(str(recieved[0]))
                if p == None:
                    self.log.info(str(recieved[0])+' not found')
                p.x, p.y = recieved[2][0], recieved[2][1]
                body = p.physical_conditions.body
                body.angle, body.velocity = recieved[2][2], tuple(recieved[2][3])

def send(data):
    sock.sendto(data, (G('host'), G('port')))
