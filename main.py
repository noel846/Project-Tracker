import pygame, sys, subprocess
pygame.init()

# TODO: give the window a title — look up pygame.display.set_caption
#       it takes a string, like the name of your app

window = pygame.display.set_mode((600,600), pygame.RESIZABLE)
pygame.display.set_caption("project tracker")

# --- polka dot background ---
spacing = 30
dot_surface = None
last_size = (0, 0)

# step 1: make a blank canvas the same size as the window
#         dot_surface = pygame.Surface((600, 750))

# step 2: fill it white so the background isn't black
#         dot_surface.fill((255, 255, 255))

# step 3: pick a spacing — how far apart the dots are (try 30)
#         spacing = 30

# step 4: draw a grid of dots using two loops
#         the outer loop goes across (x), the inner loop goes down (y)
#         for x in range(0, 600, spacing):
#             for y in range(0, 750, spacing):
#                 pygame.draw.circle(dot_surface, (200, 200, 200), (x, y), 2)
#         the (200, 200, 200) is a light grey color — change it if you want
#         the 2 at the end is the dot radius in pixels

# step 5: now dot_surface is ready — remove the window.fill below and replace it with:
#         window.blit(dot_surface, (0, 0))

# --- your project data ---
projects = [
    {"name": "project1", "status": "done", "tags": ["tag1"]},
    {"name": "project2", "status": "on hold", "tags": ["tag2"]},
    {"name": "project3", "status": "deadline", "tags": ["tag3"]},
]
# FIXME: tags should be a list, like ["tag1", "tag2"] — you can have multiple tags per project

# --- fonts ---
font_small = pygame.font.SysFont("arial", 16)
font_big = pygame.font.SysFont("arial", 20)
# FIXME: give the fonts names so you can use them — font_small for regular text, font_heading for titles
SIDEBAR_X = 150
shadow_w = 8
run = True
while run:
    pygame.time.delay(100)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            pass  # FIXME: wire up key handling logic here

    win_w, win_h = window.get_size()

    if (win_w, win_h) != last_size:
        dot_surface = pygame.Surface((win_w, win_h))
        dot_surface.fill((255, 255, 255))
        for x in range(0, win_w, spacing):
            for y in range(0, win_h, spacing):
                pygame.draw.circle(dot_surface, (200, 200, 200), (x, y), 2)
        last_size = (win_w, win_h)

    window.blit(dot_surface, (0, 0))
    for i in range(shadow_w):
        alpha = 60 - i * 7
        strip = pygame.Surface((1, win_h), pygame.SRCALPHA)
        strip.fill((0, 0, 0, alpha))
        window.blit(strip, (SIDEBAR_X + i, 0))

    # TODO: draw a shadow along the right edge of the sidebar (at x=SIDEBAR_X)
    #       pygame can't blur, so fake it with a few semi-transparent vertical strips getting lighter
    #       create a surface for each strip, fill it with black + low alpha, blit it just right of the box:
    #           shadow_w = 8  # how wide the shadow is in pixels
    #           for i in range(shadow_w):
    #               alpha = 60 - i * 7  # starts darker, fades out — tweak these numbers
    #               strip = pygame.Surface((1, win_h), pygame.SRCALPHA)
    #               strip.fill((0, 0, 0, alpha))
    #               window.blit(strip, (SIDEBAR_X + i, 0))
    #       do this BEFORE drawing the white sidebar box so the shadow sits behind it

    sidebar_overlay = pygame.Surface((SIDEBAR_X, win_h), pygame.SRCALPHA)
    sidebar_overlay.fill((255, 255, 255, 180))
    window.blit(sidebar_overlay, (0, 0))

    # --- layout lines ---
    
    pygame.draw.line(window, (0, 0, 0), (SIDEBAR_X, 0), (SIDEBAR_X, win_h), 2)
    pygame.draw.line(window, (0, 0, 0), (0, win_h * 3 // 5), (SIDEBAR_X, win_h * 3 // 5), 2)

    # --- sidebar (the thin left strip, from x=0 to x=win_w//4) ---
    # TODO: this is where you put navigation — like a list of your status categories
    # TODO: to draw text, first do: text_surface = font.render("your text", True, (r, g, b))
    #       then blit it onto the window at a position: window.blit(text_surface, (x, y))
    # TODO: top half of the sidebar (y from 0 to win_h//2): list the status names
    # TODO: top half counts — show how many projects are in each status, like "2 done"

    # --- sidebar bottom half: tags ---
    # TODO: bottom half (y from win_h//2 to win_h): show all tags that exist across your projects
    #       loop through every project and its tags list, collect unique tags with a set()
    # TODO: draw each tag as a small pill — pygame.draw.rect with a corner radius, then blit the name on top
    # TODO: to add a new tag: press a key to enter "typing mode", capture KEYDOWN events to build a string,
    #       Enter saves it, Escape cancels — store custom tags in a separate list outside projects
    # TODO: to assign a tag to a project, click the tag in the sidebar then click a project card

    # --- main panel (the big right area, from x=win_w//4 to x=win_w) ---
    # TODO: this is where your project cards go — like the columns in the inspo screenshot
    # TODO: figure out how many status columns you have, then divide the panel width equally
    #       so if you have 3 statuses and the panel is 450px wide, each column is 150px
    # TODO: draw a heading at the top of each column (the status name)
    # TODO: then loop through your projects list — for each project, check its status
    #       and draw a card in the matching column
    # TODO: a card is just a rectangle — pygame.draw.rect draws one
    #       put the project name as text inside it
    # TODO: to stack cards vertically, keep a counter per column
    #       each new card in that column is drawn lower by one card height

    pygame.display.update()
pygame.quit()
sys.exit(0)