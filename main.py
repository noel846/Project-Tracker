import pygame
import sys
import subprocess
import ctypes
import platform

pygame.init()

# --- platform setup ---
IS_WINDOWS = platform.system() == "Windows"
if IS_WINDOWS:
    import ctypes.wintypes
else:
    import ctypes.util
    from pygame._sdl2.video import Window as SDLWindow
    _libSDL2 = ctypes.CDLL(ctypes.util.find_library("SDL2"))

# --- window ---
window = pygame.display.set_mode((600, 600), pygame.NOFRAME)
pygame.display.set_caption("project tracker")

# --- your project data ---
projects = [
    {"name": "project1", "status": "done",     "tags": ["tag1"], "progress": 0.50},
    {"name": "project2", "status": "on hold",  "tags": ["tag2"], "progress": 0.45},
    {"name": "project3", "status": "deadline", "tags": ["tag3"], "progress": 0.01},
]

# --- fonts ---
font_small = pygame.font.SysFont("tahoma", 13)
font_big   = pygame.font.SysFont("tahoma", 16)

# --- layout constants ---
SIDEBAR_X = 150

# --- state ---
win_w, win_h   = window.get_size()
panel_w        = win_w - SIDEBAR_X
run            = True
offset         = 0

dragging       = False
drag_offset_x  = 0
drag_offset_y  = 0

drag_start_win_x = 0
drag_start_win_y = 0
drag_start_abs_x = 0
drag_start_abs_y = 0

resizing_right   = False
resizing_bottom  = False
resize_start_w   = 0
resize_start_h   = 0
resize_delta_x   = 0
resize_delta_y   = 0


