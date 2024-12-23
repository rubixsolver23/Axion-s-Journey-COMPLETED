import pygame
from pygame.locals import *
import os, sys
import random, math

# Make a UML diagram of all the classes
# Classes like:
'''
Block, which has children like PlayerBlock and LavaBlock
Camera, associated with PlayerBlock 
LevelEditor, which is associated with camera
Level, which has blocks in it
Particle
SoundManager
'''


class Game:
    def __init__(self):
        self.camera = Camera(None, 1)
        self.level_idx = 0

    def move_camera_to_player(self, x, y, boundaries):
        move_x = (x - self.camera.pos[0] - 300) / 10
        move_y = (y - self.camera.pos[1] - 300) / 10
        self.camera.move_camera([move_x, move_y], boundaries)



class LevelManager:
    def __init__(self):
        self.camera = Camera(None, None)

    def create_empty_level(self, id, dimensions):
        level_list = []
        level_list += ["B"] * dimensions[0] # top of box
        level_list += ((["B"] + [" "] * (dimensions[0]-2) + ["B"]) * (dimensions[1]-2)) # walls and middle of box
        level_list += ["B"] * dimensions[0] # bottom of box
        



        return Level(id, {
            "width": dimensions[0],
            "height": dimensions[1],
            "blocklist": level_list
        }, 20, {})
    
    def save_all(self, list_of_levels):
        print("Saving...")
        i=0
        for level in list_of_levels:
            l_dict = level.level_dict
            l_width = l_dict["width"]
            l_height = l_dict["height"]
            l_list = "".join(l_dict["blocklist"])

            l_messages = {}
            for text_block in level.text_blocks:
                l_messages[text_block.idx] = text_block.message.message
            
            l_write = str(l_width) + "," + str(l_height) + "," + l_list

            for key in l_messages:
                l_write += f"`{key}[{l_messages[key]}]"

            level_file = open("levels/level-"+str(i)+".axj", "w")
            level_file.write(l_write)
            level_file.close()
            i += 1

        print("Levels saved!")

    def load_all(self):

        levels = []

        level_dir = "levels"
        id=0
        for file in os.listdir(level_dir):
            if ".axj" in file:
                lvl_file = open("levels/"+file, "r")
                lvl_txt = lvl_file.read()
                width = ""
                for char in lvl_txt:
                    if char == ",":
                        break
                    width += char
                lvl_txt = lvl_txt[len(width)+1:]
                    
                width = int(width)
                height = ""
                for char in lvl_txt:
                    if char == ",":
                        break
                    height += char
                lvl_txt = lvl_txt[len(height)+1:]
                height = int(height)
                lvl_list = list(lvl_txt[:width*height])
                lvl_txt = lvl_txt[width*height:]

                messages = {}
                idx = ""
                msg = ""
                mode=0
                for char in lvl_txt:
                    if char == "`":
                        mode = 1
                    elif mode == 1:
                        if char == "[":
                            mode = 2
                            continue
                        idx += char
                    elif mode == 2:
                        if char == "]":
                            mode = 0
                            messages[int(idx)] = msg
                            idx = ""
                            msg = ""
                            continue
                        msg += char

                levels.append(Level(
                    id,
                    {
                        "width": width,
                        "height": height,
                        "blocklist": lvl_list
                    },
                    20,
                    messages
                    ))
                
                id+=1


        return levels

    def add_level(self, level_idx):

        while True:
            try:
                width = int(input("What should the width of the new level be?: ").strip())
                break
            except ValueError:
                print("That's not a valid integer.")
        
        while True:
            try:
                height = int(input("What should the height of the new level be?: ").strip())
                break
            except ValueError:
                print("That's not a valid integer.")
        
        return self.create_empty_level(level_idx, [width, height])




