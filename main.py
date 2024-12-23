import pygame
from pygame.locals import *
import os, sys
from AxionsJourney import *
import random

mainClock = pygame.time.Clock()
pygame.init()

WINDOWWIDTH = 600
WINDOWHEIGHT = 600
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), flags=pygame.SCALED, depth=32, vsync=1)
pygame.display.set_caption("Axion's Journey")

def main():
    editing = True

    LEVELMANAGER = LevelManager()
    GAME = Game()

    levels = LEVELMANAGER.load_all()
    if levels == []:
        levels.append(LEVELMANAGER.create_empty_level(30,30))
    

    LEVELEDITOR = LevelEditor()
    blocksize = 20

    cursor_box = pygame.Rect(0, 0, 20, 20)
    
    player = None

    CHECKPOINT = pygame.USEREVENT + 1
    DEATH = pygame.USEREVENT + 2
    FINISH = pygame.USEREVENT + 3

    SKY = (192, 253, 255)


    pygame.mixer.init()

    hit = pygame.mixer.Sound("sfx/hit.wav")

    while True:
        # FIRST
        keys = pygame.key.get_pressed()

        if editing:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == K_g:
                        levels.append(LEVELMANAGER.add_level(len(levels)))
                        LEVELEDITOR.level_idx = len(levels)-1
                    elif event.key == K_r:
                        if keys[K_4] and keys[K_5]:
                            levels[LEVELEDITOR.level_idx] = LEVELMANAGER.add_level(LEVELEDITOR.level_idx)
                    elif event.key == K_h:
                        LEVELEDITOR.level_idx -= 1
                        if LEVELEDITOR.level_idx < 0:
                            LEVELEDITOR.level_idx = len(levels)-1
                    elif event.key == K_j:
                        LEVELEDITOR.level_idx += 1
                        if LEVELEDITOR.level_idx >= len(levels):
                            LEVELEDITOR.level_idx = 0
                        

                    # change brush
                    elif event.key == K_b:
                        LEVELEDITOR.change_brush("B")
                    elif event.key == K_e:
                        LEVELEDITOR.change_brush(" ")
                    elif event.key == K_p:
                        LEVELEDITOR.change_brush("P")
                    elif event.key == K_c:
                        LEVELEDITOR.change_brush("C")
                    elif event.key == K_v:
                        LEVELEDITOR.change_brush("J")
                    elif event.key == K_x:
                        LEVELEDITOR.change_brush("X")
                    elif event.key == K_z:
                        LEVELEDITOR.change_brush("Z")
                    elif event.key == K_f:
                        LEVELEDITOR.change_brush("F")
                    elif event.key == K_n:
                        LEVELEDITOR.change_brush("N")

                    elif event.key == K_o:
                        LEVELEDITOR.change_brush("O")
                    elif event.key == K_k:
                        LEVELEDITOR.change_brush("K")
                    elif event.key == K_l:
                        LEVELEDITOR.change_brush("L")
                    elif event.key == K_SEMICOLON:
                        LEVELEDITOR.change_brush(";")


                    elif event.key == K_q:
                        GAME.level_idx = LEVELEDITOR.level_idx
                        editing = False
            
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()

            if player == None:
                player = levels[LEVELEDITOR.level_idx].get_player_object()

            # Get keys pressed and mouse position
            
            raw_mouse_pos = pygame.mouse.get_pos()
            
            # Get camera movements

            level_width = levels[LEVELEDITOR.level_idx].level_dict["width"] * 20
            level_height = levels[LEVELEDITOR.level_idx].level_dict["height"] * 20
            if keys[LEVELEDITOR.camera.move_buttons["up"]]:
                LEVELEDITOR.camera.move_camera([0, -LEVELEDITOR.camera.speed], [level_width, level_height])
            if keys[LEVELEDITOR.camera.move_buttons["down"]]:
                LEVELEDITOR.camera.move_camera([0, LEVELEDITOR.camera.speed], [level_width, level_height])
            if keys[LEVELEDITOR.camera.move_buttons["left"]]:
                LEVELEDITOR.camera.move_camera([-LEVELEDITOR.camera.speed, 0], [level_width, level_height])
            if keys[LEVELEDITOR.camera.move_buttons["right"]]:
                LEVELEDITOR.camera.move_camera([LEVELEDITOR.camera.speed, 0], [level_width, level_height])
            LEVELEDITOR.camera.screenshake()

            mouse_pos = [raw_mouse_pos[0]+LEVELEDITOR.camera.pos[0], raw_mouse_pos[1]+LEVELEDITOR.camera.pos[1]]

            LEVELEDITOR.tile_num = mouse_pos[0] // blocksize + (mouse_pos[1] // blocksize) * levels[LEVELEDITOR.level_idx].level_dict["width"]

            cursor_box.left = LEVELEDITOR.tile_num % levels[LEVELEDITOR.level_idx].level_dict["width"] * blocksize
            cursor_box.top = LEVELEDITOR.tile_num // levels[LEVELEDITOR.level_idx].level_dict["width"] * blocksize
            cursor_box.left -= LEVELEDITOR.camera.pos[0]
            cursor_box.top -= LEVELEDITOR.camera.pos[1]

            if pygame.mouse.get_pressed()[0]:
                if levels[LEVELEDITOR.level_idx].level_dict["blocklist"][LEVELEDITOR.tile_num] != LEVELEDITOR.brush:
                    if LEVELEDITOR.brush != "N" and levels[LEVELEDITOR.level_idx].level_dict["blocklist"][LEVELEDITOR.tile_num] == "N":
                        LEVELEDITOR.add_block(levels[LEVELEDITOR.level_idx])
                        levels[LEVELEDITOR.level_idx].messages.pop(LEVELEDITOR.tile_num)
                    else:
                        LEVELEDITOR.add_block(levels[LEVELEDITOR.level_idx])
                        player = levels[LEVELEDITOR.level_idx].get_player_object()
                    
            try:
                player.pos_block(LEVELEDITOR.camera.pos)
            except:
                pass

            # Set positions of rectangles
            for block in levels[LEVELEDITOR.level_idx].block_object_list:
                block.pos_block(LEVELEDITOR.camera.pos)
            for block in levels[GAME.level_idx].fog_blocks:
                block.pos_block(LEVELEDITOR.camera.pos)
            for block in levels[GAME.level_idx].text_blocks:
                block.pos_block(LEVELEDITOR.camera.pos)

            # Draw rectangles
            windowSurface.fill(SKY)

            for block in levels[LEVELEDITOR.level_idx].block_object_list:
                block.render(windowSurface, LEVELEDITOR.camera.pos)
            for block in levels[LEVELEDITOR.level_idx].fog_blocks:
                block.render(windowSurface, LEVELEDITOR.camera.pos)
            for block in levels[LEVELEDITOR.level_idx].text_blocks:
                block.render(windowSurface, LEVELEDITOR.camera.pos) 

            try:
                player.render(windowSurface, LEVELEDITOR.camera.pos)
            except:
                pass

            # Cursor
            if LEVELEDITOR.brush == "B":
                cursor_color = (0,0,0)
            elif LEVELEDITOR.brush == " ":
                cursor_color = SKY
            elif LEVELEDITOR.brush == "P":
                cursor_color = (80,80,255)
            elif LEVELEDITOR.brush == "C":
                cursor_color = (0,100,0)
            elif LEVELEDITOR.brush == "J":
                cursor_color = (255,175,0)
            elif LEVELEDITOR.brush == "X":
                cursor_color = (255,20,71)
            elif LEVELEDITOR.brush == "Z":
                cursor_color = (255,200,100)
            elif LEVELEDITOR.brush == "F":
                cursor_color = (50,0,22)
            elif LEVELEDITOR.brush == "N":
                cursor_color = (200, 200, 150)
            
            elif LEVELEDITOR.brush == "O" or LEVELEDITOR.brush == "K" or LEVELEDITOR.brush == "L" or LEVELEDITOR.brush == ";":
                cursor_color = (250, 250, 250)

            pygame.draw.rect(windowSurface, cursor_color, cursor_box)


            # LAST
            pygame.display.update()
            mainClock.tick(60)




        else: # Not in editing mode?

            if GAME.level_idx == 4 and not pygame.mixer.music.get_busy():
                pygame.mixer.music.load("music/Annihilate (edited).mp3")
                pygame.mixer.music.play(1)


            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == K_q:
                        editing = True
                    if event.key == K_r:
                        player.reset_to_checkpoint()

                    if event.key == K_e:
                        if levels[GAME.level_idx].is_writing:
                            levels[GAME.level_idx].is_writing = False
                            for block in levels[GAME.level_idx].text_blocks:
                                block.is_writing = False
                        else:
                            for block in levels[GAME.level_idx].text_blocks:
                                if block.check_touching_player(player) and not block.is_writing:
                                    block.is_writing = True
                                    levels[GAME.level_idx].is_writing = True
                                    break
                                

                elif event.type == CHECKPOINT:
                    for block in levels[GAME.level_idx].block_object_list:
                        if isinstance(block, CheckpointBlock):
                            block.declaim()

                elif event.type == DEATH:
                    levels[GAME.level_idx].death_particles(player)
                    GAME.camera.screenshake_intensity = 18
                    hit.play()

                elif event.type == FINISH:
                    GAME.level_idx += 1
                    player = None
                    continue


            if player == None:
                player = levels[GAME.level_idx].get_player_object()
            
            keys = pygame.key.get_pressed()

            if player.dead == 0:
                if not levels[GAME.level_idx].is_writing:
                    player.main_loop(keys, levels[GAME.level_idx], DEATH, FINISH)
            else:
                player.dead -= 1
                if player.dead == 0:
                    player.reset_to_checkpoint()


            for block in levels[GAME.level_idx].block_object_list:
                if isinstance(block, CheckpointBlock):
                    block.check_touching_player(player, CHECKPOINT)
                elif isinstance(block, AirJumpBlock):
                    block.check_touching_player(player)
                    block.particles(GAME.camera.pos, levels[GAME.level_idx])
                elif isinstance(block, ExitBlock):
                    block.change_color()
                    block.particles(GAME.camera.pos, levels[GAME.level_idx])
                elif isinstance(block, WindBlock):
                    block.particles(levels[GAME.level_idx], GAME.camera.pos)

            levels[GAME.level_idx].spread_fog()


            level_width = levels[GAME.level_idx].level_dict["width"] * 20
            level_height = levels[GAME.level_idx].level_dict["height"] * 20
            GAME.move_camera_to_player(player.x+20, player.y+20, [level_width, level_height])
            GAME.camera.screenshake()

            player.pos_block(GAME.camera.pos)

            for block in levels[GAME.level_idx].block_object_list:
                block.pos_block(GAME.camera.pos)
            for block in levels[GAME.level_idx].fog_blocks:
                block.pos_block(GAME.camera.pos)
            for block in levels[GAME.level_idx].text_blocks:
                block.pos_block(GAME.camera.pos)

            for particle in levels[GAME.level_idx].particles:
                particle.update()
                particle.pos_particle(GAME.camera.pos)
                if "wind" in particle.type:
                    particle.kill_wind_particle(levels[GAME.level_idx])

            levels[GAME.level_idx].clear_dead_particles()
            # Draw rectangles
            windowSurface.fill(SKY)

            for block in levels[GAME.level_idx].block_object_list:
                block.render(windowSurface, GAME.camera.pos)
            for block in levels[GAME.level_idx].text_blocks:
                block.render(windowSurface, GAME.camera.pos)
                if block.check_touching_player(player):
                    block.draw_prompt(GAME.camera.pos, windowSurface)

            if player.dead == 0:
                player.render(windowSurface, GAME.camera.pos)

            for block in levels[GAME.level_idx].fog_blocks:
                block.render(windowSurface, GAME.camera.pos)

            for particle in levels[GAME.level_idx].particles:
                particle.render(windowSurface)

            for block in levels[GAME.level_idx].text_blocks:
                if block.is_writing:
                    block.drawing_text += 1
                    block.message.draw_text(block.drawing_text, windowSurface)
                else:
                    block.drawing_text = 0

            # LAST
            pygame.display.update()
            mainClock.tick(60)
        

main()
