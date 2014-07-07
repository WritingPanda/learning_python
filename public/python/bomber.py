# CodeSkulptor runs Python programs in your browser.
# Click the upper left button to run this simple demo.

# CodeSkulptor runs in Chrome 18+, Firefox 11+, and Safari 6+.
# Some features may work in other browsers, but do not expect
# full functionality.  It does NOT run in Internet Explorer.


try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

import random


# Constants used in bomber_crash explosion animation
EXPLOSION_CENTER = [50, 50]
EXPLOSION_SIZE = [100, 100]
EXPLOSION_SIZE_2 = [200, 200]
EXPLOSION_DIM = [9, 9]

BOMBER_DOWN = 25  # number of pixels the bomber downs each pass
CUNETA = 60       # separation among buildings
score = 0         # game score (1 point each bomb explosion + 25 bonus points each landing)
crash = False     # bomber crashed
launched = False  # True if a bomb has already been launched during actual pass (only one bomb each pass)
bomb = False      # True is bomb is flying
landed = False    # True is bomber has landed
flag = 0          # used to animate bomb
bomber_pos = [-300, 20]  # bomber initial position
bomb_pos = [0, 0]        # bomber position (its value is given when launched)
heights = []             # table with buildings' heights (there are 10 buildings numbered from #0 to #9)
                         # NOTE: heigths are measured from the top side of the frame (not from the floor)
                         #       so the higher the building, the lower height.

# assign randomly heights to each building (from 2 to 7 floors)
for idx in range(10):
    heights.append(random.randrange(300, 600, 50))
heights.append(800)  # dummy building #10 of zero height (used in bomber collision function)

# Explosions table:
#   Each item is a list of 3 elements:
# - tuple with explosion's center position.
# - number of animation's steps + 1
# - type of explosion (0 -> bomb; 1 -> bomber)
explosions = []


def timer_1_handler():
    """
    bomber and bomb movements independent from frame rate
    (controlled by this timer)
    """
    if not landed and not crash:
        bomber_move()
        bomber_collision(bomber_pos)
    if bomb:
        bomb_move()
        bomb_collision(bomb_pos)


# Handler for keyboard input (only keydown)
def key_down(key):
    global bomb_pos, bomb, launched, crash, score
    # Any key pressed launchs a bomb if conditions are met: bomber's center on screen and flying and no bomb flying.
    if bomber_pos[0] > 0 and bomber_pos[0] <= 800 and not bomb and not landed and not launched and not crash:
        launched = True  # bomb has been launched. Only one bomb each airplane's pass
        bomb_pos[0] = bomber_pos[0]
        bomb_pos[1] = bomber_pos[1]
        bomb = True   # flag to indicate bomb is flying
        launch_sound.play()
    elif landed:
        if key == simplegui.KEY_MAP['t']:
            new_level()   # begins a new level
    elif crash:
        if key == simplegui.KEY_MAP['t']:
            restart()     # resets game

def restart():
    """
    resets game (see above for comments on variables and tables)
    """
    global bomb, landed, flag, bomber_pos, bomb_pos, heights, launched, explosions, crash, score
    score = 0
    new_level()

def new_level():
    """
    new level: like restart(), but score is kept.
    """
    global bomb, landed, flag, bomber_pos, bomb_pos, heights, launched, explosions, crash, score
    crash = False
    launched = False
    bomb = False
    landed = False
    flag = 0
    bomber_pos = [-300, 20]
    bomb_pos = [0, 0]
    heights = []
    for idx in range(10):
        heights.append(random.randrange(300, 600, 50))
    heights.append(800)
    explosions = []

def bomber_move():
    """
    move bomber
    BE CAREFUL if you modify the number of pixels the bomber moves (n pixels) since the numbers "876" and "-152" below
    have to be multiples of that "n". If not, the bomber flying sound will not work correctly (even may not sound at all)
    """
    global bomber_pos, launched
    bomber_pos[0] += 4        # bomber moves "n = 4" pixels each time this function is called (by the timer)
    if bomber_pos[0] > 1000:
        bomber_pos[0] =  -300
        launched = False
        bomber_pos[1] += BOMBER_DOWN
    if bomber_pos[0] == 876:  # this number has to be a multiple of "n"
        bomber_sound.rewind()
    if bomber_pos[0] == -152: # Idem (multiple of n)
        bomber_sound.play()

def bomb_move():
    global bomb_pos, bomb
    bomb_pos[1] += 4
    if bomb_pos[1] > 770 and bomb:  # if bomb is completely under floor, it is discarded (bomb = False)
        bomb = False

