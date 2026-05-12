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
    {"name": "project1", "status": "done",     "tags": [], "progress": 0.50, "notes": ""},
    {"name": "project2", "status": "on hold",  "tags": [], "progress": 0.45, "notes": ""},
    {"name": "project3", "status": "deadline", "tags": [], "progress": 0.05, "notes": ""},
]

all_tags = ["tag1", "tag2", "tag3"]


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
selected     = 0

dragging       = False
drag_offset_x  = 0
drag_offset_y  = 0

drag_start_win_x = 0
drag_start_win_y = 0
drag_start_abs_x = 0
drag_start_abs_y = 0

plus_projects_rect = pygame.Rect(0, 0, 0, 0)
plus_tags_rect     = pygame.Rect(0, 0, 0, 0)
close_rect   = pygame.Rect(win_w - 30, 5, 20, 20)
refresh_rect = pygame.Rect(win_w - 55, 5, 20, 20)


resizing_right   = False
resizing_bottom  = False
resize_start_w   = 0
resize_start_h   = 0
resize_delta_x   = 0
resize_delta_y   = 0

typing         = False
text_buffer    = ""
saved_name     = ""
last_click_time = 0
last_click_i    = -1
last_tag_click_i    = -1
last_tag_click_time = 0
editing_tag_i       = -1
typing_mode = "name"
name_rect       = pygame.Rect(0, 0, 0, 0)
note_name_rect  = pygame.Rect(0, 0, 0, 0)
caret_visible = False
caret_timer   = 0
cursor_pos = 0
dropdown_open     = False
tag_drop_rects    = []
tag_sidebar_rects = []


pygame.key.set_repeat(400, 50)