class Level:
    def __init__(self, id, level_dict, block_size, messages):
        self.id = id
        self.level_dict = level_dict
        self.block_object_list = []
        self.block_size = block_size
        self.player_objects = []
        self.particles = []

        self.fog_blocks = []
        self.fog_idxes = []
        self.live_fog_blocks = []
        self.queued_fog = []
        self.fog_cooldown = 14

        self.text_blocks = []
        self.messages = messages
        self.is_writing = False

        self.create_block_objects()

    def create_block_objects(self):
        self.block_object_list = []
        self.player_objects = []
        self.fog_blocks = []
        self.text_blocks = []
        width = self.level_dict["width"]
        for idx, block in enumerate(self.level_dict["blocklist"]):
            if block == "B":
                block_hitbox = pygame.Rect(0, 0, self.block_size, self.block_size)
                self.block_object_list.append(RegBlock(idx%width, idx//width, block_hitbox, self.block_size, idx))
            elif block == "P":
                block_hitbox = pygame.Rect(0, 0, self.block_size, self.block_size)
                char = pygame.Rect(0, 0, self.block_size, self.block_size)
                new_player = PlayerBlock(self.block_size*(idx%width), self.block_size*(idx//width), block_hitbox, self.block_size, char, idx)
                self.player_objects.append(new_player)
            elif block == "C":
                block_hitbox = pygame.Rect(0, 0, self.block_size, self.block_size)
                checkpoint = CheckpointBlock(idx%width, idx//width, block_hitbox, self.block_size, idx)
                self.block_object_list.append(checkpoint)
            elif block == "J":
                block_hitbox = pygame.Rect(0, 0, 10, 10)
                self.block_object_list.append(AirJumpBlock(idx%width, idx//width, block_hitbox, idx))
            elif block == "X":
                block_hitbox = pygame.Rect(0, 0, self.block_size, self.block_size)
                self.block_object_list.append(DangerBlock(idx%width, idx//width, block_hitbox, self.block_size, idx))
            elif block == "Z":
                block_hitbox = pygame.Rect(0, 0, self.block_size, self.block_size)
                self.block_object_list.append(ExitBlock(idx%width, idx//width, block_hitbox, self.block_size, idx))
            elif block == "F":
                block_hitbox = pygame.Rect(0, 0, self.block_size, self.block_size)
                block = FogBlock(idx%width, idx//width, block_hitbox, self.block_size, idx)
                self.fog_blocks.append(block)
                self.live_fog_blocks.append(block)
                self.fog_idxes.append(idx)
            elif block == "N":
                self.add_story_block(idx, width)

            elif block == "O":
                block_hitbox = pygame.Rect(0, 0, self.block_size, self.block_size)
                self.block_object_list.append(WindBlock(idx%width, idx//width, block_hitbox, self.block_size, "up", idx))
            elif block == "L":
                block_hitbox = pygame.Rect(0, 0, self.block_size, self.block_size)
                self.block_object_list.append(WindBlock(idx%width, idx//width, block_hitbox, self.block_size, "down", idx))
            elif block == "K":
                block_hitbox = pygame.Rect(0, 0, self.block_size, self.block_size)
                self.block_object_list.append(WindBlock(idx%width, idx//width, block_hitbox, self.block_size, "left", idx))
            elif block == ";":
                block_hitbox = pygame.Rect(0, 0, self.block_size, self.block_size)
                self.block_object_list.append(WindBlock(idx%width, idx//width, block_hitbox, self.block_size, "right", idx))
            
    
    def get_str_of_blocks(self):
        return "".join(self.level_dict["blocklist"])
    
    def get_player_object(self):
        if self.player_objects != []:
            return self.player_objects[0]
        else:
            return None
    
    def spread_fog(self, cooldown):
        if self.fog_cooldown == 0:
            for block in self.live_fog_blocks:
                block.live = False
                block.spread(self)
            self.live_fog_blocks = []
            self.create_fog()
            self.fog_cooldown = cooldown
        else:
            self.fog_cooldown -= 1

    def add_fog(self, idx):
        width = self.level_dict["width"]
        block_hitbox = pygame.Rect(0, 0, self.block_size, self.block_size)
        block = FogBlock(idx%width, idx//width, block_hitbox, self.block_size, idx)
        self.queued_fog.append(block)
        self.fog_blocks.append(block)
        self.fog_idxes.append(idx)
    
    def create_fog(self):
        self.live_fog_blocks += self.queued_fog
        self.queued_fog = []

    def add_story_block(self, idx, width):
        block_hitbox = pygame.Rect(0, 0, self.block_size, self.block_size)
        try:
            self.text_blocks.append(TextBlock(idx%width, idx//width, block_hitbox, self.block_size, self.messages[idx], idx))
        except KeyError:
            message = input("What message should this block have? (34 Characters to a line): ")
            self.text_blocks.append(TextBlock(idx%width, idx//width, block_hitbox, self.block_size, message, idx))
            self.messages[idx] = message
        
    def clear_dead_particles(self):
        new_list = []
        for particle in self.particles:
            if particle.lifetime > 0:
                new_list.append(particle)
        self.particles = new_list

    def death_particles(self, player):
        for i in range(50):
            self.particles.append(Particle(player.x, player.y, "death"))
    
    def danger_particle(self, x, y):
        self.particles.append(Particle(x, y, "danger"))

    def walk_particle(self, player, direction, color):
        p_x = int(player.x)
        p_y = int(player.y)
        if direction == 1:
            self.particles.append(Particle(random.randint(p_x, p_x+17), random.randint(p_y, p_y+17), "left", color))
        elif direction == -1:
            self.particles.append(Particle(random.randint(p_x, p_x+17), random.randint(p_y, p_y+17), "right", color))
    
    def exit_particle(self, x, y, color):
        self.particles.append(Particle(x, y, "exit", color))

    def airjump_particle(self, x, y):
        self.particles.append(Particle(x, y, "airjump"))

    def wind_particle(self, x, y, direction):
        self.particles.append(Particle(x, y, "wind-"+direction))

    def fog_particle(self, x, y):
        self.particles.append(Particle(x, y, "fog"))

    def reset(self):
        self.block_object_list = []
        self.player_objects = []
        self.particles = []

        self.fog_blocks = []
        self.fog_idxes = []
        self.live_fog_blocks = []
        self.queued_fog = []
        self.fog_cooldown = 14

        self.create_block_objects()


class LevelEditor:
    def __init__(self):
        self.camera = Camera({"up": K_w, "down": K_s, "left": K_a, "right": K_d}, 5)
        self.tile_num = 0
        self.level_idx = 0
        self.brush = "B"

    def add_block(self, level):
        level.level_dict["blocklist"][self.tile_num] = self.brush
        level.create_block_objects()
    
    def change_brush(self, new_brush):
        self.brush = new_brush




class Block:
    def __init__(self, x, y, color, hitbox, blocksize, idx):
        self.x = x
        self.y = y
        self.color = color
        self.hitbox = hitbox
        self.blocksize = blocksize
        self.idx = idx

    def pos_block(self, camera_pos):
        self.hitbox.left = self.x*self.blocksize - camera_pos[0]
        self.hitbox.top = self.y*self.blocksize - camera_pos[1]

    def render(self, windowSurface, camera_pos):
        if self.x*20 + 30 > camera_pos[0] and self.x*20 < camera_pos[0] + 610 and self.y*20 + 30 > camera_pos[1] and self.y*20 < camera_pos[1] + 610:
            pygame.draw.rect(windowSurface, self.color, self.hitbox)



class PlayerBlock(Block):
    def __init__(self, x, y, hitbox, blocksize, character, idx):
        super().__init__(x, y, [80,80,255], hitbox, blocksize, idx)

        self.character = character

        self.GRAVITY = 0.25
        self.WALKSPEED = 1.5
        self.AIRSPEED = 0.5
        self.JUMPHEIGHT = 5.5
        self.AIRJUMPHEIGHT = 7
        self.TERMINALVELOCITY = 10
        self.COYOTETIME = 6
        self.FRICTION = 0.7
        self.AIRFRICTION = 0.9

        self.JUMPBUTTONS = [K_w, K_UP, K_SPACE]
        self.LEFTBUTTONS = [K_a, K_LEFT]
        self.RIGHTBUTTONS = [K_d, K_RIGHT]

        self.ZERO_COLOR = [144, 166, 173]
        self.ONE_COLOR = [80,80,255]
        self.TWO_COLOR = [34, 240, 109]
        self.MORE_COLOR = [240, 34, 219]
        
        self.released_jump = True
        self.velocity = [0,0]
        self.airtime = 0
        self.airjumps = 1

        self.checkpoint_x = x
        self.checkpoint_y = y
        
        self.particle_timer = 0
        self.dead = 0

        self.wind_push = {"up": False, "down": False, "left": False, "right": False}

        self.width = 20
        self.height = 20

    def main_loop(self, buttons_pressed, level, death_event, finish_event, fog_event):
        self.fall()
        self.walk(buttons_pressed, level)
        self.jump(buttons_pressed)
        self.pushed_by_wind()
        self.update_pos(level)
        self.get_touching_wind(level)
        self.squarify()
        self.check_touching_danger(level, death_event)
        self.get_in_fog(level, fog_event)
        self.check_exit(level, finish_event)

    def fall(self):
        self.velocity[1] += self.GRAVITY
        if self.velocity[1] >= self.TERMINALVELOCITY:
            self.velocity[1] = self.TERMINALVELOCITY
        self.airtime += 1

    def walk(self, buttons_pressed, level):
        key_walk = 0
        for button in self.LEFTBUTTONS:
            if buttons_pressed[button]:
                key_walk -= 1
                break
        for button in self.RIGHTBUTTONS:
            if buttons_pressed[button]:
                key_walk += 1
                break
        
        if self.airtime < 3:
            self.velocity[0] += key_walk * self.WALKSPEED
            self.velocity[0] *= self.FRICTION
        else:
            self.velocity[0] += key_walk * self.AIRSPEED
            self.velocity[0] *= self.AIRFRICTION
        if abs(self.velocity[0]) < 0.1:
            self.velocity[0] = 0
        if key_walk != 0:
            if self.particle_timer == 0:
                level.walk_particle(self, key_walk, self.color)
                self.particle_timer = 1
            else:
                self.particle_timer -= 1
        

    def jump(self, buttons_pressed):
        for button in self.JUMPBUTTONS:
            if buttons_pressed[button]:
                if self.airtime < self.COYOTETIME:
                    self.velocity[1] = -self.JUMPHEIGHT
                    self.released_jump = False
                    self.stretch(False)
                elif self.airjumps > 0 and self.released_jump:
                    self.velocity[1] = -self.AIRJUMPHEIGHT
                    self.airjumps -= 1
                    self.released_jump = False
                    self.stretch(True)
                break
        else:
            self.released_jump = True

    def detect_wall(self, level):
        if self.get_tile_at(self.x, self.y, level) == "B" or self.get_tile_at(self.x, self.y+19.99, level) == "B" or self.get_tile_at(self.x+19.99, self.y, level) == "B" or self.get_tile_at(self.x+19.99, self.y+19.99, level) == "B":
            if self.velocity[0] > 0:
                self.x -= (self.x % 20)
            else:
                self.x += 20-(self.x % 20)
            self.velocity[0] = 0


    def detect_floor_ceiling(self, level):
        if self.get_tile_at(self.x, self.y, level) == "B" or self.get_tile_at(self.x, self.y+19.99, level) == "B" or self.get_tile_at(self.x+19.99, self.y, level) == "B" or self.get_tile_at(self.x+19.99, self.y+19.99, level) == "B":
            if self.velocity[1] > 0:
                self.y -= (self.y % 20)
                if self.airtime > 2:
                    self.squish()
                self.airtime = 0
                self.airjumps = 1
            else:
                self.y += 20-(self.y % 20)
            self.velocity[1] = 0
            

    def stretch(self, is_air_jump):
        if is_air_jump:
            self.width -= 13
            self.height += 13
            while self.width < 7:
                self.width += 1
                self.height -= 1
                self.character.inflate_ip(1, -1)
            self.character.inflate_ip(-13, 13)
        else:
            self.width -= 6
            self.height += 6
            while self.width < 14:
                self.width += 1
                self.height -= 1
                self.character.inflate_ip(1, -1)
            self.character.inflate_ip(-6, 6)

    def squish(self):
        amount = int(self.velocity[1])
        self.width += amount
        self.height -= amount
        while self.width > 20 + amount:
            self.width -= 1
            self.height += 1
            self.character.inflate_ip(-1, 1)
        self.character.inflate_ip(amount, -amount)

    def squarify(self):
        if self.width < 20:
            self.width += 1
            self.height -= 1
            self.character.inflate_ip(1, -1)
        elif self.width > 20:
            self.width -= 1
            self.height += 1
            self.character.inflate_ip(-1, 1)

    def get_touching_wind(self, level):
        self.wind_push["up"] = self.get_tile_at(self.x, self.y, level) == "O" or self.get_tile_at(self.x, self.y+19.99, level) == "O" or self.get_tile_at(self.x+19.99, self.y, level) == "O" or self.get_tile_at(self.x+19.99, self.y+19.99, level) == "O"
        self.wind_push["down"] = self.get_tile_at(self.x, self.y, level) == "L" or self.get_tile_at(self.x, self.y+19.99, level) == "L" or self.get_tile_at(self.x+19.99, self.y, level) == "L" or self.get_tile_at(self.x+19.99, self.y+19.99, level) == "L"
        self.wind_push["left"] = self.get_tile_at(self.x, self.y, level) == "K" or self.get_tile_at(self.x, self.y+19.99, level) == "K" or self.get_tile_at(self.x+19.99, self.y, level) == "K" or self.get_tile_at(self.x+19.99, self.y+19.99, level) == "K"
        self.wind_push["right"] = self.get_tile_at(self.x, self.y, level) == ";" or self.get_tile_at(self.x, self.y+19.99, level) == ";" or self.get_tile_at(self.x+19.99, self.y, level) == ";" or self.get_tile_at(self.x+19.99, self.y+19.99, level) == ";"

    def get_in_fog(self, level, fog_event):
        if self.get_tile_num_at(self.x, self.y, level) in level.fog_idxes and self.get_tile_num_at(self.x, self.y+19.99, level) in level.fog_idxes and self.get_tile_num_at(self.x+19.99, self.y, level) in level.fog_idxes and self.get_tile_num_at(self.x+19.99, self.y+19.99, level) in level.fog_idxes:
            pygame.event.post(pygame.event.Event(fog_event))

    def pushed_by_wind(self):
        if self.wind_push["up"]:
            self.velocity[1] -= 0.5
        if self.wind_push["down"]:
            self.velocity[1] += 0.3
        if self.wind_push["left"]:
            self.velocity[0] -= 0.55
        if self.wind_push["right"]:
            self.velocity[0] += 0.55

            
    def update_pos(self, level):
        self.y += self.velocity[1]
        self.detect_floor_ceiling(level)
        self.x += self.velocity[0]
        self.detect_wall(level)
        

    def pos_block(self, camera_pos):
        self.hitbox.left = self.x - camera_pos[0]
        self.hitbox.top = self.y - camera_pos[1]
        self.character.midbottom = self.hitbox.midbottom

    def reset_to_checkpoint(self):
        self.x = self.checkpoint_x
        self.y = self.checkpoint_y
        self.airtime = 0
        self.airjumps = 1
        self.velocity = [0, 0]

    def check_touching_danger(self, level, event):
        if self.get_tile_at(self.x, self.y, level) == "X" or self.get_tile_at(self.x, self.y+19.99, level) == "X" or self.get_tile_at(self.x+19.99, self.y, level) == "X" or self.get_tile_at(self.x+19.99, self.y+19.99, level) == "X":
            pygame.event.post(pygame.event.Event(event))
            self.dead = 120

    def check_exit(self, level, event):
        if self.get_tile_at(self.x, self.y, level) == "Z" or self.get_tile_at(self.x, self.y+19.99, level) == "Z" or self.get_tile_at(self.x+19.99, self.y, level) == "Z" or self.get_tile_at(self.x+19.99, self.y+19.99, level) == "Z":
            pygame.event.post(pygame.event.Event(event))


    def render(self, windowSurface, camera_pos):
        if self.airjumps == 0:
            self.color = self.ZERO_COLOR.copy()
        elif self.airjumps == 1:
            self.color = self.ONE_COLOR.copy()
        elif self.airjumps == 2:
            self.color = self.TWO_COLOR.copy()
        elif self.airjumps >= 3:
            self.color = self.MORE_COLOR.copy()
        pygame.draw.rect(windowSurface, self.color, self.character)


    @staticmethod
    def get_tile_at(x, y, level):
        tile_x = int(x/20)
        tile_y = int(y/20)
        tile_idx = tile_x + tile_y*level.level_dict["width"]
        return level.level_dict["blocklist"][tile_idx]
    
    @staticmethod
    def get_tile_num_at(x, y, level):
        tile_x = int(x/20)
        tile_y = int(y/20)
        tile_idx = tile_x + tile_y*level.level_dict["width"]
        return tile_idx



class RegBlock(Block):
    def __init__(self, x, y, hitbox, blocksize, idx):
        super().__init__(x, y, (0,0,0), hitbox, blocksize, idx)

class DangerBlock(Block):
    def __init__(self, x, y, hitbox, blocksize, idx):
        super().__init__(x, y, (255,40,121), hitbox, blocksize, idx)
        self.particle_timer = 5

    def particles(self, level, camera_pos):
        if self.particle_timer == 0:
            block_above = level.level_dict["blocklist"][self.idx-level.level_dict["width"]]
            if self.x*20 + 30 > camera_pos[0] and self.x*20 < camera_pos[0] + 610 and self.y*20 + 40 > camera_pos[1] and self.y*20 < camera_pos[1] + 620 and block_above != "X" and block_above != "B" and not self.idx in level.fog_idxes:
                x = random.randint(self.x*20, self.x*20 + 17)
                y = random.randint(self.y*20, self.y*20 + 10)
                level.danger_particle(x, y)
                self.particle_timer = 5
        else:
            self.particle_timer -= 1

class ExitBlock(Block):
    def __init__(self, x, y, hitbox, blocksize, idx):
        super().__init__(x, y, [255, 0, 0], hitbox, blocksize, idx)
        self.particle_timer = 0

    def change_color(self):
        if self.color[0] > 0 and self.color[1] < 255 and self.color[2] == 0:
            self.color[1] += 5

        elif self.color[0] > 0 and self.color[1] == 255:
            self.color[0] -= 5

        elif self.color[1] > 0 and self.color[2] < 255:
            self.color[2] += 5

        elif self.color[1] > 0 and self.color[2] == 255:
            self.color[1] -= 5

        elif self.color[2] > 0 and self.color[0] < 255:
            self.color[0] += 5

        elif self.color[2] > 0 and self.color[0] == 255:
            self.color[2] -= 5
    
    def particles(self, level, camera_pos):
        if self.particle_timer == 0:
            if self.x*20 + 30 > camera_pos[0] and self.x*20 < camera_pos[0] + 610 and self.y*20 + 40 > camera_pos[1] and self.y*20 < camera_pos[1] + 620:
                x = self.x*20+10
                y = self.y*20+10
                level.exit_particle(x, y, self.color)
                self.particle_timer = 2
        else:
            self.particle_timer -= 1
    
class CheckpointBlock(Block):
    def __init__(self, x, y, hitbox, blocksize, idx):
        super().__init__(x, y, (0, 0, 0), hitbox, blocksize, idx)
        self.claimed = False
        self.color = [0, 100, 0]
        self.buffer = 0

    def claim(self, player, event):
        pygame.event.post(pygame.event.Event(event))
        self.color = [10, 255, 50]
        player.checkpoint_x = self.p_x
        player.checkpoint_y = self.p_y
        self.buffer = 2

    def declaim(self):
        if self.buffer == 0:
            self.color = [0, 100, 0]
            self.claimed = False

    def check_touching_player(self, player, event):
        self.get_pixel_coords()
        if not self.buffer == 0:
            self.buffer -= 1
        if (player.x < self.p_x + 19 and player.x > self.p_x - 19) and (player.y < self.p_y + 19 and player.y > self.p_y - 19):
            if not self.claimed:
                self.claim(player, event)
    
    def get_pixel_coords(self):
        self.p_x = self.x * 20
        self.p_y = self.y * 20
    
class AirJumpBlock(Block):
    def __init__(self, x, y, hitbox, idx):
        super().__init__(x, y, (255,175,0), hitbox, 10, idx)
        self.claimed_frames = 0
        self.particle_timer = 0
    
    def pos_block(self, camera_pos):
        self.hitbox.left = self.x*20+5 - camera_pos[0]
        self.hitbox.top = self.y*20+5 - camera_pos[1]
    
    def render(self, windowSurface, camera_pos):
        if self.claimed_frames > 0:
            self.claimed_frames -= 1
        else:
            self.claimed_frames = 0
            pygame.draw.rect(windowSurface, self.color, self.hitbox)

    def claim(self, player):
        player.airjumps += 1
        self.claimed_frames = 120
    
    def check_touching_player(self, player):
        self.get_pixel_coords()
        if (player.x < self.p_x + 9 and player.x > self.p_x - 19) and (player.y < self.p_y + 9 and player.y > self.p_y - 19):
            if self.claimed_frames == 0:
                self.claim(player)

    def get_pixel_coords(self):
        self.p_x = self.x * 20 + 5
        self.p_y = self.y * 20 + 5

    def particles(self, camera_pos, level):
        if self.particle_timer == 0:
            if self.x*20 + 30 > camera_pos[0] and self.x*20 < camera_pos[0] + 610 and self.y*20 + 40 > camera_pos[1] and self.y*20 < camera_pos[1] + 620 and self.claimed_frames == 0 and not self.idx in level.fog_idxes:
                x = self.x*20+10
                y = self.y*20+10
                level.airjump_particle(x, y)
                self.particle_timer = 2
        else:
            self.particle_timer -= 1

class FogBlock(Block):
    def __init__(self, x, y, hitbox, blocksize, idx):
        super().__init__(x, y, (50,0,22), hitbox, blocksize, idx)
        self.live = True
        self.particle_timer = 1

    def spread(self, level):
        self.live = False
        assert isinstance(level, Level)
        level_list = level.level_dict["blocklist"]

        idx_above = self.idx - level.level_dict["width"]
        idx_below = self.idx + level.level_dict["width"]
        idx_right = self.idx + 1
        idx_left = self.idx - 1

        if level_list[idx_above] != "B" and not (idx_above in level.fog_idxes):
            level.add_fog(idx_above)
        if level_list[idx_below] != "B" and not (idx_below in level.fog_idxes):
            level.add_fog(idx_below)
        if level_list[idx_left] != "B" and not (idx_left in level.fog_idxes):
            level.add_fog(idx_left)
        if level_list[idx_right] != "B" and not (idx_right in level.fog_idxes):
            level.add_fog(idx_right)
        
    def particles(self, level, camera_pos):
        if self.particle_timer == 0:
            if self.x*20 + 30 > camera_pos[0] and self.x*20 < camera_pos[0] + 610 and self.y*20 + 40 > camera_pos[1] and self.y*20 < camera_pos[1] + 620:
                x = self.x*20+10
                y = self.y*20+10
                level.fog_particle(x, y)
                self.particle_timer = 2
        else:
            self.particle_timer -= 1

    def render(self, windowSurface, camera_pos):
        super().render(windowSurface, camera_pos)


class TextBlock(Block):
    def __init__(self, x, y, hitbox, blocksize, message, idx):
        super().__init__(x, y, (250, 250, 150), hitbox, blocksize, idx)
        self.message = Paragraph(message)
        self.is_writing = False
        self.drawing_text = 0
        self.prompt_font = pygame.font.Font("fonts/PixelSplitter-Bold.ttf", 15)
    
    def check_touching_player(self, player):
        self.get_pixel_coords()
        if (player.x < self.p_x + 19 and player.x > self.p_x - 19) and (player.y < self.p_y + 19 and player.y > self.p_y - 19):
            return True
    
    def get_pixel_coords(self):
        self.p_x = self.x * 20
        self.p_y = self.y * 20
    
    def draw_prompt(self, camera_pos, screen):
        press_e = self.prompt_font.render("Press E", False, (100, 100, 100), None)
        press_e_rect = press_e.get_rect()
        pos_x = self.p_x - camera_pos[0]
        pos_y = self.p_y - camera_pos[1]
        press_e_rect.centerx = pos_x + 10
        press_e_rect.centery = pos_y - 20
        screen.blit(press_e, press_e_rect)

class WindBlock(Block):
    def __init__(self, x, y, hitbox, blocksize, direction, idx):
        super().__init__(x, y, (247, 247, 247), hitbox, blocksize, idx)
        self.direction = direction
        self.particle_timer = 0

        if self.direction == "up":
            self.color = (247, 255, 247)
        elif self.direction == "down":
            self.color = (255, 247, 247)
        elif self.direction == "left":
            self.color = (247, 247, 255)
        else:
            self.color = (255, 255, 247)
    
    def particles(self, level, camera_pos):
        if self.particle_timer == 0:
            if self.x*20 + 30 > camera_pos[0] and self.x*20 < camera_pos[0] + 610 and self.y*20 + 40 > camera_pos[1] and self.y*20 < camera_pos[1] + 620 and not self.idx in level.fog_idxes:
                x = random.randint(self.x*20, self.x*20 + 17)
                y = random.randint(self.y*20, self.y*20 + 10)
                level.wind_particle(x, y, self.direction)
                self.particle_timer = 10
        else:
            self.particle_timer -= 1
        


class Paragraph:
    def __init__(self, message):
        self.message = message
        self.frames_per_letter = 4
        self.font = pygame.font.Font("fonts/Pixellari.ttf", 30)

    def create_text(self, frames):
        idx = 0
        full_message = []
        string = ""
        while idx < frames and idx < len(self.message)*self.frames_per_letter:
            if idx/self.frames_per_letter == int(idx/self.frames_per_letter):
                if self.message[int(idx/self.frames_per_letter)] == "~":
                    pass
                elif self.message[int(idx/self.frames_per_letter)] == "<":
                    full_message.append(string)
                    string = ""
                else:
                    string += self.message[int(idx/self.frames_per_letter)]
            idx += 1
        full_message.append(string)
        return full_message
    
    def draw_text(self, frames, screen):
        text = self.create_text(frames)
        full_rect = pygame.rect.Rect(0, 450, 600, 150)
        mid_rect = pygame.rect.Rect(10, 460, 580, 130)
        center_rect = pygame.rect.Rect(20, 470, 560, 110)

        text_surf1 = self.font.render(text[0], False, (0, 0, 0))
        text_rect1 = text_surf1.get_rect()
        text_rect1.left = 30
        text_rect1.top = 480

        if len(text) > 1:
            text_surf2 = self.font.render(text[1], False, (0, 0, 0))
            text_rect2 = text_surf2.get_rect()
            text_rect2.left = 30
            text_rect2.top = 510

        if len(text) > 2:
            text_surf3 = self.font.render(text[2], False, (0, 0, 0))
            text_rect3 = text_surf3.get_rect()
            text_rect3.left = 30
            text_rect3.top = 540


        pygame.draw.rect(screen, (0, 0, 0), full_rect)
        pygame.draw.rect(screen, (100, 100, 100), mid_rect)
        pygame.draw.rect(screen, (255, 255, 255), center_rect)
        screen.blit(text_surf1, text_rect1)
        if len(text) > 1:
            screen.blit(text_surf2, text_rect2)
        if len(text) > 2:
            screen.blit(text_surf3, text_rect3)




class Particle:
    def __init__(self, x, y, type, color=None):
        self.type = type
        self.x = x
        self.y = y
        if self.type == "death":
            self.velocity = [random.random()*10-5, random.random()*10-7]
            self.color = [255, 0, 0]
            self.gravity = 0.25
            self.hitbox = pygame.rect.Rect(0, 0, 3, 3)
            self.lifetime = 120

            self.update()

        elif self.type == "danger":
            self.velocity = [0, -1]
            self.color = [255, 40, 121]
            self.hitbox = pygame.rect.Rect(0, 0, 3, 3)
            self.lifetime = 40

        elif self.type == "left":
            self.velocity = [-1, 0]
            self.color = color
            self.hitbox = pygame.rect.Rect(0, 0, 3, 3)
            self.lifetime = 40
        elif self.type == "right":
            self.velocity = [1, 0]
            self.color = color
            self.hitbox = pygame.rect.Rect(0, 0, 3, 3)
            self.lifetime = 40

        elif self.type == "exit":
            self.velocity = [random.random()*3-1.5, random.random()*3-1.5]
            self.color = color
            self.hitbox = pygame.rect.Rect(0, 0, 3, 3)
            self.lifetime = 40

        elif self.type == "airjump":
            self.velocity = [random.random()*2-1, random.random()*2-1]
            self.color = (255,175,0)
            self.hitbox = pygame.rect.Rect(0, 0, 3, 3)
            self.lifetime = 20

        elif "wind" in self.type:
            self.speed = 0.1
            self.amplitude = 10
            self.lifetime = 100
            self.hitbox = pygame.rect.Rect(0, 0, 3, 3)
            self.color = (210, 210, 210)
            if "up" in self.type:
                self.velocity = [0, -1]
                self.consistant_x = x

            elif "down" in self.type:
                self.velocity = [0, 1]
                self.consistant_x = x

            elif "right" in self.type:
                self.velocity = [1, 0]
                self.consistant_y = y

            elif "left" in self.type:
                self.velocity = [-1, 0]
                self.consistant_y = y
        
        elif self.type == "fog":
            self.velocity = [random.random()*3-1.5, random.random()*3-1.5]
            self.color = (50, 0, 21)
            self.hitbox = pygame.rect.Rect(0, 0, 3, 3)
            self.lifetime = 40

    
    def update(self):
        if self.type == "death":
            self.x += self.velocity[0]
            self.y += self.velocity[1]
            self.velocity[1] += self.gravity
            self.lifetime -= 1
        elif self.type == "danger":
            self.y += self.velocity[1]
            self.velocity[1] *= 0.95
            self.lifetime -= 1
        elif self.type == "right" or self.type == "left":
            self.x += self.velocity[0]
            self.velocity[0] *= 0.98
            self.lifetime -= 1
        elif self.type == "exit" or self.type == "airjump" or self.type == "fog":
            self.x += self.velocity[0]
            self.y += self.velocity[1]
            self.velocity[0] *= 0.95
            self.velocity[1] *= 0.95
            self.lifetime -= 1
        elif "wind" in self.type:
            if "up" in self.type or "down" in self.type:
                self.y += self.velocity[1]
                self.x = self.consistant_x + self.amplitude * math.sin(self.speed * self.lifetime)
                self.lifetime -= 1
            if "left" in self.type or "right" in self.type:
                self.x += self.velocity[0]
                self.y = self.consistant_y + self.amplitude * math.sin(self.speed * self.lifetime)
                self.lifetime -= 1


    def pos_particle(self, camera_pos):
        self.hitbox.left = self.x - camera_pos[0]
        self.hitbox.top = self.y - camera_pos[1]

    def kill_wind_particle(self, level):
        tile_x = int(self.x/20)
        tile_y = int(self.y/20)
        tile_idx = tile_x + tile_y*level.level_dict["width"]
        if "up" in self.type:
            if level.level_dict["blocklist"][tile_idx] != "O":
                level.particles.remove(self)
        elif "down" in self.type:
            if level.level_dict["blocklist"][tile_idx] != "L":
                level.particles.remove(self)
        elif "left" in self.type:
            if level.level_dict["blocklist"][tile_idx] != "K":
                level.particles.remove(self)
        elif "right" in self.type:
            if level.level_dict["blocklist"][tile_idx] != ";":
                level.particles.remove(self)

    def render(self, surface):
        if self.lifetime > 0:
            pygame.draw.rect(surface, self.color, self.hitbox)




class Camera():
    def __init__(self, move_buttons, speed):
        self.real_pos = [0, 0]
        self.pos = [0, 0]
        self.move_buttons = move_buttons
        self.speed = speed
        self.screenshake_intensity = 0


    def move_camera(self, movement, boundaries):
        self.real_pos[0] += movement[0]
        self.real_pos[1] += movement[1]
        if self.real_pos[0] < 0:
            self.real_pos[0] = 0
        if self.real_pos[1] < 0:
            self.real_pos[1] = 0
        if self.real_pos[0] > boundaries[0] - 600:
            self.real_pos[0] = boundaries[0] - 600
        if self.real_pos[1] > boundaries[1] - 600:
            self.real_pos[1] = boundaries[1] - 600
    
    def screenshake(self):
        self.pos = self.real_pos.copy()
        if self.screenshake_intensity >= 1:
            self.pos[0] += random.random()*self.screenshake_intensity-(self.screenshake_intensity/2)
            self.pos[1] += random.random()*self.screenshake_intensity-(self.screenshake_intensity/2)
            self.screenshake_intensity -= 1




class Blackout:
    def __init__(self):
        self.surface = pygame.Surface((600, 600))
        self.alpha = 0

    def fade_out(self, frame, total_frames):
        self.alpha = 255 - int(frame / total_frames * 255)
    
    def fade_in(self, frame, total_frames):
        self.alpha = int(frame / total_frames * 255)
    
    def draw(self, screen):
        self.surface.fill((0, 0, 0))
        self.surface.set_alpha(self.alpha)
        screen.blit(self.surface, (0,0))