def bomber_collision(pos):
    """
    collison between bomber and a building
    """
    global crash
    if pos[0] > 750 or crash: # bomber's center is out of screen's right side. (bombs are launched from bomber's center)
        return
    block_number = pos[0] // 80  # block number in which stands the center of the bomber (block = separation + building)
    rel_x = pos[0] - block_number * 80  # x-coor of bomber's center relative to the block origin (left side)
    if block_number < -1: # bomber is too far to the left to collide with first building.
        return
    if rel_x >= CUNETA:  # bomber front is inside y-vertical of the next block building (CUNETA = separation's width)
        if pos[1] + 30 > heights[block_number + 1]:  # collision
            crash = True  # bomber has crashed
            explosions.append([(pos[0], pos[1]), 81 + 1, 1])  # append a bomber explosion to the explosion's table
            crash_sound.rewind()
            crash_sound.play()
            return
    return

def bomb_collision(pos):
    """
    collision between bomb and a building: Rectangle containing bomb touchs building
    """
    global bomb, explosions
    if not bomb:  # there is no flying bomb
        return
    # Block width = building width: (80 - CUNETA) pixels + separation width: CUNETA pixels = 80 pixels/block
    block_number = pos[0] // 80  # block number in which the center of the bomb is located
    rel_x = pos[0] - block_number * 80 # x-coord of the bomb center relative to the block origin (left side)
    if rel_x < CUNETA:  # bomb x-center is located in the separation
        if rel_x + 8 >= CUNETA:  # bomb right side touchs the block's building (bomb width is 16 pixels)
            # check is bomb is at building's height
            if heights[block_number] >= 700: # building not exist (it has been previously destroyed)
                return
            elif heights[block_number] > pos[1] + 13:  # bomb height is 26 pixels.
                return  # bomb can not collide with building (it is above building)
            else: # collision with building in the block in which bomb is flying.
                bomb = False  # remove bomb
                explosions.append([(pos[0], pos[1] + 38), 24 + 1, 0]) # append bomb explosion to the explosion's table.
                explosion_sound.rewind()
                explosion_sound.play()
                building_resize(block_number) # affected building is re-sized to its new height after been bombarded.
                return
        elif rel_x - 8 <= 0:  # bomb left side touchs the previous block's building:
            if block_number == 0:  # the actual block is the first one (no more block at left side)
                return
            if heights[block_number - 1] >= 700: # building of previous block has already been completely destroyed.
                return
            # check is bomb is at building's height
            elif heights[block_number - 1] > pos[1] + 13:  # bomb height is 26 pixels
                return  # bomb can not collide with building (it is above building)
            # collision with building in the block to the left to the one in which bomb is flying.
            bomb = False  # remove bomb
            explosions.append([(pos[0], pos[1] + 38), 24 + 1, 0]) # append bomb explosion to the explosion's table.
            explosion_sound.rewind()
            explosion_sound.play()
            building_resize(block_number - 1) # affected building is re-sized to its new height after been bombarded.
            return
        return  # bomb center is in separation without touching any building
    # bomb center is inside the block's building width
    if heights[block_number] >= 700: # building already destroyed
        return
    # check is bomb is at building's height
    elif heights[block_number] > pos[1] + 13:  # bomb is 26 pixels height
        return  # bomb can not collide with building (it is above building)
    # collision with building in which the bomb center is flying
    bomb = False  # remove bomb
    explosions.append([(pos[0], pos[1] + 38), 24 + 1, 0]) # append bomb explosion to the explosion's table.
    explosion_sound.rewind()
    explosion_sound.play()
    building_resize(block_number) # affected building is re-sized to its new height after been bombarded.
    return

def building_resize(block):
    """
    building is re-sized randomly making it from 1 to 5 floors shorter.
    """
    global score
    if heights[block] >= 700:
        return
    heights[block] += 50 * random.choice([ 1, 2, 2, 2, 3, 3, 3, 4, 5]) # each floor is 50 pixels height
    score += 1  # one point for each bomb exploded on a building
    if heights[block] > 700: # building can not be shorter than 0 floors.
        heights[block] = 700
    no_buildings()  # check if all buildings has been destroyed (if so, accelerates landing)


def no_buildings():
    """
    when all buildings have been destroyed, the bomber descends to a height of 2 floors above ground,
    in order to not have to wait long before landing
    """
    global bomber_pos
    no_one = True
    for item in heights:
        if item < 700:
            no_one = False
            break
    if no_one and bomber_pos[1] < 620:
        bomber_pos[1] = 620

def check_landed(pos):
    """
    checks if bomber has arrived to the floor right side
    """
    global score
    if pos[1] == 670 and  pos[0] >= 734:
        if not landed:
            score += 25  # landing bonus
        return True
    return False


