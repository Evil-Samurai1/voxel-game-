from ursina import Entity, Mesh, floor, Vec3, destroy
from perlin_noise import PerlinNoise
import random
import config

class ChunkManager:
    def __init__(self, uv_map, grid_size, seed=None):
        self.seed = seed or random.randint(1, 10**6)
        self.noise = PerlinNoise(octaves=2, seed=self.seed)
        self.chunk_size = config.CHUNK_SIZE
        
        self.uv_map = uv_map
        self.grid_size = grid_size
        
        self.chunks_data = {} 
        self.chunks_entities = {} 
        
        self.amplitude = 6
        self.frequency = 24
        self.base_height = 10 

        self.block_textures = {
            'grass': {'top': 'stone_bricks', 'bottom': 'dirt', 'sides': 'stone_bricks'}, 
            'dirt': {'top': 'dirt', 'bottom': 'dirt', 'sides': 'dirt'},
            'stone': {'top': 'stone', 'bottom': 'stone', 'sides': 'stone'},
            'grass_block_side': {'top': 'stone_bricks', 'bottom': 'dirt', 'sides': 'stone_bricks'}
        }

    def get_block(self, gx, gy, gz):
        cx = floor(gx / self.chunk_size)
        cz = floor(gz / self.chunk_size)
        
        if (cx, cz) in self.chunks_data:
            return self.chunks_data[(cx, cz)].get((gx, gy, gz))
        return None

    def generate_chunk_data(self, cx, cz):
        if (cx, cz) in self.chunks_data:
            return

        self.chunks_data[(cx, cz)] = {}
        
        for x in range(self.chunk_size):
            for z in range(self.chunk_size):
                gx = cx * self.chunk_size + x
                gz = cz * self.chunk_size + z
                
                noise_val = self.noise([gx / self.frequency, gz / self.frequency])
                y = max(1, int(noise_val * self.amplitude) + self.base_height)
                
                for depth in range(y, -1, -1):
                    block_type = 'grass' if depth == y else 'dirt'
                    self.chunks_data[(cx, cz)][(gx, depth, gz)] = block_type

    def get_uvs(self, block_type):
        if block_type not in self.uv_map:
            return [(0,0), (1,0), (1,1), (0,0), (1,1), (0,1)]
            
        tx, ty = self.uv_map[block_type]
        u_min = tx / self.grid_size
        u_max = (tx + 1) / self.grid_size
        v_min = 1.0 - (ty + 1) / self.grid_size
        v_max = 1.0 - ty / self.grid_size
        
        return [
            (u_min, v_min), (u_max, v_min), (u_max, v_max),
            (u_min, v_min), (u_max, v_max), (u_min, v_max)
        ]

    def get_face_texture(self, block_type, face):
        if block_type in self.block_textures:
            return self.block_textures[block_type].get(face, block_type)
        return block_type

    def build_chunk_mesh(self, cx, cz):
        if (cx, cz) not in self.chunks_data:
            return

        verts, uvs = [], []
        
        for (gx, gy, gz), block_type in self.chunks_data[(cx, cz)].items():
            x = gx % self.chunk_size
            y = gy
            z = gz % self.chunk_size
            
            # (Top)
            if not self.get_block(gx, gy + 1, gz):
                verts.extend([
                    Vec3(x, y+1, z), Vec3(x+1, y+1, z), Vec3(x+1, y+1, z+1),
                    Vec3(x, y+1, z), Vec3(x+1, y+1, z+1), Vec3(x, y+1, z+1)
                ])
                tex = self.get_face_texture(block_type, 'top')
                uvs.extend(self.get_uvs(tex))

            # (Bottom)
            if not self.get_block(gx, gy - 1, gz):
                verts.extend([
                    Vec3(x, y, z+1), Vec3(x+1, y, z+1), Vec3(x+1, y, z),
                    Vec3(x, y, z+1), Vec3(x+1, y, z), Vec3(x, y, z)
                ])
                tex = self.get_face_texture(block_type, 'bottom')
                uvs.extend(self.get_uvs(tex))

            side_tex = self.get_face_texture(block_type, 'sides')

            # (Forward, +Z)
            if not self.get_block(gx, gy, gz + 1):
                verts.extend([
                    Vec3(x+1, y, z+1), Vec3(x, y, z+1), Vec3(x, y+1, z+1),
                    Vec3(x+1, y, z+1), Vec3(x, y+1, z+1), Vec3(x+1, y+1, z+1)
                ])
                uvs.extend(self.get_uvs(side_tex))

            # (Back, -Z)
            if not self.get_block(gx, gy, gz - 1):
                verts.extend([
                    Vec3(x, y, z), Vec3(x+1, y, z), Vec3(x+1, y+1, z),
                    Vec3(x, y, z), Vec3(x+1, y+1, z), Vec3(x, y+1, z)
                ])
                uvs.extend(self.get_uvs(side_tex))

            # (Right, +X)
            if not self.get_block(gx + 1, gy, gz):
                verts.extend([
                    Vec3(x+1, y, z), Vec3(x+1, y, z+1), Vec3(x+1, y+1, z+1),
                    Vec3(x+1, y, z), Vec3(x+1, y+1, z+1), Vec3(x+1, y+1, z)
                ])
                uvs.extend(self.get_uvs(side_tex))

            # (Left, -X)
            if not self.get_block(gx - 1, gy, gz):
                verts.extend([
                    Vec3(x, y, z+1), Vec3(x, y, z), Vec3(x, y+1, z),
                    Vec3(x, y, z+1), Vec3(x, y+1, z), Vec3(x, y+1, z+1)
                ])
                uvs.extend(self.get_uvs(side_tex))

        if not verts:
            if (cx, cz) in self.chunks_entities:
                destroy(self.chunks_entities[(cx, cz)])
                del self.chunks_entities[(cx, cz)]
            return

        new_mesh = Mesh(vertices=verts, uvs=uvs, static=True)
        
        if (cx, cz) in self.chunks_entities:
            chunk_entity = self.chunks_entities[(cx, cz)]
            chunk_entity.model = new_mesh
            chunk_entity.collider = 'mesh' 
        else:
            chunk_entity = Entity(
                model=new_mesh, 
                position=(cx * self.chunk_size, 0, cz * self.chunk_size),
                texture=f'{config.TEXTURES_DIR}atlas.png', 
                collider='mesh'
            )
            if chunk_entity.texture:
                chunk_entity.texture.filtering = 'nearest'
            self.chunks_entities[(cx, cz)] = chunk_entity

    def set_block(self, gx, gy, gz, block_type):
        cx = floor(gx / self.chunk_size)
        cz = floor(gz / self.chunk_size)
        
        if (cx, cz) not in self.chunks_data:
            return 
            
        if block_type is None:
            if (gx, gy, gz) in self.chunks_data[(cx, cz)]:
                del self.chunks_data[(cx, cz)][(gx, gy, gz)]
        else:
            self.chunks_data[(cx, cz)][(gx, gy, gz)] = block_type
            
        self.build_chunk_mesh(cx, cz)
        
        x_in_chunk = gx % self.chunk_size
        z_in_chunk = gz % self.chunk_size
        
        if x_in_chunk == 0: self.build_chunk_mesh(cx - 1, cz)
        if x_in_chunk == self.chunk_size - 1: self.build_chunk_mesh(cx + 1, cz)
        if z_in_chunk == 0: self.build_chunk_mesh(cx, cz - 1)
        if z_in_chunk == self.chunk_size - 1: self.build_chunk_mesh(cx, cz + 1)

    def update(self, player_position, render_distance):
        cx = floor(player_position.x / self.chunk_size)
        cz = floor(player_position.z / self.chunk_size)
        
        for x in range(cx - render_distance, cx + render_distance + 1):
            for z in range(cz - render_distance, cz + render_distance + 1):
                if (x, z) not in self.chunks_data:
                    self.generate_chunk_data(x, z)
                    self.build_chunk_mesh(x, z)
        
        chunks_to_remove = [
            pos for pos in self.chunks_data 
            if abs(pos[0] - cx) > render_distance or abs(pos[1] - cz) > render_distance
        ]
        
        for pos in chunks_to_remove:
            if pos in self.chunks_entities:
                destroy(self.chunks_entities.pop(pos))
            self.chunks_data.pop(pos)

    def generate_initial_world(self, render_distance):
        self.update(Vec3(0, 0, 0), render_distance)