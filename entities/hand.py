from ursina import Entity, camera, Vec2, Vec3
import config

class Hand(Entity):
    def __init__(self, texture_name='dirt'):
        super().__init__(
            parent=camera.ui,
            model='cube',
            texture=f'{config.TEXTURES_DIR}blocks/{texture_name}.png',
            scale=0.3,
            rotation=Vec3(10, -20, 0),
            position=Vec2(0.6, -0.4)
        )
        if self.texture:
            self.texture.filtering = 'nearest'
            
    def active(self):
        self.position = Vec2(0.5, -0.3)
    
    def passive(self):
        self.position = Vec2(0.6, -0.4)