import math
from pathlib import Path
from PIL import Image 
from loguru import logger

def build_atlas(blocks_dir='assets/textures/blocks', output_file='assets/textures/atlas.png', tile_size=64):
    folder = Path(blocks_dir)
    
    if not folder.exists():
        logger.error(f"Directory not found: {blocks_dir}")
        return None
        
    files = sorted(folder.glob('*.png'))
    if not files:
        logger.error(f"No PNG files found in {blocks_dir}")
        return None

    grid_size = math.ceil(math.sqrt(len(files)))
    atlas = Image.new('RGBA', (grid_size * tile_size, grid_size * tile_size), (0, 0, 0, 0))
    uv_map = {}
    
    for i, file_path in enumerate(files):
        with Image.open(file_path) as img:
            img = img.convert('RGBA')
            if img.size != (tile_size, tile_size):
                img = img.resize((tile_size, tile_size), Image.Resampling.NEAREST)

            grid_x, grid_y = i % grid_size, i // grid_size
            atlas.paste(img, (grid_x * tile_size, grid_y * tile_size))
            
            uv_map[file_path.stem] = (grid_x, grid_y)
    
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    atlas.save(output_file)      
    logger.info(f'texture atlas {grid_size}x{grid_size} succsessfule create: {output_file}')
    
    return uv_map, grid_size