# =============================================================================
# main loop
# =============================================================================
while run:
    pygame.time.delay(16)

    now = pygame.time.get_ticks()
    if typing and now - caret_timer >= 500:
        caret_visible = not caret_visible
        caret_timer   = now
    if not typing:
        caret_visible = False

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
            if typing:
                if event.key == pygame.K_ESCAPE:
                    if typing_mode == "name":
                        projects[selected]["name"] = saved_name
                    elif typing_mode == "tag":
                        all_tags[editing_tag_i] = saved_name
                    typing = False
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                elif event.key == pygame.K_BACKSPACE:
                    if cursor_pos > 0:
                        text_buffer = text_buffer[:cursor_pos - 1] + text_buffer[cursor_pos:]
                        cursor_pos -= 1
                    if typing_mode == "note":
                        projects[selected]["notes"] = text_buffer
                    elif typing_mode == "name":
                        projects[selected]["name"] = text_buffer
                elif event.key == pygame.K_RETURN:
                    if typing_mode == "name":
                        projects[selected]["name"] = text_buffer
                        typing = False
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    elif typing_mode == "note":
                        text_buffer += "\n"
                        projects[selected]["notes"] = text_buffer
                    elif typing_mode == "tag":
                        all_tags[editing_tag_i] = text_buffer
                        typing = False
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                elif event.key == pygame.K_LEFT:
                    cursor_pos = cursor_pos - 1
                    if cursor_pos < 0:
                        cursor_pos = 0
                elif event.key == pygame.K_RIGHT:
                    cursor_pos = cursor_pos + 1
                    if cursor_pos > len(text_buffer):
                        cursor_pos = len(text_buffer)
                else:
                    text_buffer = text_buffer[:cursor_pos] + event.unicode + text_buffer[cursor_pos:]
                    cursor_pos += 1
                    if typing_mode == "note":
                        projects[selected]["notes"] = text_buffer

        if event.type == pygame.MOUSEWHEEL:
            if pygame.mouse.get_pos()[0] > SIDEBAR_X:
                offset -= event.y * 20
                if offset < 0:
                    offset = 0
                if offset > 925 - win_h:
                    offset = 925 - win_h

        if event.type == pygame.MOUSEBUTTONDOWN:
            typing = False
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

            if close_rect.collidepoint(event.pos) and event.button == 1:
                run = False

            if refresh_rect.collidepoint(event.pos) and event.button == 1:
                subprocess.Popen(["python3", sys.argv[0]])
                run = False

            if plus_projects_rect.collidepoint(event.pos) and event.button == 1:
                projects.append({"name": "", "status": "", "tags": [], "progress": 0.00})
                selected = len(projects) - 1
                typing = True
                typing_mode = "name"
                saved_name = ""
                text_buffer = ""
                cursor_pos = 0
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
                
            for i, rect in enumerate(project_rect):
                if rect.collidepoint(event.pos):
                    now = pygame.time.get_ticks()
                    if i == last_click_i and now - last_click_time < 300:
                        typing = True
                        typing_mode = "name"
                        saved_name = projects[i]["name"]
                        text_buffer = ""
                        cursor_pos = 0
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
                    selected = i
                    last_click_time = now
                    last_click_i = i

            if name_rect.collidepoint(event.pos) and event.button == 1:
                typing_mode = "name"
                typing = True
                text_buffer = projects[selected]["name"]
                cursor_pos = len(text_buffer)
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
            if note_name_rect.collidepoint(event.pos) and event.button == 1:
                typing_mode = "note"
                typing = True
                text_buffer = projects[selected]["notes"]
                cursor_pos = len(text_buffer)
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)

            if plus_tags_rect.collidepoint(event.pos) and event.button == 1:
                all_tags.append("")
                editing_tag_i = len(all_tags) - 1
                typing = True
                typing_mode = "tag"
                saved_name = ""
                text_buffer = ""
                cursor_pos = 0
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)

            for i, rect in enumerate(tag_drop_rects):
                if rect.collidepoint(event.pos) and event.button == 1:
                    if all_tags[i] not in projects[selected]["tags"]:
                        projects[selected]["tags"].append(all_tags[i])
                    elif all_tags[i] in projects[selected]["tags"]:
                        projects[selected]["tags"].remove(all_tags[i])

            for i, rect in enumerate(tag_sidebar_rects):
                if rect.collidepoint(event.pos):
                    now = pygame.time.get_ticks()
                    if i == last_tag_click_i and now - last_tag_click_time < 300:
                        typing = True
                        typing_mode = "tag"
                        editing_tag_i = i
                        saved_name = all_tags[i]
                        text_buffer = ""
                        cursor_pos = 0
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
                    last_tag_click_time = now
                    last_tag_click_i = i
            # You need a list of rects for the sidebar tag boxes — make it the same way as project_rect.
            # Loop over that list with enumerate. On double-click (same pattern as project cards):
            #   - set typing = True and typing_mode = "tag"
            #   - save the current tag name in saved_name (so Escape can restore it)
            #   - save the index i in a new variable called editing_tag_i (so you know which tag to save later)
            #   - set text_buffer = "" so the old name is cleared and the user types fresh

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
            
            if combobox_rect.collidepoint(event.pos) and event.button == 1:
                dropdown_open = not dropdown_open

        if event.type == pygame.MOUSEMOTION:
            if not resizing_right and not resizing_bottom and not dragging:
                if right_edge.collidepoint(event.pos):
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEWE)
                elif bottom_edge.collidepoint(event.pos):
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZENS)
                elif typing:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
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
            if typing:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
            else:
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
    progress     = projects[selected]["progress"]
    progress_W   = (panel_w - 12) * progress

    # -------------------------------------------------------------------------
    # draw — background
    # -------------------------------------------------------------------------
    window.fill((236, 233, 216))

    # title bar gradient (XP: dark navy left → light blue right)
    bands = 30
    for i in range(bands):
        bx = win_w * i // bands
        bw = win_w * (i + 1) // bands - bx
        r  = int(10  + (146 - 10)  * i / bands)
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
    # draw — sidebar: projects
    # -------------------------------------------------------------------------
    project_rect = []
    y = 38
    for i, project in enumerate(projects):
        text_w, text_h = font_small.size(project["name"])
        rw, rh = text_w + 6, text_h + 4
        project_rect.append(pygame.Rect(10, y, rw, rh))
        pygame.draw.rect(window, (212, 208, 200), (10, y, rw, rh))
        if i == selected:
            pygame.draw.line(window, (255, 255, 255), (10,      y),      (10+rw-1, y),      1)
            pygame.draw.line(window, (255, 255, 255), (10,      y),      (10,      y+rh-1), 1)
            pygame.draw.line(window, (128, 128, 128), (10,      y+rh-1), (10+rw-1, y+rh-1), 1)
            pygame.draw.line(window, (128, 128, 128), (10+rw-1, y),      (10+rw-1, y+rh-1), 1)
        else:
            pygame.draw.line(window, (128, 128, 128), (10,      y),      (10+rw-1, y),      1)
            pygame.draw.line(window, (128, 128, 128), (10,      y),      (10,      y+rh-1), 1)
            pygame.draw.line(window, (255, 255, 255), (10,      y+rh-1), (10+rw-1, y+rh-1), 1)
            pygame.draw.line(window, (255, 255, 255), (10+rw-1, y),      (10+rw-1, y+rh-1), 1)
        window.blit(font_small.render(project["name"], True, (0, 0, 0)), (13, y + 2))
        y += rh + 4

    # projects + button (fixed position, top-right corner of sidebar)
    pbw = rh * 2
    px, py = SIDEBAR_X - pbw - 5, title_h + 5
    pygame.draw.rect(window, (212, 208, 200), (px, py, pbw, rh))
    pygame.draw.line(window, (255, 255, 255), (px,       py),      (px+pbw-1, py),      1)
    pygame.draw.line(window, (255, 255, 255), (px,       py),      (px,       py+rh-1), 1)
    pygame.draw.line(window, (128, 128, 128), (px,       py+rh-1), (px+pbw-1, py+rh-1), 1)
    pygame.draw.line(window, (128, 128, 128), (px+pbw-1, py),      (px+pbw-1, py+rh-1), 1)
    plus_projects_rect = pygame.Rect(px, py, pbw, rh)
    plus_text = font_small.render("+", True, (0, 0, 0))
    window.blit(plus_text, (
        plus_projects_rect.centerx - plus_text.get_width()  // 2,
        plus_projects_rect.centery - plus_text.get_height() // 2,
    ))

    # -------------------------------------------------------------------------
    # draw — sidebar: tags
    # -------------------------------------------------------------------------
    y = win_h * 3 // 5 + 10
    tag_sidebar_rects = []
    for i, tag in enumerate(all_tags):
        text_w, text_h = font_small.size(tag)
        rw, rh = text_w + 6, text_h + 4
        tag_sidebar_rects.append(pygame.Rect(10, y, rw, rh))
        pygame.draw.rect(window, (212, 208, 200), (10, y, rw, rh))
        editing_this = typing and typing_mode == "tag" and i == editing_tag_i
        if editing_this:
            pygame.draw.line(window, (255, 255, 255), (10,      y),      (10+rw-1, y),      1)
            pygame.draw.line(window, (255, 255, 255), (10,      y),      (10,      y+rh-1), 1)
            pygame.draw.line(window, (128, 128, 128), (10,      y+rh-1), (10+rw-1, y+rh-1), 1)
            pygame.draw.line(window, (128, 128, 128), (10+rw-1, y),      (10+rw-1, y+rh-1), 1)
        else:
            pygame.draw.line(window, (128, 128, 128), (10,      y),      (10+rw-1, y),      1)
            pygame.draw.line(window, (128, 128, 128), (10,      y),      (10,      y+rh-1), 1)
            pygame.draw.line(window, (255, 255, 255), (10,      y+rh-1), (10+rw-1, y+rh-1), 1)
            pygame.draw.line(window, (255, 255, 255), (10+rw-1, y),      (10+rw-1, y+rh-1), 1)
        label = text_buffer if editing_this else tag
        window.blit(font_small.render(label, True, (0, 0, 0)), (13, y + 2))
        y += rh + 4

    # TODO: rename tags — double-click a tag box in the sidebar to edit its name


    # same pattern as double-clicking a project card:
    # use enumerate on all_tags to get the index, make a rect for each tag box,
    # detect double-click with last_click_time, set typing = True with typing_mode = "tag",
    # store the index being edited so you know which entry in all_tags to update on Enter

    # tags + button (fixed position, top-right corner of tags section)
    pbw_t = rh * 2
    px, py = SIDEBAR_X - pbw_t - 5, win_h * 3 // 5 + 5
    pygame.draw.rect(window, (212, 208, 200), (px, py, pbw_t, rh))
    pygame.draw.line(window, (255, 255, 255), (px,         py),      (px+pbw_t-1, py),      1)
    pygame.draw.line(window, (255, 255, 255), (px,         py),      (px,         py+rh-1), 1)
    pygame.draw.line(window, (128, 128, 128), (px,         py+rh-1), (px+pbw_t-1, py+rh-1), 1)
    pygame.draw.line(window, (128, 128, 128), (px+pbw_t-1, py),      (px+pbw_t-1, py+rh-1), 1)
    plus_tags_rect = pygame.Rect(px, py, pbw_t, rh)
    plus_text_tag = font_small.render("+", True, (0, 0, 0))
    window.blit(plus_text_tag, (
        plus_tags_rect.centerx - plus_text_tag.get_width()  // 2,
        plus_tags_rect.centery - plus_text_tag.get_height() // 2,
    ))

    # -------------------------------------------------------------------------
    # draw — main panel (clipped so content doesn't overflow into the sidebar)
    # -------------------------------------------------------------------------
    window.set_clip(pygame.Rect(SIDEBAR_X + 2, title_h, win_w - SIDEBAR_X - 2, win_h - title_h))

    # section divider lines — fade from blue to white
    # layout rule: label → divider (+17px) → content (+5px) → next label (+20px)
    for line_y, fade_dist in [
        (title_h + 55  - offset, 120),   # tags
        (title_h + 114 - offset, 250),   # notes / todos
        (title_h + 376 - offset, 250),   # files
        (title_h + 538 - offset, 250),   # links
    ]:
        for xi in range(SIDEBAR_X + 5, SIDEBAR_X + 5 + fade_dist):
            fade = max(0, 1 - (xi - SIDEBAR_X - 5) / fade_dist)
            r    = int(255 - 200 * fade)
            g    = int(255 - 180 * fade)
            b    = 255
            pygame.draw.rect(window, (r, g, b), (xi, line_y - 1, 1, 3))

    # project name and section labels
    name_text = text_buffer if (typing and typing_mode == "name") else projects[selected]["name"]
    name_surf = font_big.render(name_text, True, (20, 20, 20))
    window.blit(name_surf, (155, title_h + 18 - offset))
    name_rect = pygame.Rect(155, title_h + 18 - offset, name_surf.get_width(), name_surf.get_height())
    if typing and typing_mode == "name" and caret_visible:
        caret_x = 155 + font_big.size(text_buffer[:cursor_pos])[0]
        caret_y = title_h + 18 - offset
        pygame.draw.line(window, (20, 20, 20), (caret_x, caret_y), (caret_x, caret_y + name_surf.get_height() - 1), 1)
    window.blit(font_small.render("tags",          True, (80, 80, 80)), (155, title_h + 36  - offset))
    window.blit(font_small.render("notes / todos", True, (80, 80, 80)), (155, title_h + 97  - offset))
    window.blit(font_small.render("files",         True, (80, 80, 80)), (155, title_h + 359 - offset))
    window.blit(font_small.render("links",         True, (80, 80, 80)), (155, title_h + 521 - offset))

    # notes/todos and files boxes — double sunken bevel
    for rx, ry, rw, rh in [
        (155, title_h + 119 - offset, 430, 220),
        (155, title_h + 381 - offset, 430, 120),
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

    note_name_rect = pygame.Rect(155, title_h + 119 - offset, 430, 220)
    notes_to_draw = text_buffer if (typing and typing_mode == "note") else projects[selected]["notes"]
    note_lines = notes_to_draw.split("\n")
    for note_i, note in enumerate(note_lines):
        window.blit(font_small.render(note, True, (0, 0, 0)), (160, title_h + 124 + note_i * 16 - offset))
    if typing and typing_mode == "note" and caret_visible:
        before_cursor = text_buffer[:cursor_pos].split("\n")
        caret_line    = len(before_cursor) - 1
        caret_x       = 160 + font_small.size(before_cursor[-1])[0]
        caret_y       = title_h + 124 + caret_line * 16 - offset
        pygame.draw.line(window, (0, 0, 0), (caret_x, caret_y), (caret_x, caret_y + 13), 1)

    # tags combobox — sunken text area + raised dropdown button
    cx, cy, cw, ch = 155, title_h + 60 - offset, 160, 20
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

    # draw the selected project's tags as a comma-separated string in the combobox text area
    tag_surf = font_small.render(", ".join(projects[selected]["tags"]), True, (0, 0, 0))
    window.blit(tag_surf, (cx + 3, cy + 1))
    combobox_rect = pygame.Rect(bx, cy, btn, ch)

    tag_drop_rects = []
    if dropdown_open:
        dx, dy = cx, cy + ch - 1.5
        dw     = cw - btn
        dh     = len(all_tags) * 18 + 20
        pygame.draw.rect(window, (212, 208, 200), (dx, dy, dw, dh))
        pygame.draw.line(window, (235, 233, 225), (dx,      dy),      (dx+dw-1, dy),      1)
        pygame.draw.line(window, (212, 208, 200), (dx+1,    dy+1),    (dx+dw-2, dy+1),    1)
        pygame.draw.line(window, (235, 233, 225), (dx,      dy),      (dx,      dy+dh-1), 1)
        pygame.draw.line(window, (212, 208, 200), (dx+1,    dy+1),    (dx+1,    dy+dh-2), 1)
        pygame.draw.line(window, (128, 128, 128), (dx,      dy+dh-1), (dx+dw-1, dy+dh-1), 1)
        pygame.draw.line(window, (180, 180, 180), (dx+1,    dy+dh-2), (dx+dw-2, dy+dh-2), 1)
        pygame.draw.line(window, (64,  64,  64),  (dx+dw-1, dy),      (dx+dw-1, dy+dh-1), 1)
        pygame.draw.line(window, (128, 128, 128), (dx+dw-2, dy+1),    (dx+dw-2, dy+dh-2), 1)
        for i, tag in enumerate(all_tags):
            tags = font_small.render(tag, True, (0,0,0))
            window.blit(tags, (dx + 3, dy + 4 + i * 18))
            tag_drop_rects.append(pygame.Rect(dx + 3, dy + 4 + i * 18, dw, 18))



        # TODO: clicking the arrow button should flip dropdown_open True/False
        # make a rect for the button using bx, cy, btn, ch and check it in MOUSEBUTTONDOWN

        # TODO: draw each tag as a row inside the dropdown
        # loop over all_tags with enumerate to get the index and tag name
        # draw each tag at dy + 4 + index * 18 (so they stack down the box)
        # clicking a row adds that tag to projects[selected]["tags"] if it isn't already there
        # use the "in" keyword to check: if tag not in projects[selected]["tags"]

    # -------------------------------------------------------------------------
    # draw — progress bar (scrolls with content)
    # -------------------------------------------------------------------------
    bt  = title_h + 2 - offset
    bb  = title_h + 2 + bar_h - 1 - offset
    bf  = title_h + 4 - offset
    bfb = title_h + 4 + bar_h - 5 - offset

    # grey track — sunken bevel
    pygame.draw.rect(window, (212, 208, 200), (SIDEBAR_X+5, bt, panel_w-10, bar_h))
    pygame.draw.line(window, (128, 128, 128), (SIDEBAR_X+5,         bt), (SIDEBAR_X+panel_w-5, bt), 1)
    pygame.draw.line(window, (128, 128, 128), (SIDEBAR_X+5,         bt), (SIDEBAR_X+5,         bb), 1)
    pygame.draw.line(window, (255, 255, 255), (SIDEBAR_X+5,         bb), (SIDEBAR_X+panel_w-5, bb), 1)
    pygame.draw.line(window, (255, 255, 255), (SIDEBAR_X+panel_w-5, bt), (SIDEBAR_X+panel_w-5, bb), 1)

    # green fill — raised bevel
    pygame.draw.rect(window, (0, 165, 0), (SIDEBAR_X+7, bf, progress_W, bar_h-4))
    pygame.draw.line(window, (255, 255, 255), (SIDEBAR_X+7,            bf),  (SIDEBAR_X+7+progress_W, bf),  1)
    pygame.draw.line(window, (255, 255, 255), (SIDEBAR_X+7,            bf),  (SIDEBAR_X+7,            bfb), 1)
    pygame.draw.line(window, (0,   100,  0),  (SIDEBAR_X+7,            bfb), (SIDEBAR_X+7+progress_W, bfb), 1)
    pygame.draw.line(window, (0,   100,  0),  (SIDEBAR_X+7+progress_W, bf),  (SIDEBAR_X+7+progress_W, bfb), 1)

    # TODO: show the percentage as a small label above the bar
    # hint: convert progress to a string like "50%" and draw it with window.blit

    window.set_clip(None)
    pygame.display.update()

pygame.quit()
sys.exit(0)
