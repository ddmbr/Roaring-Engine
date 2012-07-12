"""The main visual theme"""

import serge.blocks.themes

theme = serge.blocks.themes.Manager()
theme.load({
    'main':('',{
    # global settings
    'screen-height': 640,
    'screen-width': 800,
    'screen-title': 'Roaring Engine',
    'framerate':30,
    # player settings
    'player-x': 320,
    'player-y': 400,
    'player-speed': 5,
    }),
    '__default__':'main'
})
G = theme.getProperty
