from ursina import Ursina, window, color, Entity, camera, application
from core.texture_builder import build_atlas
from core.chunk_manager import ChunkManager
from entities.player import Player
import config
from loguru import logger
from core.logger import setup_logger

def input(key):
    if key == 'f11':
        window.fullscreen = not window.fullscreen
    if key == 'escape':
        application.quit()

def main():
    setup_logger()
    logger.info('The game have started')
    atlas_data = build_atlas()
    uv_map, grid_size = atlas_data
    
    app = Ursina(
        title=config.WINDOW_TITLE,
        size=(config.WINDOW_WIDTH, config.WINDOW_HIGHT),
        fullscreen=config.FULLSCREEN,
        vsync=config.VSYNC
    )
    camera.backround_color = color.rgb(189, 94, 252)
    window.exit_button.visible = False
    window.fps_counter.enabled = True
    
    world = ChunkManager(uv_map=uv_map, grid_size=grid_size)
    world.generate_initial_world(config.RENDER_DISTANCE)
    
    player = Player(world=world, position=(0, 20, 0))
    
    
    updater = Entity()
    updater.update = lambda: world.update(player.position, config.RENDER_DISTANCE)
    
    app.run()

if __name__ == '__main__':
    main()