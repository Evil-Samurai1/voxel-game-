from ursina import mouse, floor, color, invoke 
from ursina.prefabs.first_person_controller import FirstPersonController
from loguru import logger
import config
from entities.hand import Hand

class Player(FirstPersonController):
    def __init__(self, world, position=(0, 20, 0)):
        super().__init__(
            position=position,
            speed=config.PLAYER_SPEED,
            jump_height=config.PLAYER_JUMP_HIGHT,
            gravity=config.GRAVITY
        )
        self.world = world
        
        self.cursor.texture = 'assets/textures/crosshair.png'
        
        self.cursor.color = color.red
        self.cursor.scale = 0.01
        self.hotbar = ['black_glazed_terracotta', 'bedrock', 'note_block', 'oak_planks', 'crimson_trapdoor']
        self.current_block_index = 0
        self.hand = Hand(self.hotbar[self.current_block_index])
        
        logger.debug(f'player spawned at {position}')
        
    def input(self, key):
        super().input(key)
        
        if key.isdigit() and 1 <= int(key) <= len(self.hotbar):
            self.current_block_index = int(key) - 1
            block_name = self.hotbar[self.current_block_index]
            self.hand.texture = f'{config.TEXTURES_DIR}blocks/{block_name}.png'
            self.hand.texture.filtering = 'nearest'
        
        if key == 'right mouse down' and mouse.hovered_entity:
            wp = mouse.world_point
            norm = mouse.normal
            bx = floor(wp.x + norm.x * 0.5)
            by = floor(wp.y + norm.y * 0.5)
            bz = floor(wp.z + norm.z * 0.5)
            
            block_name = self.hotbar[self.current_block_index]
            
            self.world.set_block(bx, by, bz, block_name)
            self._animate_hand()
            
        if key == 'left mouse down' and mouse.hovered_entity:
            wp = mouse.world_point
            norm = mouse.normal
            bx = floor(wp.x - norm.x * 0.5)
            by = floor(wp.y - norm.y * 0.5)
            bz = floor(wp.z - norm.z * 0.5)
            self.world.set_block(bx, by, bz, None)
            self._animate_hand()
            
    def _animate_hand(self):
        self.hand.active()
        invoke(self.hand.passive, delay = 0.1)