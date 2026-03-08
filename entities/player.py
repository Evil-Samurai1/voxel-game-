from ursina import mouse, floor, color 
from ursina.prefabs.first_person_controller import FirstPersonController
import config

class Player(FirstPersonController):
    def __init__(self, world, position=(0, 20, 0)):
        super().__init__(
            position=position,
            speed=config.PLAYER_SPEED,
            jump_height=config.PLAYER_JUMP_HIGHT,
            gravity=config.GRAVITY
        )
        self.world = world
        
        self.cursor.color = color.red
        self.cursor.scale = 0.01
        
    def input(self, key):
        super().input(key)
        
        if key == 'right mouse down' and mouse.hovered_entity:
            wp = mouse.world_point
            norm = mouse.normal
            bx = floor(wp.x + norm.x * 0.5)
            by = floor(wp.y + norm.y * 0.5)
            bz = floor(wp.z + norm.z * 0.5)
            self.world.set_block(bx, by, bz, 'stone_briсks')
            
        if key == 'left mouse down' and mouse.hovered_entity:
            wp = mouse.world_point
            norm = mouse.normal
            bx = floor(wp.x - norm.x * 0.5)
            by = floor(wp.y - norm.y * 0.5)
            bz = floor(wp.z - norm.z * 0.5)
            self.world.set_block(bx, by, bz, None)