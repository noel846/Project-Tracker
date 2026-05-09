import pygame, sys, subprocess, ctypes, ctypes.wintypes
pygame.init()

# TODO: give the window a title — look up pygame.display.set_caption

# TODO: switch pygame.RESIZABLE to pygame.NOFRAME | pygame.RESIZABLE to remove the OS title bar
# TODO: then handle dragging by tracking MOUSEBUTTONDOWN on the blue bar area and moving the window with pygame.display.set_mode or ctypes
# TODO: add a close button on the top right of the blue bar — draw a small X rect, check if clicked, then run = False
window = pygame.display.set_mode((600,600), pygame.NOFRAME)
pygame.display.set_caption("project tracker")

ui_img = pygame.image.load(r"C:\Users\noel\Pictures\ui.png")


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
dragging = False
drag_offset_x = 0
drag_offset_y = 0
# TODO: dragging — add these before the loop: dragging = False, drag_offset_x = 0, drag_offset_y = 0
# TODO: also import ctypes at the top
while run:
    pygame.time.delay(16)
    close_rect = pygame.Rect(win_w - 30, 5, 20, 20)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            pass  # FIXME: wire up key handling logic here
        if event.type == pygame.MOUSEWHEEL:
            offset += event.y * 20
        if event.type == pygame.MOUSEBUTTONDOWN:
            if close_rect.collidepoint(event.pos):
                run = False
            if event.pos[1] < 35:
                dragging = True
                drag_offset_x = event.pos[0]
                drag_offset_y = event.pos[1]
        if event.type == pygame.MOUSEMOTION:
            if dragging:
                hwnd = pygame.display.get_wm_info()["window"]
                pt = ctypes.wintypes.POINT()
                ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
                ctypes.windll.user32.SetWindowPos(hwnd, 0, pt.x - drag_offset_x, pt.y - drag_offset_y, 0, 0, 0x0001)
        if event.type == pygame.MOUSEBUTTONUP:
            dragging = False
        # TODO: close button — on MOUSEBUTTONDOWN, check if the click is inside the X button area (top right of the blue bar)
        #       define a rect like close_rect = pygame.Rect(win_w - 30, 5, 20, 20) and check if event.pos is inside it using close_rect.collidepoint(event.pos)
        #       if it is, set run = False
        # TODO: draw the close button each frame — pygame.draw.rect a small red box, then blit an "X" on top of it


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

    window.blit(pygame.transform.scale(ui_img, (win_w, win_h)), (0, 0))

    pygame.draw.rect(window, (200, 0, 0), close_rect)
    text_surface = font_small.render("X", True, (255, 255, 255))
    window.blit(text_surface, (win_w - 25, 6))

    # --- sidebar (the thin left strip, from x=0 to x=win_w//4) ---
    text_surface = font_small.render("folder1", True, (0,0,0))
    window.blit(text_surface, (10,65))
    text_surface = font_small.render("project1", True, (0,0,0))
    window.blit(text_surface, (20,75))
    text_surface = font_small.render("folder2", True, (0,0,0))
    window.blit(text_surface, (10,95))
    text_surface = font_small.render("project2", True, (0,0,0))
    window.blit(text_surface, (20,105))
    text_surface = font_small.render("folder3", True, (0,0,0))
    window.blit(text_surface, (10,125))
    text_surface = font_small.render("project3", True, (0,0,0))
    window.blit(text_surface, (20,135))
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
    
    text_surface = font_big.render("project1", True, (45,45,45))
    window.blit(text_surface, (160, 75 - offset))
    text_surface = font_big.render("tags", True, (45,45,45))
    window.blit(text_surface, (160, 100 - offset))
    text_surface = font_big.render("notes/todos", True, (45,45,45))
    window.blit(text_surface, (160, 155 - offset))
    text_surface = font_big.render("files", True, (45,45,45))
    window.blit(text_surface, (160, 435 - offset))
    text_surface = font_big.render("links", True, (45,45,45))
    window.blit(text_surface, (160, 585 - offset))
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