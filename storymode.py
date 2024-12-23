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


def run_level(level, GAME, BLACKOUT, CHECKPOINT, DEATH, FINISH, hit, song):

    level_color = (192, 253, 255)

    pygame.mixer.music.load(song)

    pygame.mixer.music.play(-1)

    player = level.get_player_object()
    fadeout_frames = -1
    fadein_frames = 180

    for x in range(30):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        BLACKOUT.draw(windowSurface)

        pygame.display.update()
        mainClock.tick(60)

    while True:
        # FIRST
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.key == K_r and player != None:
                    player.reset_to_checkpoint()

                if event.key == K_e and player != None:
                    if level.is_writing:
                        for block in level.text_blocks:
                            if block.is_writing:
                                if block.drawing_text < len(block.message.message) * block.message.frames_per_letter:
                                    block.drawing_text = 9999
                                else:
                                    level.is_writing = False
                                    block.is_writing = False
                                break  
                    else:
                        for block in level.text_blocks:
                            if block.check_touching_player(player) and not block.is_writing:
                                block.is_writing = True
                                level.is_writing = True
                                break
                            

            elif event.type == CHECKPOINT:
                for block in level.block_object_list:
                    if isinstance(block, CheckpointBlock):
                        block.declaim()

            elif event.type == DEATH:
                level.death_particles(player)
                GAME.camera.screenshake_intensity = 18
                hit.play()

            elif event.type == FINISH:
                player = None
                fadeout_frames = 300
                pygame.mixer.music.fadeout(6000)

        
        if fadeout_frames > -1:
            fadeout_frames -= 1
            BLACKOUT.fade_out(fadeout_frames, 300)
            if fadeout_frames == 0:
                break
        elif fadein_frames > 0:
            fadein_frames -= 1
            BLACKOUT.fade_in(fadein_frames, 180)
    
        
        keys = pygame.key.get_pressed()

        if player != None and fadein_frames  < 90:
            if player.dead == 0:
                if not level.is_writing:
                    player.main_loop(keys, level, DEATH, FINISH, None)
            else:
                player.dead -= 1
                if player.dead == 0:
                    player.reset_to_checkpoint()


        for block in level.block_object_list:
            if isinstance(block, CheckpointBlock):
                if player != None:
                    block.check_touching_player(player, CHECKPOINT)
            elif isinstance(block, AirJumpBlock):
                if player != None:
                    block.check_touching_player(player)
                block.particles(GAME.camera.pos, level)
            elif isinstance(block, ExitBlock):
                block.change_color()
                block.particles(level, GAME.camera.pos)
            elif isinstance(block, DangerBlock):
                block.particles(level, GAME.camera.pos)
            elif isinstance(block, WindBlock):
                block.particles(level, GAME.camera.pos)



        level_width = level.level_dict["width"] * 20
        level_height = level.level_dict["height"] * 20
        if player != None:
            GAME.move_camera_to_player(player.x+20, player.y+20, [level_width, level_height])
        GAME.camera.screenshake()

        if player != None:
            player.pos_block(GAME.camera.pos)

        for block in level.block_object_list:
            block.pos_block(GAME.camera.pos)

        for block in level.text_blocks:
            block.pos_block(GAME.camera.pos)

        for particle in level.particles:
            particle.update()
            particle.pos_particle(GAME.camera.pos)
            if "wind" in particle.type:
                particle.kill_wind_particle(level)

        level.clear_dead_particles()



        # Draw rectangles
        windowSurface.fill(level_color)

        for block in level.block_object_list:
            block.render(windowSurface, GAME.camera.pos)
        for block in level.text_blocks:
            block.render(windowSurface, GAME.camera.pos)
            if player != None:
                if block.check_touching_player(player):
                    block.draw_prompt(GAME.camera.pos, windowSurface)

        if player != None:
            if player.dead == 0:
                player.render(windowSurface, GAME.camera.pos)

        for particle in level.particles:
            particle.render(windowSurface)

        for block in level.text_blocks:
            if block.is_writing:
                block.drawing_text += 1
                block.message.draw_text(block.drawing_text, windowSurface)
            else:
                block.drawing_text = 0

        BLACKOUT.draw(windowSurface)

        # LAST
        pygame.display.update()
        mainClock.tick(60)




