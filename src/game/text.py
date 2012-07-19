import serge.visual
import serge.actor

class Text(serge.actor.Actor):
    def __init__(self, content, pos = (0, 0)):
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
        text = serge.visual.Text(self.content, (0xff, 0xff, 0xff), font_size = 18)
        self.setVisual(text)
