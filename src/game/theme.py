"""The main visual theme"""

import serge.blocks.themes

theme = serge.blocks.themes.Manager()
theme.load({
    'main':('',{
    # global settings
    'screen-height': 700,
    'screen-width': 900,
    'screen-title': 'Roaring Engine',
    'framerate':30,
    # player settings
    'player-x': 320,
    'player-y': 400,
    'player-speed': 5,
    # track settings
    'track-height': 2000,
    'track-width': 2000,
    # network settings
    'host': '184.82.236.126',
    'port': 9999,
    }),
    '__default__':'main'
})
G = theme.getProperty
