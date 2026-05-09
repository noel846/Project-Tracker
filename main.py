import pygame, sys, subprocess, ctypes, ctypes.wintypes
pygame.init()

window = pygame.display.set_mode((600,600), pygame.NOFRAME)
pygame.display.set_caption("project tracker")

# --- your project data ---
projects = [
    {"name": "project1", "status": "done", "tags": ["tag1"], "progress": 0.50},
    {"name": "project2", "status": "on hold", "tags": ["tag2"], "progress": 0.45},
    {"name": "project3", "status": "deadline", "tags": ["tag3"], "progress": 0.01},
]

# --- fonts ---
font_small = pygame.font.SysFont("arial", 16)
font_big = pygame.font.SysFont("arial", 20)
SIDEBAR_X = 150
win_w, win_h = window.get_size()
panel_w = win_w - SIDEBAR_X
run = True
offset = 0
dragging = False
drag_offset_x = 0
drag_offset_y = 0
resizing_right = False
resizing_bottom = False
while run:
    pygame.time.delay(16)
    close_rect = pygame.Rect(win_w - 30, 5, 20, 20)
    right_edge = pygame.Rect(win_w - 5, 0, 5, win_h)
    bottom_edge = pygame.Rect(0, win_h - 5, win_w, 5)

    hwnd = pygame.display.get_wm_info()["window"]
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            pass  # FIXME: wire up key handling logic here
        if event.type == pygame.MOUSEWHEEL:
            # TODO: only scroll if pygame.mouse.get_pos()[0] > SIDEBAR_X (mouse is inside the main panel)
            offset -= event.y * 20
            # TODO: clamp offset so it can't go below 0 (top) or above the max content height minus win_h
        if event.type == pygame.MOUSEBUTTONDOWN:
            if close_rect.collidepoint(event.pos):
                run = False
            if right_edge.collidepoint(event.pos):
                resizing_right = True
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEWE)
            if bottom_edge.collidepoint(event.pos):
                resizing_bottom = True
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZENS)
            if event.pos[1] < 35:
                dragging = True
                drag_offset_x = event.pos[0]
                drag_offset_y = event.pos[1]
        if event.type == pygame.MOUSEMOTION:
            if not resizing_right and not resizing_bottom and not dragging:
                if right_edge.collidepoint(event.pos):
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEWE)
                elif bottom_edge.collidepoint(event.pos):
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZENS)
                else:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            if resizing_right:
                ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, event.pos[0], win_h, 0x0002)
            if resizing_bottom:
                ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, win_w, event.pos[1], 0x0002)
            if dragging:
                hwnd = pygame.display.get_wm_info()["window"]
                pt = ctypes.wintypes.POINT()
                ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
                ctypes.windll.user32.SetWindowPos(hwnd, 0, pt.x - drag_offset_x, pt.y - drag_offset_y, 0, 0, 0x0001)
        if event.type == pygame.MOUSEBUTTONUP:
            if resizing_right or resizing_bottom:
                pt = ctypes.wintypes.POINT()
                ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
                rect = ctypes.wintypes.RECT()
                ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
                new_w = (pt.x - rect.left) if resizing_right else win_w
                new_h = (pt.y - rect.top) if resizing_bottom else win_h
                window = pygame.display.set_mode((max(200, new_w), max(100, new_h)), pygame.NOFRAME)
            dragging = False
            resizing_right = False
            resizing_bottom = False
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

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

    # --- draw UI ---
    window.fill((236, 233, 216))

    # title bar gradient (XP blue: dark navy left to light blue right)
    title_h = 30
    bands = 30
    for i in range(bands):
        bx = win_w * i // bands
        bw = win_w * (i + 1) // bands - bx
        r = int(10 + (166 - 10) * i / bands)
        g = int(36 + (202 - 36) * i / bands)
        b = int(106 + (240 - 106) * i / bands)
        pygame.draw.rect(window, (r, g, b), (bx, 0, bw, title_h))
    pygame.draw.line(window, (216, 228, 248), (0, 1), (win_w, 1), 1)

    # title text
    window.blit(font_small.render("project tracker", True, (255, 255, 255)), (8, 8))

    # sidebar background
    pygame.draw.rect(window, (212, 208, 200), (0, title_h, SIDEBAR_X, win_h - title_h))

    # main panel background
    pygame.draw.rect(window, (255, 255, 255), (SIDEBAR_X + 2, title_h, win_w - SIDEBAR_X - 2, win_h - title_h))

    # outer window border (beveled XP style)
    pygame.draw.line(window, (255, 255, 255), (0, 0), (win_w, 0), 2)
    pygame.draw.line(window, (255, 255, 255), (0, 0), (0, win_h), 2)
    pygame.draw.line(window, (64, 64, 64), (win_w - 1, 0), (win_w - 1, win_h), 2)
    pygame.draw.line(window, (64, 64, 64), (0, win_h - 1), (win_w, win_h - 1), 2)

    # sidebar/panel divider (beveled)
    pygame.draw.line(window, (128, 128, 128), (SIDEBAR_X, title_h), (SIDEBAR_X, win_h), 1)
    pygame.draw.line(window, (255, 255, 255), (SIDEBAR_X + 1, title_h), (SIDEBAR_X + 1, win_h), 1)

    # sidebar horizontal divider (beveled)
    divider_y = win_h * 3 // 5
    pygame.draw.line(window, (128, 128, 128), (0, divider_y), (SIDEBAR_X, divider_y), 1)
    pygame.draw.line(window, (255, 255, 255), (0, divider_y + 1), (SIDEBAR_X, divider_y + 1), 1)

    pygame.draw.rect(window, (200, 0, 0), close_rect)
    window.blit(font_small.render("X", True, (255, 255, 255)), (win_w - 25, 6))

    # --- sidebar ---
    window.blit(font_small.render("folder1", True, (0,0,0)), (10,65))
    window.blit(font_small.render("project1", True, (0,0,0)), (20,75))
    window.blit(font_small.render("folder2", True, (0,0,0)), (10,95))
    window.blit(font_small.render("project2", True, (0,0,0)), (20,105))
    window.blit(font_small.render("folder3", True, (0,0,0)), (10,125))
    window.blit(font_small.render("project3", True, (0,0,0)), (20,135))
    # TODO: top half — list each status name and how many projects have it

    # --- sidebar bottom half: tags ---
    tags = set()
    for project in projects:
        for tag in project["tags"]:
            tags.add(tag)

    y = win_h * 3 // 5 + 10
    for tag in tags:
        window.blit(font_small.render(tag, True, (0,0,0)), (10, y))
        y += 20
    # TODO: draw each tag as a small pill (rect with rounded corners)
    # TODO: pressing a key enters typing mode to create a new tag; Enter saves, Escape cancels
    # TODO: clicking a tag then a project card assigns the tag to that project

    # --- main panel (clipped so content stays inside the panel) ---
    window.set_clip(pygame.Rect(SIDEBAR_X + 2, title_h, win_w - SIDEBAR_X - 2, win_h - title_h))

    for line_y in [title_h + 55 - offset, title_h + 75 - offset, 420 - offset, 570 - offset]:
        for xi in range(SIDEBAR_X + 5, SIDEBAR_X + 160):
            fade = max(0, 1 - (xi - SIDEBAR_X - 5) / 140)
            pygame.draw.line(window, (0, 0, int(200 * fade)), (xi, line_y), (xi, line_y))

    window.blit(font_big.render("project1", True, (20, 20, 20)), (160, title_h + 10 - offset))
    window.blit(font_small.render("tags", True, (80, 80, 80)), (160, title_h + 32 - offset))
    window.blit(font_small.render("notes / todos", True, (80, 80, 80)), (160, title_h + 90 - offset))
    window.blit(font_small.render("files", True, (80, 80, 80)), (160, 398 - offset))
    window.blit(font_small.render("links", True, (80, 80, 80)), (160, 548 - offset))

    window.set_clip(None)
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
