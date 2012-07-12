
"""Main module for the game"""

import pygame
import random

import serge.engine
import serge.world
import serge.actor
import serge.zone
import serge.render
import serge.sound
import serge.common

import serge.blocks.utils

import mainscreen

from theme import G

def registerGraphics():
    """Register the graphics to use"""
    serge.visual.Sprites.setPath('graphics')
    rf = serge.visual.Sprites.registerFromFiles
    r = serge.visual.Sprites.registerItem
    #
    #Now register resources
    #
    #for example
    #
    #   r('bg', 'bg.png')
    #   rf('car-jump', 'car-jump-%d.png', 10, 15, True, loop=False)
    #
    r('default-car', 'default-car.png')
    r('default-background', 'default-track.png')
    r('empty-ground', 'empty-ground.png')

def startEngine():
    engine = serge.engine.Engine(
        width=G('screen-width'),
        height=G('screen-height'),
        title=G('screen-title')
        )
    #
    #Create layers
    serge.blocks.utils.createVirtualLayersForEngine(
    #serge.blocks.utils.createLayersForEngine(
        engine,
        ['background',
         'ground',
         'main',
         'status',
         'message']
        )
    #ground_layer = serge.engine.CurrentEngine().renderer.getLayer('background')
    #ground_layer.clearBeforeUpdate = False
    #
    #Create Worlds
    serge.blocks.utils.createWorldsForEngine(
        engine,
        ['start-screen',
         'main-screen']
        )
    #
    #Set current world
    engine.setCurrentWorldByName('main-screen')
    return engine

def main():
    #
    # register the resources
    registerGraphics()
    #
    # Create the engine
    engine = startEngine()
    #
    # Initialize the main logic
    mainscreen.main()
    #
    # Run the engine
    engine.run(G('framerate'))