def boss_level(level, GAME, BLACKOUT, CHECKPOINT, DEATH, FINISH, FOGGED, hit):

    done = False

    while not done:
        level.reset()
        level_color = (255, 140, 150)

        pygame.mixer.music.load("music/Annihilate (edited).mp3")

        pygame.mixer.music.play()

        player = level.get_player_object()
        fadeout_frames = -1
        fadein_frames = 30

        

        for x in range(30):
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

            BLACKOUT.draw(windowSurface)

            pygame.display.update()
            mainClock.tick(60)

        while True:
            # FIRST
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                    if event.key == K_r and player != None:
                        player.reset_to_checkpoint()

                    if event.key == K_e and player != None:
                        if level.is_writing:
                            for block in level.text_blocks:
                                if block.is_writing:
                                    if block.drawing_text < len(block.message.message) * block.message.frames_per_letter:
                                        block.drawing_text = 9999
                                    else:
                                        level.is_writing = False
                                        block.is_writing = False
                                    break  
                        else:
                            for block in level.text_blocks:
                                if block.check_touching_player(player) and not block.is_writing:
                                    block.is_writing = True
                                    level.is_writing = True
                                    break
                                

                elif event.type == CHECKPOINT:
                    for block in level.block_object_list:
                        if isinstance(block, CheckpointBlock):
                            block.declaim()

                elif event.type == DEATH:
                    level.death_particles(player)
                    GAME.camera.screenshake_intensity = 18
                    hit.play()

                elif event.type == FINISH:
                    player = None
                    fadeout_frames = 300
                    pygame.mixer.music.fadeout(6000)
                    done = True

                elif event.type == FOGGED:
                    player = None
                    fadeout_frames = 300
                    pygame.mixer.music.fadeout(6000)

            
            if fadeout_frames > -1:
                fadeout_frames -= 1
                BLACKOUT.fade_out(fadeout_frames, 300)
                if fadeout_frames == 0:
                    break
            elif fadein_frames > 0:
                fadein_frames -= 1
                BLACKOUT.fade_in(fadein_frames, 30)
        
            time_in_seconds = pygame.mixer.music.get_pos() / 1000

            if time_in_seconds > 180.5:
                level.spread_fog(100)
            elif time_in_seconds > 172.5:
                level.spread_fog(39)
            elif time_in_seconds > 170:
                level.spread_fog(28)
                done = True
            elif time_in_seconds > 7:
                level.spread_fog(9)
            else:
                level.spread_fog(28)

            if time_in_seconds > 185.5:
                player = None
                fadeout_frames = 300
            
            if not done:
                keys = pygame.key.get_pressed()

            if player != None:
                if player.dead == 0:
                    if not level.is_writing:
                        player.main_loop(keys, level, DEATH, FINISH, FOGGED)
                else:
                    player.dead -= 1
                    if player.dead == 0:
                        player.reset_to_checkpoint()


            for block in level.block_object_list:
                if isinstance(block, CheckpointBlock):
                    if player != None:
                        block.check_touching_player(player, CHECKPOINT)
                elif isinstance(block, AirJumpBlock):
                    if player != None:
                        block.check_touching_player(player)
                    block.particles(GAME.camera.pos, level)
                elif isinstance(block, ExitBlock):
                    block.change_color()
                    block.particles(level, GAME.camera.pos)
                elif isinstance(block, DangerBlock):
                    block.particles(level, GAME.camera.pos)
                elif isinstance(block, WindBlock):
                    block.particles(level, GAME.camera.pos)

            
            
            for block in level.live_fog_blocks:
                block.particles(level, GAME.camera.pos)


            level_width = level.level_dict["width"] * 20
            level_height = level.level_dict["height"] * 20
            if player != None:
                GAME.move_camera_to_player(player.x+20, player.y+20, [level_width, level_height])
            GAME.camera.screenshake()

            if player != None:
                player.pos_block(GAME.camera.pos)

            for block in level.block_object_list:
                block.pos_block(GAME.camera.pos)
            for block in level.fog_blocks:
                block.pos_block(GAME.camera.pos)
            for block in level.live_fog_blocks:
                block.pos_block(GAME.camera.pos)

            for particle in level.particles:
                particle.update()
                particle.pos_particle(GAME.camera.pos)
                if "wind" in particle.type:
                    particle.kill_wind_particle(level)

            level.clear_dead_particles()



            # Draw rectangles
            windowSurface.fill(level_color)

            for block in level.block_object_list:
                block.render(windowSurface, GAME.camera.pos)

            if player != None:
                if player.dead == 0:
                    player.render(windowSurface, GAME.camera.pos)

            for particle in level.particles:
                particle.render(windowSurface)

            for block in level.fog_blocks:
                block.render(windowSurface, GAME.camera.pos)
            for block in level.fog_blocks:
                block.render(windowSurface, GAME.camera.pos)
        

            BLACKOUT.draw(windowSurface)

            # LAST
            pygame.display.update()
            mainClock.tick(60)

    