def draw_bomb(canvas):
    """
    Draws the bomb on canvas.
    bomb original size 128 * 128. Drawn rectangle size 32 * 32: bomb image = 16 * 26 (width * height)
    """
    global flag, bomb_pos, bomber_pos, bomb
    flag += 1
    if bomb:
        canvas.draw_image(bomb_image, (64 + 128 * ((flag // 4) % 5) , 64), (128, 128), (bomb_pos[0], bomb_pos[1]),
                          (32, 32))

def draw_bomber(canvas):
    """
    Draws the bomber on canvas
    bomber original size 300 * 232. Drawn rectangle size 150 * 116: bomber image = 140 * 60 (width * height)
    """
    if crash:
        return
    canvas.draw_image(bomber_image, (150, 116), (300, 232), (bomber_pos[0], bomber_pos[1]), (150, 116))
    canvas.draw_circle(bomber_pos, 4, 1, "red", "red")  # it indicates the bomb launching point.

def draw_floor(canvas):
    """
    floor occupies the bottom 100 pixels of canvas.
    """
    canvas.draw_polygon(((0, 700), (800, 700), (800, 800), (0, 800)), 1, "brown", "brown")

def draw_buildings(canvas):
    """
    Draws the 10 buildings in canvas as filled rectangles.
    """
    for idx in range(10):
        canvas.draw_polygon(((idx * 80 + CUNETA, heights[idx]), (idx * 80 + 80, heights[idx]),
                             (idx * 80 + 80, 700), (idx * 80 + CUNETA, 700)), 4, "red", "yellow")

def update_explosions(canvas):
    """
    draws animated explosions on canvas.
    """
    global explosions
    if len(explosions) == 0: # there is no explosion
        return
    for item in explosions:
        if item[1] > 0:  # there are animations steps pending (to be drawn)
            if item[2]:  # 1 -> bomber crash explosio. 0 -> bomb explosion
                image_name = explosion_image
                explosion_index = [item[1] % EXPLOSION_DIM[0], (item[1] // EXPLOSION_DIM[0]) % EXPLOSION_DIM[1]]
                canvas.draw_image(explosion_image,
                                [EXPLOSION_CENTER[0] + explosion_index[0] * EXPLOSION_SIZE[0],
                                 EXPLOSION_CENTER[1] + explosion_index[1] * EXPLOSION_SIZE[1]],
                                 EXPLOSION_SIZE, (item[0][0] + 50, item[0][1]), EXPLOSION_SIZE_2)
                # canvas.draw_image(image_name, (64 + (25 - item[1]) * 128, 64), (128, 128), item[0], (128, 128))
            else:
                image_name = explosion_alpha_image
                canvas.draw_image(image_name, (64 + (25 - item[1]) * 128, 64), (128, 128), item[0], (128, 128))
            item[1] -= 1
    # remove exhausted explosions:
    copy_explosions = []
    for item in explosions:
        if item[1] > 0: # there are no steps pending to be drawn (explosion exhausted)
            copy_explosions.append(item)
    explosions = list(copy_explosions)

# Handler to draw on canvas
def draw(canvas):
    """
    It is important to keep the order in which drawing functions are called
    """
    global landed, crash

    draw_bomb(canvas)
    draw_bomber(canvas)
    draw_buildings(canvas)
    draw_floor(canvas)
    canvas.draw_text("Score: " + str(score),(100, 750), 30, "black")

    update_explosions(canvas)

    if check_landed(bomber_pos):
        landed = True
        canvas.draw_text("L A N D E D !", (100, 30), 40, "green")
        canvas.draw_text("(press T key)", (400, 30), 30, "green")
        bomber_sound.rewind()

    if crash:
        bomb = False
        canvas.draw_text("C R A S H E D !", (100, 30), 40, "red")
        canvas.draw_text("(press T key)", (400, 30), 30, "red")
        bomber_sound.rewind()


# Create a frame and assign callbacks to event handlers
frame = simplegui.create_frame("Home", 800, 800)
frame.set_canvas_background("White")
frame.set_keydown_handler(key_down)
frame.set_draw_handler(draw)
timer_1 = simplegui.create_timer(15, timer_1_handler)
bomber_image = simplegui.load_image("https://dl.dropboxusercontent.com/u/54834334/B_24-J.png")
bomb_image = simplegui.load_image("https://dl.dropboxusercontent.com/u/54834334/bomb.png")
explosion_alpha_image = simplegui.load_image("https://dl.dropboxusercontent.com/u/54834334/explosion_alpha.png")
explosion_image = simplegui.load_image("https://dl.dropboxusercontent.com/u/54834334/explosion.png")
explosion_sound = simplegui.load_sound("https://dl.dropboxusercontent.com/u/54834334/bomb%203.ogg")
crash_sound = simplegui.load_sound("https://dl.dropboxusercontent.com/u/54834334/aircrash.ogg")
bomber_sound = simplegui.load_sound("https://dl.dropboxusercontent.com/u/54834334/fighter_plane_squadron.ogg")
launch_sound = simplegui.load_sound("https://dl.dropboxusercontent.com/u/54834334/bomb_launch_short.ogg")

# Start the frame animation
timer_1.start()
frame.start()

