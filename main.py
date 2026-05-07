import pygame, sys, subprocess
pygame.init()

# TODO: give the window a title — look up pygame.display.set_caption

window = pygame.display.set_mode((600,600), pygame.RESIZABLE)
pygame.display.set_caption("project tracker")

# --- polka dot background ---
spacing = 30
dot_surface = None
last_size = (0, 0)

# TODO: make a Surface the size of the window, fill it white, then draw a grid of dots with two nested loops
# TODO: use window.blit to draw it each frame instead of window.fill

# --- your project data ---
projects = [
    {"name": "project1", "status": "done", "tags": ["tag1"], "progress": 0.50},
    {"name": "project2", "status": "on hold", "tags": ["tag2"], "progress": 0.45},
    {"name": "project3", "status": "deadline", "tags": ["tag3"], "progress": 0.01},
]
# FIXME: tags should be a list, like ["tag1", "tag2"] — you can have multiple tags per project

# --- fonts ---
font_small = pygame.font.SysFont("arial", 16)
font_big = pygame.font.SysFont("arial", 20)
# FIXME: give the fonts names so you can use them — font_small for regular text, font_heading for titles
SIDEBAR_X = 150
win_w, win_h = window.get_size()
panel_w = win_w - SIDEBAR_X
run = True
offset = 0
while run:
    pygame.time.delay(100)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            pass  # FIXME: wire up key handling logic here
        if event.type == pygame.MOUSEWHEEL:
            offset += event.y * 20


    win_w, win_h = window.get_size()
    panel_w = win_w - SIDEBAR_X
    px = SIDEBAR_X
    pw = win_w - SIDEBAR_X
    pr = win_w
    bar_h = 10
    bar_y = 30
    selected = 0
    progress = projects[selected]["progress"]
    progress_W = pw * progress

    if (win_w, win_h) != last_size:
        dot_surface = pygame.Surface((win_w, win_h))
        dot_surface.fill((255, 255, 255))
        for x in range(0, win_w, spacing):
            for y in range(0, win_h, spacing):
                pygame.draw.circle(dot_surface, (200, 200, 200), (x, y), 2)
        last_size = (win_w, win_h)

    window.blit(dot_surface, (0, 0))

    pygame.draw.rect(window, (255, 255, 255), (0, 0, SIDEBAR_X, win_h))

    # --- layout lines ---

    pygame.draw.line(window, (0, 0, 0), (SIDEBAR_X, 0), (SIDEBAR_X, win_h), 2)
    pygame.draw.line(window, (0, 0, 0), (0, win_h * 3 // 5), (SIDEBAR_X, win_h * 3 // 5), 2)

    # --- sidebar (the thin left strip, from x=0 to x=win_w//4) ---
    text_surface = font_small.render("folder1", True, (0,0,0))
    window.blit(text_surface, (10,30))
    text_surface = font_small.render("project1", True, (0,0,0))
    window.blit(text_surface, (20,40))
    text_surface = font_small.render("folder2", True, (0,0,0))
    window.blit(text_surface, (10,60))
    text_surface = font_small.render("project2", True, (0,0,0))
    window.blit(text_surface, (20,70))
    text_surface = font_small.render("folder3", True, (0,0,0))
    window.blit(text_surface, (10,90))
    text_surface = font_small.render("project3", True, (0,0,0))
    window.blit(text_surface, (20,100))
    # TODO: top half — list each status name and how many projects have it

    # --- sidebar bottom half: tags ---
    tags = set()
    for project in projects:
        for tag in project["tags"]:
            tags.add(tag)

    y = win_h * 3 // 5 + 10
    for tag in tags:
        text_surface = font_small.render(tag, True, (0,0,0))
        window.blit(text_surface, (10, y))
        y += 20
    # TODO: draw each tag as a small pill (rect with rounded corners)
    # TODO: pressing a key enters typing mode to create a new tag; Enter saves, Escape cancels
    # TODO: clicking a tag then a project card assigns the tag to that project

    # --- main panel (the big right area, from x=SIDEBAR_X to x=win_w) ---
    
    pygame.draw.rect(window, (210,210,210), (px, bar_y - offset, pw, bar_h))
    pygame.draw.rect(window, (0,128,0), (px, bar_y - offset, progress_W, bar_h))
    text_surface = font_big.render("project1", True, (45,45,45))
    window.blit(text_surface, (160, 40 - offset))
    text_surface = font_big.render("tags", True, (45,45,45))
    window.blit(text_surface, (160, 65 - offset))
    text_surface = font_big.render("notes/todos", True, (45,45,45))
    window.blit(text_surface, (160, 120 - offset))
    pygame.draw.rect(window, (255,255,255), (160, 150 - offset, 395, 250 - offset))
    text_surface = font_big.render("files", True, (45,45,45))
    window.blit(text_surface, (160, 400 - offset))
    pygame.draw.rect(window, (0,0,0), (160, 450 - offset, 395, 450 - offset))
    text_surface = font_big.render("files", True, (45,45,45))
    window.blit(text_surface, (160, 550 - offset))
    # step 1: draw a progress bar near the top — use pygame.draw.rect twice: once grey for the track, once green for the fill
    # step 2: label it with window.blit in light grey above the bar, and draw a small white box on the top right
    # step 3: below the progress bar, draw the project name in big text on the left
    # step 4: on the same row, draw a "tags" label and a box to the right of the name for the project's tags
    # step 5: below that, write "notes/todos" as a label, then draw a large empty rectangle under it
    # step 6: below that, write "files" as a label, then draw another large empty rectangle under it
    # step 7: at the bottom, write "links" as a label, then draw a horizontal line stretching across the panel

    pygame.display.update()
pygame.quit()
sys.exit(0)