def main():

    LEVELMANAGER = LevelManager()
    GAME = Game()
    BLACKOUT = Blackout()

    levels = LEVELMANAGER.load_all()
    if levels == []:
        levels.append(LEVELMANAGER.create_empty_level(30,30))
    
    player = None

    CHECKPOINT = pygame.USEREVENT + 1
    DEATH = pygame.USEREVENT + 2
    FINISH = pygame.USEREVENT + 3
    FOGGED = pygame.USEREVENT + 4


    pygame.mixer.init()
    hit = pygame.mixer.Sound("sfx/hit.wav")


    WHITE = (255, 255, 255)
    SKY = (192, 253, 255)


    
    # LOAD IN
    pygame.mixer.music.load("music/Adventure - Disasterpiece.mp3")
    pygame.mixer.music.play(-1)

    pygame_logo = pygame.image.load("img/Pygame_logo.png")
    pygame_logo = pygame.transform.scale(pygame_logo, (500, 140))

    

    for x in range(80):                     # blank screen
        windowSurface.fill(SKY)
        pygame.display.update()
        mainClock.tick(60)
    
    for x in range(20):                     # fade in pygame logo
        windowSurface.fill(SKY)
        pygame_logo.set_alpha(x/20*255)
        windowSurface.blit(pygame_logo, (50, 230))
        pygame.display.update()
        mainClock.tick(60)
    
    for x in range(60):                     # show pygame logo 
        windowSurface.fill(SKY)
        windowSurface.blit(pygame_logo, (50, 230))
        pygame.display.update()
        mainClock.tick(60)
    
    for x in range(30, 0, -1):              # fade out pygame logo
        windowSurface.fill(SKY)
        pygame_logo.set_alpha(x/30*255)
        windowSurface.blit(pygame_logo, (50, 230))
        pygame.display.update()
        mainClock.tick(60)
    

    for x in range(70):                     # blank screen
        windowSurface.fill(SKY)
        pygame.display.update()
        mainClock.tick(60)

    # BUTTONS AND LOGO AND TITLE PARALAX

    img_back = pygame.image.load("img/Title_Image-3.png")
    img_back = pygame.transform.scale(img_back, (640, 640))
    img_back_rect = img_back.get_rect()

    img_midback = pygame.image.load("img/Title_Image-4.png")
    img_midback = pygame.transform.scale(img_midback, (640, 640))
    img_midback_rect = img_midback.get_rect()

    img_midfront = pygame.image.load("img/Title_Image-2.png")
    img_midfront = pygame.transform.scale(img_midfront, (640, 640))
    img_midfront_rect = img_midfront.get_rect()

    img_front = pygame.image.load("img/Title_Image-1.png")
    img_front = pygame.transform.scale(img_front, (640, 640))
    img_front_rect = img_front.get_rect()
    


    title_font = pygame.font.Font("fonts/Poxast-R9Jjl.ttf", 30)
    title_txt = title_font.render("Axion's Journey", False, (10, 10, 150))
    title_rect = title_txt.get_rect()
    title_rect.center = (300, 650)
    t_pos = [300, 700]

    
    button_img = pygame.image.load("img/button.png")
    btn_img_rect = button_img.get_rect()
    btn_img_rect.center = (300, 700)

    button_font = pygame.font.Font("fonts/PixelSplitter-Bold.ttf", 35)
    button_txt = button_font.render("BEGIN", False, (0, 0, 0))
    button_rect = button_txt.get_rect()
    button_rect.center = (300, 700)
    b_pos = [300, 850]
    
    hover = False
    clicked = False


    time = 0
    while not clicked:

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == MOUSEBUTTONDOWN:
                if hover:
                    clicked = True






        t_speed = (100 - t_pos[1])/20
        if t_speed < -2:
            t_speed = -2

        b_speed = (300 - b_pos[1])/20
        if b_speed < -2:
            b_speed = -2

        t_pos[1] += t_speed
        b_pos[1] += b_speed
        
        raw_mouse_pos = pygame.mouse.get_pos()
        mouse_pos = ((raw_mouse_pos[0]-300)/10, (raw_mouse_pos[1]-300)/10)

        title_rect.center = (t_pos[0] + mouse_pos[0]*1.5, t_pos[1] + mouse_pos[1]*1.4)
        btn_img_rect.center = (b_pos[0] + mouse_pos[0]*1.2, b_pos[1] + mouse_pos[1]*1.3)
        button_rect.center = (b_pos[0] + mouse_pos[0]*1.2, b_pos[1] + mouse_pos[1]*1.3)




        img_back_rect.center = (300 + mouse_pos[0]*0.6, 300 + mouse_pos[1]*0.6)
        img_midback_rect.center = (300 + mouse_pos[0]*0.68, 300 + mouse_pos[1]*0.68)
        img_midfront_rect.center = (300 + mouse_pos[0]*0.9, 300 + mouse_pos[1]*0.9)
        img_front_rect.center = (300 + mouse_pos[0]*1.2, 300 + mouse_pos[1]*1.2)


        alpha = time
        if alpha > 255:
            alpha = 255

        img_back.set_alpha(alpha)
        img_midback.set_alpha(alpha)
        img_midfront.set_alpha(alpha)
        img_front.set_alpha(alpha)


        if raw_mouse_pos[0] > btn_img_rect.left and raw_mouse_pos[0] < btn_img_rect.right and raw_mouse_pos[1] > btn_img_rect.top and raw_mouse_pos[1] < btn_img_rect.bottom:
            hover = True
        else:
            hover = False



        windowSurface.fill(SKY)

        windowSurface.blit(img_back, img_back_rect)
        windowSurface.blit(img_midback, img_midback_rect)
        windowSurface.blit(img_midfront, img_midfront_rect)
        windowSurface.blit(img_front, img_front_rect)


        windowSurface.blit(title_txt, title_rect)
        windowSurface.blit(button_img, btn_img_rect)
        windowSurface.blit(button_txt, button_rect)

        pygame.display.update()
        mainClock.tick(60)
        time += 1
        

    pygame.mixer.music.fadeout(5000)

    for x in range(300):

        BLACKOUT.fade_out(300-x, 300)

        windowSurface.fill(SKY)

        windowSurface.blit(img_back, img_back_rect)
        windowSurface.blit(img_midback, img_midback_rect)
        windowSurface.blit(img_midfront, img_midfront_rect)
        windowSurface.blit(img_front, img_front_rect)


        windowSurface.blit(title_txt, title_rect)
        windowSurface.blit(button_img, btn_img_rect)
        windowSurface.blit(button_txt, button_rect)
        BLACKOUT.draw(windowSurface)

        pygame.display.update()
        mainClock.tick(60)
    

    for x in range(60):
        BLACKOUT.draw(windowSurface)

        pygame.display.update()
        mainClock.tick(60)




    

    run_level(levels[0], GAME, BLACKOUT, CHECKPOINT, DEATH, FINISH, hit, "music/Luna Ascension EX - flashygoodness.mp3")

    # CUTSCENE HERE!!! (intro and panic)

    run_level(levels[1], GAME, BLACKOUT, CHECKPOINT, DEATH, FINISH, hit, "music/Cheat Codes - Nitro Fun.mp3")
    run_level(levels[2], GAME, BLACKOUT, CHECKPOINT, DEATH, FINISH, hit, "music/Commando Steve - Bossfight.mp3")
    run_level(levels[3], GAME, BLACKOUT, CHECKPOINT, DEATH, FINISH, hit, "music/Oceanic Breeze - flashygoodness.mp3")

    # CUTSCENE HERE!!! (oh no, hes gonna get me)
    
    boss_level(levels[4], GAME, BLACKOUT, CHECKPOINT, DEATH, FINISH, FOGGED, hit)

    # CUTSCENE HERE!!! (the longest one, quaternius is saved!!!)



    
    # CREDITS
    
    credit_dict = {
        "heading1": "Created by Tyler Watts",

        "heading3": "Music",
        "Adventure": "Disasterpiece",
        "Luna Ascension EX": "flashygoodness",
        "Sorrow": "flashygoodness",
        "Eldrich Crisis": "flashygoodness",
        "Cheat Codes": "Nitro Fun",
        "Commando Steve": "Bossfight",
        "Oceanic Breeze": "flashygoodness",
        "Pursuit": "Shirobon",
        "Annihilate": "Excision & Far Too Loud",
        "Formed by Glaciers": "Kubbi",
        "Once Again": "Matsirt",
        "The Moon": "Jake Kaufman",

        "heading4": "Inspiration",
        "Celeste": "Maddy Makes Games",
        "Just Shapes & Beats": "Berzerk Studio",
        "Rivals of Aether": "Aether Studios",

        "heading5": "Special Thanks",
        "Elissa Maffei": "Story & Art Review",
        "Brenna Stanley": "Story Review",
        "Rachel Petersen": "Story Review",
        "Lincolin Haggard": "Playtesting",
        "Dax Petersen": "Playtesting",
        "Taggart Cook": "Playtesting",

        "headingfinal": "THANK YOU FOR PLAYING!"

    }

    heading_font = pygame.font.Font("fonts/PixelSplitter-Bold.ttf", 30)
    small_font = pygame.font.Font("fonts/Pixellari.ttf", 20)

    title_txt = title_font.render("Axion's Journey", False, WHITE)
    title_rect = title_txt.get_rect()
    title_rect.midtop = (300, 630)

    credit_items = []
    credit_rects = []
    for idx, item in enumerate(credit_dict):

        if "heading" in item:
            new_item = heading_font.render(credit_dict[item], 0, WHITE)
            new_item_rect = new_item.get_rect()
            new_item_rect.center = (300, 740+idx*60)
            credit_items.append(new_item)
            credit_rects.append(new_item_rect)
        else:
            new_item1 = small_font.render(item, 0, WHITE)
            new_item_rect1 = new_item1.get_rect()
            new_item_rect1.midright = (260, 740+idx*60)
            new_item2 = small_font.render(credit_dict[item], 0, WHITE)
            new_item_rect2 = new_item2.get_rect()
            new_item_rect2.midleft = (340, 740+idx*60)


            credit_items.append(new_item1)
            credit_items.append(new_item2)
            credit_rects.append(new_item_rect1)
            credit_rects.append(new_item_rect2)


    pygame.mixer.music.load("music/The Moon - Jake Kaufman.mp3")
    pygame.mixer.music.play()

    counter = 0

    while credit_rects[-1].bottom > 0:

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()


        counter += 1
        if counter == 3:
            counter = 0
            title_rect.top -= 1
            for rect in credit_rects:
                rect.top -= 1

        

        
        windowSurface.fill((0, 0, 0))

        windowSurface.blit(title_txt, title_rect)

        for idx, item in enumerate(credit_items):
            windowSurface.blit(item, credit_rects[idx])

        pygame.display.update()
        mainClock.tick(60)
    


main()