# =============================================================================
# main loop
# =============================================================================
while run:
    pygame.time.delay(16)

    win_w, win_h = window.get_size()

    right_edge  = pygame.Rect(win_w - 5, 0, 5, win_h)
    bottom_edge = pygame.Rect(0, win_h - 5, win_w, 5)

    if IS_WINDOWS:
        hwnd = pygame.display.get_wm_info()["window"]

    # -------------------------------------------------------------------------
    # events
    # -------------------------------------------------------------------------
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            pass  # FIXME: wire up key handling logic here

        if event.type == pygame.MOUSEWHEEL:
            if pygame.mouse.get_pos()[0] > SIDEBAR_X:
                offset -= event.y * 20
                if offset < 0:
                    offset = 0
                if offset > 800 - win_h:
                    offset = 800 - win_h

        if event.type == pygame.MOUSEBUTTONDOWN:
            if close_rect.collidepoint(event.pos) and event.button == 1:
                run = False

            if refresh_rect.collidepoint(event.pos) and event.button == 1:
                subprocess.Popen(["python3", sys.argv[0]])
                run = False

            if right_edge.collidepoint(event.pos):
                resizing_right = True
                resize_start_w, resize_delta_x = win_w, 0
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEWE)

            if bottom_edge.collidepoint(event.pos):
                resizing_bottom = True
                resize_start_h, resize_delta_y = win_h, 0
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZENS)

            if event.pos[1] < 35:
                dragging      = True
                drag_offset_x = event.pos[0]
                drag_offset_y = event.pos[1]
                if not IS_WINDOWS:
                    mx, my = ctypes.c_int(), ctypes.c_int()
                    _libSDL2.SDL_GetGlobalMouseState(ctypes.byref(mx), ctypes.byref(my))
                    drag_start_abs_x, drag_start_abs_y = mx.value, my.value
                    sdl_win = SDLWindow.from_display_module()
                    drag_start_win_x, drag_start_win_y = sdl_win.position

        if event.type == pygame.MOUSEMOTION:
            if not resizing_right and not resizing_bottom and not dragging:
                if right_edge.collidepoint(event.pos):
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEWE)
                elif bottom_edge.collidepoint(event.pos):
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZENS)
                else:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

            if resizing_right:
                if IS_WINDOWS:
                    ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, event.pos[0], win_h, 0x0002)
                else:
                    resize_delta_x += event.rel[0]

            if resizing_bottom:
                if IS_WINDOWS:
                    ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, win_w, event.pos[1], 0x0002)
                else:
                    resize_delta_y += event.rel[1]

            if dragging:
                if IS_WINDOWS:
                    hwnd = pygame.display.get_wm_info()["window"]
                    pt   = ctypes.wintypes.POINT()
                    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
                    ctypes.windll.user32.SetWindowPos(hwnd, 0, pt.x - drag_offset_x, pt.y - drag_offset_y, 0, 0, 0x0001)
                else:
                    mx, my = ctypes.c_int(), ctypes.c_int()
                    _libSDL2.SDL_GetGlobalMouseState(ctypes.byref(mx), ctypes.byref(my))
                    sdl_win = SDLWindow.from_display_module()
                    sdl_win.position = (
                        drag_start_win_x + mx.value - drag_start_abs_x,
                        drag_start_win_y + my.value - drag_start_abs_y,
                    )

        if event.type == pygame.MOUSEBUTTONUP:
            if resizing_right or resizing_bottom:
                if IS_WINDOWS:
                    pt   = ctypes.wintypes.POINT()
                    rect = ctypes.wintypes.RECT()
                    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
                    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
                    new_w = (pt.x - rect.left) if resizing_right  else win_w
                    new_h = (pt.y - rect.top)  if resizing_bottom else win_h
                else:
                    new_w = (resize_start_w + resize_delta_x) if resizing_right  else win_w
                    new_h = (resize_start_h + resize_delta_y) if resizing_bottom else win_h
                window = pygame.display.set_mode((max(200, new_w), max(100, new_h)), pygame.NOFRAME)
                win_w, win_h = window.get_size()

            dragging        = False
            resizing_right  = False
            resizing_bottom = False
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    # -------------------------------------------------------------------------
    # layout recalculation (must happen after events in case window was resized)
    # -------------------------------------------------------------------------
    close_rect   = pygame.Rect(win_w - 30, 5, 20, 20)
    refresh_rect = pygame.Rect(win_w - 55, 5, 20, 20)
    panel_w      = win_w - SIDEBAR_X
    pw           = win_w - SIDEBAR_X
    title_h      = 30
    bar_h        = 10
    selected     = 0
    progress     = projects[selected]["progress"]
    progress_W   = (panel_w - 22) * progress

    # -------------------------------------------------------------------------
    # draw — background
    # -------------------------------------------------------------------------
    window.fill((236, 233, 216))

    # title bar gradient (XP: dark navy left → light blue right)
    bands = 30
    for i in range(bands):
        bx = win_w * i // bands
        bw = win_w * (i + 1) // bands - bx
        r  = int(10  + (166 - 10)  * i / bands)
        g  = int(36  + (202 - 36)  * i / bands)
        b  = int(106 + (240 - 106) * i / bands)
        pygame.draw.rect(window, (r, g, b), (bx, 0, bw, title_h))
    pygame.draw.line(window, (216, 228, 248), (0, 1), (win_w, 1), 1)

    # title text
    window.blit(font_small.render("project tracker", True, (255, 255, 255)), (8, 8))

    # sidebar and main panel backgrounds
    pygame.draw.rect(window, (212, 208, 200), (0,            title_h, SIDEBAR_X,                win_h - title_h))
    pygame.draw.rect(window, (255, 255, 255), (SIDEBAR_X + 2, title_h, win_w - SIDEBAR_X - 2, win_h - title_h))

    # -------------------------------------------------------------------------
    # draw — chrome (borders, dividers)
    # -------------------------------------------------------------------------

    # outer window border — raised bevel (white top+left, dark bottom+right)
    pygame.draw.line(window, (255, 255, 255), (0,          0),        (win_w,      0),        2)
    pygame.draw.line(window, (255, 255, 255), (0,          0),        (0,          win_h),    2)
    pygame.draw.line(window, (64,  64,  64),  (win_w - 1,  0),        (win_w - 1,  win_h),    2)
    pygame.draw.line(window, (64,  64,  64),  (0,          win_h - 1), (win_w,     win_h - 1), 2)

    # sidebar/panel vertical divider — beveled
    pygame.draw.line(window, (128, 128, 128), (SIDEBAR_X,     title_h), (SIDEBAR_X,     win_h), 1)
    pygame.draw.line(window, (255, 255, 255), (SIDEBAR_X + 1, title_h), (SIDEBAR_X + 1, win_h), 1)

    # sidebar horizontal divider — beveled
    divider_y = win_h * 3 // 5
    pygame.draw.line(window, (128, 128, 128), (0, divider_y),     (SIDEBAR_X, divider_y),     1)
    pygame.draw.line(window, (255, 255, 255), (0, divider_y + 1), (SIDEBAR_X, divider_y + 1), 1)

    # close button
    pygame.draw.rect(window, (200, 0, 0), close_rect)
    x_text = font_small.render("X", True, (255, 255, 255))
    window.blit(x_text, (
        close_rect.centerx - x_text.get_width()  // 2,
        close_rect.centery - x_text.get_height() // 2,
    ))

    # refresh button
    pygame.draw.rect(window, (0, 0, 200), refresh_rect)
    r_text = font_small.render("R", True, (255, 255, 255))
    window.blit(r_text, (
        refresh_rect.centerx - r_text.get_width()  // 2,
        refresh_rect.centery - r_text.get_height() // 2,
    ))

    # -------------------------------------------------------------------------
    # draw — sidebar
    # -------------------------------------------------------------------------
    y = 38
    for project in projects:
        text_w, text_h = font_small.size(project["name"])
        rw, rh = text_w + 6, text_h + 4
        pygame.draw.rect(window, (212, 208, 200), (10, y, rw, rh))
        pygame.draw.line(window, (128, 128, 128), (10,      y),      (10+rw-1, y),      1)
        pygame.draw.line(window, (128, 128, 128), (10,      y),      (10,      y+rh-1), 1)
        pygame.draw.line(window, (255, 255, 255), (10,      y+rh-1), (10+rw-1, y+rh-1), 1)
        pygame.draw.line(window, (255, 255, 255), (10+rw-1, y),      (10+rw-1, y+rh-1), 1)
        window.blit(font_small.render(project["name"], True, (0, 0, 0)), (13, y + 2))
        y += rh + 4

    # sidebar tags section
    tags = set()
    for project in projects:
        for tag in project["tags"]:
            tags.add(tag)

    y = win_h * 3 // 5 + 10
    for tag in tags:
        text_w, text_h = font_small.size(tag)
        rw, rh = text_w + 6, text_h + 4
        pygame.draw.rect(window, (212, 208, 200), (10, y, rw, rh))
        pygame.draw.line(window, (128, 128, 128), (10,      y),      (10+rw-1, y),      1)
        pygame.draw.line(window, (128, 128, 128), (10,      y),      (10,      y+rh-1), 1)
        pygame.draw.line(window, (255, 255, 255), (10,      y+rh-1), (10+rw-1, y+rh-1), 1)
        pygame.draw.line(window, (255, 255, 255), (10+rw-1, y),      (10+rw-1, y+rh-1), 1)
        window.blit(font_small.render(tag, True, (0, 0, 0)), (13, y + 2))
        y += rh + 4
    # TODO: add a "+" at the bottom of the tags list to create a new tag on click
    # hint: draw a "+" with window.blit, then check if it was clicked in the MOUSEBUTTONDOWN section

    # -------------------------------------------------------------------------
    # draw — main panel (clipped so content doesn't overflow into the sidebar)
    # -------------------------------------------------------------------------
    window.set_clip(pygame.Rect(SIDEBAR_X + 2, title_h, win_w - SIDEBAR_X - 2, win_h - title_h))

    # section divider lines — fade from blue to white
    for line_y, fade_dist in [
        (title_h + 55  - offset, 120),
        (title_h + 108 - offset, 250),
        (420            - offset, 250),
        (570            - offset, 250),
    ]:
        for xi in range(SIDEBAR_X + 5, SIDEBAR_X + 5 + fade_dist):
            fade = max(0, 1 - (xi - SIDEBAR_X - 5) / fade_dist)
            r    = int(255 - 200 * fade)
            g    = int(255 - 180 * fade)
            b    = 255
            pygame.draw.rect(window, (r, g, b), (xi, line_y - 1, 1, 3))

    # project name and section labels
    window.blit(font_big.render("project1",     True, (20, 20, 20)), (160, title_h + 15  - offset))
    window.blit(font_small.render("tags",        True, (80, 80, 80)), (160, title_h + 38  - offset))
    window.blit(font_small.render("notes / todos", True, (80, 80, 80)), (160, title_h + 83  - offset))
    window.blit(font_small.render("files",       True, (80, 80, 80)), (160, 398           - offset))
    window.blit(font_small.render("links",       True, (80, 80, 80)), (160, 550           - offset))

    # --- bevel recipe ---
    # a bevel makes a flat rectangle look 3D by drawing coloured lines along its edges
    # think of light hitting from the top-left — top and left sides are bright, bottom and right are in shadow
    #
    # sunken (like a text input — looks pushed into the screen):
    #   top and left edges = dark,  bottom and right edges = bright/white
    #
    # raised (like a button — looks popping out of the screen):
    #   top and left edges = bright/white,  bottom and right edges = dark
    #
    # to draw it: after your pygame.draw.rect, use pygame.draw.line along each of the 4 edges
    # the top edge goes from the top-left corner to the top-right corner
    # the left edge goes from the top-left corner to the bottom-left corner
    # the bottom edge goes from the bottom-left to the bottom-right
    # the right edge goes from the top-right to the bottom-right
    #
    # double bevel = draw two lines per edge, the second one 1px inside the first with a slightly different shade
    # the boxes below use: grey + black on top/left (shadow), white + xp-grey on bottom/right (highlight)

    # notes/todos and files boxes — double sunken bevel
    for rx, ry, rw, rh in [
        (155, title_h + 115 - offset, 430, 240),
        (155, 424           - offset, 430, 125),
    ]:
        pygame.draw.rect(window, (255, 255, 255), (rx + 2, ry + 2, rw - 4, rh - 4))
        pygame.draw.line(window, (128, 128, 128), (rx,      ry),      (rx+rw-1, ry),      1)
        pygame.draw.line(window, (0,   0,   0),   (rx+1,    ry+1),    (rx+rw-2, ry+1),    1)
        pygame.draw.line(window, (128, 128, 128), (rx,      ry),      (rx,      ry+rh-1), 1)
        pygame.draw.line(window, (0,   0,   0),   (rx+1,    ry+1),    (rx+1,    ry+rh-2), 1)
        pygame.draw.line(window, (255, 255, 255), (rx,      ry+rh-1), (rx+rw-1, ry+rh-1), 1)
        pygame.draw.line(window, (212, 208, 200), (rx+1,    ry+rh-2), (rx+rw-2, ry+rh-2), 1)
        pygame.draw.line(window, (255, 255, 255), (rx+rw-1, ry),      (rx+rw-1, ry+rh-1), 1)
        pygame.draw.line(window, (212, 208, 200), (rx+rw-2, ry+1),    (rx+rw-2, ry+rh-2), 1)

    # tags combobox — sunken text area + raised dropdown button
    cx, cy, cw, ch = 155, title_h + 57 - offset, 160, 17
    btn = 18
    pygame.draw.rect(window, (255, 255, 255), (cx + 2, cy + 2, cw - btn - 3, ch - 4))
    pygame.draw.line(window, (128, 128, 128), (cx,       cy),      (cx+cw-1,  cy),      1)
    pygame.draw.line(window, (0,   0,   0),   (cx+1,     cy+1),    (cx+cw-2,  cy+1),    1)
    pygame.draw.line(window, (128, 128, 128), (cx,       cy),      (cx,       cy+ch-1), 1)
    pygame.draw.line(window, (0,   0,   0),   (cx+1,     cy+1),    (cx+1,     cy+ch-2), 1)
    pygame.draw.line(window, (255, 255, 255), (cx,       cy+ch-1), (cx+cw-1,  cy+ch-1), 1)
    pygame.draw.line(window, (212, 208, 200), (cx+1,     cy+ch-2), (cx+cw-2,  cy+ch-2), 1)
    pygame.draw.line(window, (255, 255, 255), (cx+cw-1,  cy),      (cx+cw-1,  cy+ch-1), 1)
    pygame.draw.line(window, (212, 208, 200), (cx+cw-2,  cy+1),    (cx+cw-2,  cy+ch-2), 1)

    bx = cx + cw - btn
    pygame.draw.rect(window, (212, 208, 200), (bx, cy+1, btn-1, ch-2))
    pygame.draw.line(window, (255, 255, 255), (bx,       cy+1),    (bx+btn-2, cy+1),    1)
    pygame.draw.line(window, (255, 255, 255), (bx,       cy+1),    (bx,       cy+ch-2), 1)
    pygame.draw.line(window, (0,   0,   0),   (bx+btn-2, cy+1),    (bx+btn-2, cy+ch-2), 1)
    pygame.draw.line(window, (0,   0,   0),   (bx,       cy+ch-2), (bx+btn-2, cy+ch-2), 1)
    pygame.draw.line(window, (128, 128, 128), (bx+btn-3, cy+2),    (bx+btn-3, cy+ch-3), 1)
    pygame.draw.line(window, (128, 128, 128), (bx+1,     cy+ch-3), (bx+btn-3, cy+ch-3), 1)

    ax, ay = bx + btn // 2, cy + ch // 2 + 1
    pygame.draw.polygon(window, (0, 0, 0), [(ax-3, ay-2), (ax+3, ay-2), (ax, ay+1)])

    # -------------------------------------------------------------------------
    # draw — progress bar (scrolls with content)
    # -------------------------------------------------------------------------
    bt  = title_h + 2 - offset
    bb  = title_h + 2 + bar_h - 1 - offset
    bf  = title_h + 4 - offset
    bfb = title_h + 4 + bar_h - 5 - offset

    # grey track — sunken bevel
    pygame.draw.rect(window, (212, 208, 200), (SIDEBAR_X+10, bt, panel_w-20, bar_h))
    pygame.draw.line(window, (128, 128, 128), (SIDEBAR_X+10,         bt), (SIDEBAR_X+panel_w-10, bt), 1)
    pygame.draw.line(window, (128, 128, 128), (SIDEBAR_X+10,         bt), (SIDEBAR_X+10,         bb), 1)
    pygame.draw.line(window, (255, 255, 255), (SIDEBAR_X+10,         bb), (SIDEBAR_X+panel_w-10, bb), 1)
    pygame.draw.line(window, (255, 255, 255), (SIDEBAR_X+panel_w-10, bt), (SIDEBAR_X+panel_w-10, bb), 1)

    # green fill — raised bevel
    pygame.draw.rect(window, (0, 165, 0), (SIDEBAR_X+12, bf, progress_W, bar_h-4))
    pygame.draw.line(window, (255, 255, 255), (SIDEBAR_X+12,            bf),  (SIDEBAR_X+12+progress_W, bf),  1)
    pygame.draw.line(window, (255, 255, 255), (SIDEBAR_X+12,            bf),  (SIDEBAR_X+12,            bfb), 1)
    pygame.draw.line(window, (0,   100,  0),  (SIDEBAR_X+12,            bfb), (SIDEBAR_X+12+progress_W, bfb), 1)
    pygame.draw.line(window, (0,   100,  0),  (SIDEBAR_X+12+progress_W, bf),  (SIDEBAR_X+12+progress_W, bfb), 1)

    # TODO: show the percentage as a small label above the bar
    # hint: convert progress to a string like "50%" and draw it with window.blit

    pygame.display.update()

pygame.quit()
sys.exit(0)
