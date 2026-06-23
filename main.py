import pygame
import sys
import subprocess
import ctypes
import platform
import json
import webbrowser

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
    # files step 1 — add "files": [] to each project here, same as "tags": []
    {"name": "project1", "status": "done",     "tags": [], "progress": 0.50, "notes": "", "links": ["https://github.com"], "files": []},
    {"name": "project2", "status": "on hold",  "tags": [], "progress": 0.45, "notes": "", "links": [], "files": []},
    {"name": "project3", "status": "deadline", "tags": [], "progress": 0.05, "notes": "", "links": [], "files": []},
]

all_tags = ["tag1", "tag2", "tag3"]
try:
    with open("data.json", "r") as f:
        data = json.load(f)
        projects = data["projects"]
        all_tags = data["tags"]
except:
    pass

for p in projects:
    if "links" not in p:
        p["links"] = []
    if "files" not in p:
        p["files"] = []


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
status_rect     = pygame.Rect(0, 0, 0, 0)
caret_visible = False
caret_timer   = 0
cursor_pos = 0
dropdown_open     = False
tag_drop_rects    = []
tag_sidebar_rects = []
context_menu_open = False
context_menu_x = 0
context_menu_y = 0
context_menu_i = -1
context_menu_delete_rect = pygame.Rect(0, 0, 0, 0)
context_menu_rename_rect = pygame.Rect(0, 0, 0, 0)
context_menu_delete_hover = False
context_menu_rename_hover = False
context_menu_delete_clicked = False
context_menu_rename_clicked = False
tag_menu_open = False
tag_menu_x = 0
tag_menu_y = 0
tag_menu_i = -1
tag_menu_delete_rect = pygame.Rect(0, 0, 0, 0)
tag_menu_rename_rect = pygame.Rect(0, 0, 0, 0)
tag_menu_delete_hover = False
tag_menu_rename_hover = False
tag_menu_delete_clicked = False
tag_menu_rename_clicked = False
context_menu_log_rect    = pygame.Rect(0, 0, 0, 0)
context_menu_log_hover   = False
context_menu_log_clicked = False
context_menu_status_rect    = pygame.Rect(0, 0, 0, 0)
context_menu_status_hover   = False
context_menu_status_clicked = False
status_submenu_open    = False
status_submenu_x       = 0
status_submenu_y       = 0
status_submenu_hover_i = -1
status_submenu_rects   = []
tag_menu_log_rect    = pygame.Rect(0, 0, 0, 0)
tag_menu_log_hover   = False
tag_menu_log_clicked = False
progress_log_rect = pygame.Rect(0, 0, 0, 0)
link_rects        = []
link_hover_i      = -1
link_clicked_i    = -1


def draw_raised_bevel(surface, x, y, w, h):
    pygame.draw.line(surface, (255, 255, 255), (x,     y),     (x+w-1, y),     1)
    pygame.draw.line(surface, (255, 255, 255), (x,     y),     (x,     y+h-1), 1)
    pygame.draw.line(surface, (128, 128, 128), (x,     y+h-1), (x+w-1, y+h-1), 1)
    pygame.draw.line(surface, (128, 128, 128), (x+w-1, y),     (x+w-1, y+h-1), 1)

def draw_sunken_bevel(surface, x, y, w, h):
    pygame.draw.line(surface, (128, 128, 128), (x,     y),     (x+w-1, y),     1)
    pygame.draw.line(surface, (128, 128, 128), (x,     y),     (x,     y+h-1), 1)
    pygame.draw.line(surface, (255, 255, 255), (x,     y+h-1), (x+w-1, y+h-1), 1)
    pygame.draw.line(surface, (255, 255, 255), (x+w-1, y),     (x+w-1, y+h-1), 1)

def draw_double_sunken_bevel(surface, x, y, w, h):
    pygame.draw.line(surface, (128, 128, 128), (x,     y),     (x+w-1, y),     1)
    pygame.draw.line(surface, (0,   0,   0),   (x+1,   y+1),   (x+w-2, y+1),   1)
    pygame.draw.line(surface, (128, 128, 128), (x,     y),     (x,     y+h-1), 1)
    pygame.draw.line(surface, (0,   0,   0),   (x+1,   y+1),   (x+1,   y+h-2), 1)
    pygame.draw.line(surface, (255, 255, 255), (x,     y+h-1), (x+w-1, y+h-1), 1)
    pygame.draw.line(surface, (212, 208, 200), (x+1,   y+h-2), (x+w-2, y+h-2), 1)
    pygame.draw.line(surface, (255, 255, 255), (x+w-1, y),     (x+w-1, y+h-1), 1)
    pygame.draw.line(surface, (212, 208, 200), (x+w-2, y+1),   (x+w-2, y+h-2), 1)

def draw_button_bevel(surface, x, y, w, h):
    pygame.draw.line(surface, (255, 255, 255), (x,     y),     (x+w-1, y),     1)
    pygame.draw.line(surface, (255, 255, 255), (x,     y),     (x,     y+h-1), 1)
    pygame.draw.line(surface, (0,   0,   0),   (x+w-1, y),     (x+w-1, y+h-1), 1)
    pygame.draw.line(surface, (0,   0,   0),   (x,     y+h-1), (x+w-1, y+h-1), 1)
    pygame.draw.line(surface, (128, 128, 128), (x+w-2, y+1),   (x+w-2, y+h-2), 1)
    pygame.draw.line(surface, (128, 128, 128), (x+1,   y+h-2), (x+w-2, y+h-2), 1)

def draw_dropdown_bevel(surface, x, y, w, h):
    pygame.draw.line(surface, (235, 233, 225), (x,     y),     (x+w-1, y),     1)
    pygame.draw.line(surface, (212, 208, 200), (x+1,   y+1),   (x+w-2, y+1),   1)
    pygame.draw.line(surface, (235, 233, 225), (x,     y),     (x,     y+h-1), 1)
    pygame.draw.line(surface, (212, 208, 200), (x+1,   y+1),   (x+1,   y+h-2), 1)
    pygame.draw.line(surface, (128, 128, 128), (x,     y+h-1), (x+w-1, y+h-1), 1)
    pygame.draw.line(surface, (180, 180, 180), (x+1,   y+h-2), (x+w-2, y+h-2), 1)
    pygame.draw.line(surface, (64,  64,  64),  (x+w-1, y),     (x+w-1, y+h-1), 1)
    pygame.draw.line(surface, (128, 128, 128), (x+w-2, y+1),   (x+w-2, y+h-2), 1)

def draw_progress_bevel(surface, x, y, w, h):
    pygame.draw.line(surface, (255, 255, 255), (x,     y),     (x+w-1, y),     1)
    pygame.draw.line(surface, (255, 255, 255), (x,     y),     (x,     y+h-1), 1)
    pygame.draw.line(surface, (0,   100,  0),  (x,     y+h-1), (x+w-1, y+h-1), 1)
    pygame.draw.line(surface, (0,   100,  0),  (x+w-1, y),     (x+w-1, y+h-1), 1)

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
                        text_buffer = text_buffer[:cursor_pos] + "\n" + text_buffer[cursor_pos:]
                        cursor_pos += 1
                        projects[selected]["notes"] = text_buffer
                    elif typing_mode == "tag":
                        all_tags[editing_tag_i] = text_buffer
                        for project in projects:
                            if saved_name in project["tags"]:
                                project["tags"].remove(saved_name)
                                project["tags"].append(text_buffer)
                        typing = False
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    elif typing_mode == "progress":
                        if text_buffer:
                            new_val = min(1.0, projects[selected]["progress"] + float(text_buffer) / 100)
                            projects[selected]["progress"] = new_val
                            if new_val == 1.0:
                                projects[selected]["status"] = "done"
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
                    if typing_mode == "progress":
                        if event.unicode.isdigit():
                            text_buffer = text_buffer[:cursor_pos] + event.unicode + text_buffer[cursor_pos:]
                            cursor_pos += 1
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

            if context_menu_open and event.button == 1:
                menu_rect = pygame.Rect(context_menu_x, context_menu_y, 80, 79)
                sub_rect  = pygame.Rect(status_submenu_x, status_submenu_y, 75, 76) if status_submenu_open else pygame.Rect(0, 0, 0, 0)
                if not menu_rect.collidepoint(event.pos) and not sub_rect.collidepoint(event.pos):
                    context_menu_open   = False
                    status_submenu_open = False

            if tag_menu_open and event.button == 1:
                tmenu_rect = pygame.Rect(tag_menu_x, tag_menu_y, 80, 55)
                if not tmenu_rect.collidepoint(event.pos):
                    tag_menu_open = False

            if dropdown_open and event.button == 1:
                if not combobox_rect.collidepoint(event.pos) and not any(r.collidepoint(event.pos) for r in tag_drop_rects):
                    dropdown_open = False

            if close_rect.collidepoint(event.pos) and event.button == 1:
                run = False

            if refresh_rect.collidepoint(event.pos) and event.button == 1:
                subprocess.Popen(["python3", sys.argv[0]])
                run = False

            if plus_projects_rect.collidepoint(event.pos) and event.button == 1:
                projects.append({"name": "", "status": "", "tags": [], "progress": 0.00, "notes": ""})
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
                    if event.button == 3:
                        context_menu_open = True
                        context_menu_x = event.pos[0]
                        context_menu_y = event.pos[1]
                        context_menu_i = i
            if context_menu_open:
                if context_menu_delete_rect.collidepoint(event.pos) and event.button == 1:
                    context_menu_delete_clicked = True
                if context_menu_rename_rect.collidepoint(event.pos) and event.button == 1:
                    context_menu_rename_clicked = True
                if context_menu_log_rect.collidepoint(event.pos) and event.button == 1:
                    context_menu_log_clicked = True
                if context_menu_status_rect.collidepoint(event.pos) and event.button == 1:
                    context_menu_status_clicked = True

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

            for li, lr in enumerate(link_rects):
                if lr.collidepoint(event.pos) and event.button == 1:
                    link_clicked_i = li

            if progress_log_rect.collidepoint(event.pos) and event.button == 1:
                typing = True
                typing_mode = "progress"
                text_buffer = ""
                cursor_pos = 0
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
                    if event.button == 3:
                        tag_menu_open = True
                        tag_menu_x = event.pos[0]
                        tag_menu_y = event.pos[1]
                        tag_menu_i = i
            if tag_menu_open:
                if tag_menu_delete_rect.collidepoint(event.pos) and event.button == 1:
                    tag_menu_delete_clicked = True
                if tag_menu_rename_rect.collidepoint(event.pos) and event.button == 1:
                    tag_menu_rename_clicked = True

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
            if context_menu_open:
                context_menu_delete_hover = context_menu_delete_rect.collidepoint(event.pos)
                context_menu_rename_hover = context_menu_rename_rect.collidepoint(event.pos)
                context_menu_log_hover    = context_menu_log_rect.collidepoint(event.pos)
                context_menu_status_hover = context_menu_status_rect.collidepoint(event.pos)
            if status_submenu_open:
                statuses_list = ["on hold", "in progress", "deadline", "done"]
                status_submenu_hover_i = -1
                for si, sr in enumerate(status_submenu_rects):
                    if sr.collidepoint(event.pos) and statuses_list[si] != "done":
                        status_submenu_hover_i = si
            link_hover_i = -1
            for li, lr in enumerate(link_rects):
                if lr.collidepoint(event.pos):
                    link_hover_i = li
            if tag_menu_open:
                tag_menu_delete_hover = tag_menu_delete_rect.collidepoint(event.pos)
                tag_menu_rename_hover = tag_menu_rename_rect.collidepoint(event.pos)

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
            if context_menu_open:
                if context_menu_delete_rect.collidepoint(event.pos) and event.button == 1:
                    projects.pop(context_menu_i)
                    selected = 0
                    context_menu_open = False
                context_menu_delete_clicked = False
                context_menu_delete_hover = False
                if context_menu_rename_rect.collidepoint(event.pos) and event.button == 1:
                    typing = True
                    typing_mode = "name"
                    saved_name = projects[context_menu_i]["name"]
                    text_buffer = projects[context_menu_i]["name"]
                    cursor_pos = len(text_buffer)
                    selected = context_menu_i
                    context_menu_open = False
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
                context_menu_rename_clicked = False
                
                if context_menu_log_rect.collidepoint(event.pos) and event.button == 1:
                    selected = context_menu_i
                    typing = True
                    typing_mode = "progress"
                    text_buffer = ""
                    cursor_pos = 0
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
                    context_menu_log_clicked = False
                if context_menu_status_rect.collidepoint(event.pos) and event.button == 1:
                    if projects[context_menu_i]["status"] != "done":
                        status_submenu_open = True
                        status_submenu_x = context_menu_x + 80
                        status_submenu_y = context_menu_y + 59
                    context_menu_status_clicked = False
                if status_submenu_open:
                    statuses_list = ["on hold", "in progress", "deadline", "done"]
                    for si, sr in enumerate(status_submenu_rects):
                        if sr.collidepoint(event.pos) and event.button == 1 and statuses_list[si] != "done":
                            projects[context_menu_i]["status"] = statuses_list[si]
                            status_submenu_open = False
                            context_menu_open   = False

            if tag_menu_open:
                if tag_menu_delete_rect.collidepoint(event.pos) and event.button == 1:
                    for project in projects:
                        if all_tags[tag_menu_i] in project["tags"]:
                            project["tags"].remove(all_tags[tag_menu_i])
                    all_tags.pop(tag_menu_i)
                    tag_menu_open = False
                tag_menu_delete_clicked = False
                tag_menu_delete_hover = False
                if tag_menu_rename_rect.collidepoint(event.pos) and event.button == 1:
                    typing = True
                    typing_mode = "tag"
                    editing_tag_i = tag_menu_i
                    saved_name = all_tags[tag_menu_i]
                    text_buffer = ""
                    cursor_pos = 0
                    tag_menu_open = False
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
                tag_menu_rename_clicked = False

            for li, lr in enumerate(link_rects):
                if lr.collidepoint(event.pos) and event.button == 1:
                    import threading
                    threading.Thread(target=webbrowser.open, args=(projects[selected]["links"][li],), daemon=True).start()
            link_clicked_i = -1
            # files step 4 — check if the user clicked one of the file squares and open it with subprocess.Popen
            # files step 5 — check if the user clicked the "+" button and call tkinter.filedialog.askopenfilename()
            # files step 6 — check if the user right-clicked a file square and open a small "open / remove" menu

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

    for p in projects:
        if p["progress"] >= 1.0:
            p["status"] = "done"
        elif p["status"] == "done":
            p["status"] = "in progress"

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
            draw_raised_bevel(window, 10, y, rw, rh)
        else:
            draw_sunken_bevel(window, 10, y, rw, rh)
        window.blit(font_small.render(project["name"], True, (0, 0, 0)), (13, y + 2))
        if project["status"] == "done":
            sq_color = (0, 180, 0)
        elif project["status"] == "on hold":
            sq_color = (220, 180, 0)
        elif project["status"] == "deadline":
            sq_color = (200, 0, 0)
        else:
            sq_color = (150, 150, 150)
        pygame.draw.rect(window, sq_color, (3, y + 4, 6, 6))
        y += rh + 4

    # projects + button (fixed position, top-right corner of sidebar)
    pbw = rh * 2
    px, py = SIDEBAR_X - pbw - 5, title_h + 5
    pygame.draw.rect(window, (212, 208, 200), (px, py, pbw, rh))
    draw_raised_bevel(window, px, py, pbw, rh)
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
            draw_raised_bevel(window, 10, y, rw, rh)
        else:
            draw_sunken_bevel(window, 10, y, rw, rh)
        label = text_buffer if editing_this else tag
        window.blit(font_small.render(label, True, (0, 0, 0)), (13, y + 2))
        y += rh + 4

    # tags + button (fixed position, top-right corner of tags section)
    pbw_t = rh * 2
    px, py = SIDEBAR_X - pbw_t - 5, win_h * 3 // 5 + 5
    pygame.draw.rect(window, (212, 208, 200), (px, py, pbw_t, rh))
    draw_raised_bevel(window, px, py, pbw_t, rh)
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
        draw_double_sunken_bevel(window, rx, ry, rw, rh)

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

    # files step 2 — loop through projects[selected]["files"] and draw each one as a small square inside the files box
    #                the box is at (155, title_h + 381 - offset) and is 430 wide and 120 tall
    #                draw each square starting from the left, spaced out in a row
    # files step 3 — draw a small "+" button to the right of the "files" label at the top of the section

    pygame.draw.rect(window, (255, 255, 255), (157, title_h + 540 - offset, 426, 116))
    draw_double_sunken_bevel(window, 155, title_h + 538 - offset, 430, 120)

    link_rects = []
    for li, link in enumerate(projects[selected]["links"]):
        lx = 157
        ly = title_h + 541 + li * 20 - offset
        pygame.draw.rect(window, (212, 208, 200), (lx, ly, 426, 18))
        link_rects.append(pygame.Rect(lx, ly, 426, 18))
        if li == link_clicked_i:
            draw_sunken_bevel(window, lx, ly, 426, 18)
        elif li == link_hover_i:
            draw_raised_bevel(window, lx, ly, 426, 18)
        else:
            draw_raised_bevel(window, lx, ly, 426, 18)
        window.blit(font_small.render(link, True, (0, 0, 0)), (lx + 4, ly + 2))

    # tags combobox — sunken text area + raised dropdown button
    cx, cy, cw, ch = 155, title_h + 60 - offset, 160, 20
    btn = 18
    pygame.draw.rect(window, (255, 255, 255), (cx + 2, cy + 2, cw - btn - 3, ch - 4))
    draw_double_sunken_bevel(window, cx, cy, cw, ch)

    bx = cx + cw - btn
    pygame.draw.rect(window, (212, 208, 200), (bx, cy+1, btn-1, ch-2))
    draw_button_bevel(window, bx, cy+1, btn-1, ch-2)

    ax, ay = bx + btn // 2, cy + ch // 2 + 1
    pygame.draw.polygon(window, (0, 0, 0), [(ax-3, ay-2), (ax+3, ay-2), (ax, ay+1)])

    tag_surf = font_small.render(", ".join(projects[selected]["tags"]), True, (0, 0, 0))
    window.blit(tag_surf, (cx + 3, cy + 1))
    combobox_rect = pygame.Rect(bx, cy, btn, ch)

    tag_drop_rects = []
    if dropdown_open:
        dx, dy = cx, cy + ch - 1
        dw     = cw - btn
        dh     = len(all_tags) * 18 + 20
        pygame.draw.rect(window, (212, 208, 200), (dx, dy, dw, dh))
        draw_dropdown_bevel(window, dx, dy, dw, dh)
        for i, tag in enumerate(all_tags):
            tags = font_small.render(tag, True, (0,0,0))
            window.blit(tags, (dx + 3, dy + 4 + i * 18))
            tag_drop_rects.append(pygame.Rect(dx + 3, dy + 4 + i * 18, dw, 18))

    # -------------------------------------------------------------------------
    # draw — progress bar (scrolls with content)
    # -------------------------------------------------------------------------
    bt  = title_h + 2 - offset
    bb  = title_h + 2 + bar_h - 1 - offset
    bf  = title_h + 4 - offset
    bfb = title_h + 4 + bar_h - 5 - offset

    # grey track — sunken bevel
    pygame.draw.rect(window, (212, 208, 200), (SIDEBAR_X+5, bt, panel_w-10, bar_h))
    draw_sunken_bevel(window, SIDEBAR_X+5, bt, panel_w-10, bar_h)

    # green fill — raised bevel
    pygame.draw.rect(window, (0, 165, 0), (SIDEBAR_X+7, bf, progress_W, bar_h-4))
    draw_progress_bevel(window, SIDEBAR_X+7, bf, progress_W, bar_h-4)

    if typing and typing_mode == "progress":
        box_x = SIDEBAR_X + panel_w - 47
        box_y = bt + bar_h + 2
        pygame.draw.rect(window, (255, 255, 255), (box_x, box_y, 42, 16))
        draw_sunken_bevel(window, box_x, box_y, 42, 16)
        progress_label = font_small.render(text_buffer + "|", True, (0, 0, 0))
        window.blit(progress_label, (box_x + 3, box_y + 1))
        progress_log_rect = pygame.Rect(box_x, box_y, 42, 16)
    else:
        progress_label = font_small.render(str(int(progress * 100)) + "%", True, (0, 0, 0))
        label_x = SIDEBAR_X + panel_w - 7 - progress_label.get_width()
        window.blit(progress_label, (label_x, bt + bar_h + 2))
        progress_log_rect = pygame.Rect(label_x, bt + bar_h + 2, progress_label.get_width(), progress_label.get_height())

    window.set_clip(None)

    # draw the context menu after set_clip(None) so it draws on top of everything:
    if context_menu_open:
        pygame.draw.rect(window, (255, 255, 255), (context_menu_x, context_menu_y, 80, 79))
        window.blit(font_small.render("delete", True, (0,0,0)), (context_menu_x + 7, context_menu_y + 3))
        window.blit(font_small.render("rename", True, (0,0,0)), (context_menu_x + 7, context_menu_y + 22))
        window.blit(font_small.render("log",    True, (0,0,0)), (context_menu_x + 7, context_menu_y + 41))
        window.blit(font_small.render(projects[context_menu_i]["status"], True, (0,0,0)), (context_menu_x + 7, context_menu_y + 60))
        context_menu_delete_rect = pygame.Rect(context_menu_x + 2, context_menu_y + 2,  76, 19)
        context_menu_rename_rect = pygame.Rect(context_menu_x + 2, context_menu_y + 21, 76, 19)
        context_menu_log_rect    = pygame.Rect(context_menu_x + 2, context_menu_y + 40, 76, 19)
        context_menu_status_rect    = pygame.Rect(context_menu_x + 2, context_menu_y + 59, 76, 19)
        draw_raised_bevel(window, context_menu_x, context_menu_y, 80, 79)

        if context_menu_delete_hover:
            draw_raised_bevel(window, context_menu_x + 2, context_menu_y + 2,  76, 19)

        if context_menu_delete_clicked:
            draw_sunken_bevel(window, context_menu_x + 2, context_menu_y + 2,  76, 19)

        if context_menu_rename_hover:
            draw_raised_bevel(window, context_menu_x + 2, context_menu_y + 21, 76, 19)

        if context_menu_rename_clicked:
            draw_sunken_bevel(window, context_menu_x + 2, context_menu_y + 21, 76, 19)

        if context_menu_log_hover:
            draw_raised_bevel(window, context_menu_x + 2, context_menu_y + 40, 76, 19)

        if context_menu_log_clicked:
            draw_sunken_bevel(window, context_menu_x + 2, context_menu_y + 40, 76, 19)

        if context_menu_status_hover and projects[context_menu_i]["status"] != "done":
            draw_raised_bevel(window, context_menu_x + 2, context_menu_y + 59, 76, 19)

        if context_menu_status_clicked:
            draw_sunken_bevel(window, context_menu_x + 2, context_menu_y + 59, 76, 19)

    if status_submenu_open:
        statuses_list = ["on hold", "in progress", "deadline", "done"]
        sub_w = 75
        sub_h = len(statuses_list) * 19
        pygame.draw.rect(window, (255, 255, 255), (status_submenu_x, status_submenu_y, sub_w, sub_h))
        draw_raised_bevel(window, status_submenu_x, status_submenu_y, sub_w, sub_h)
        status_submenu_rects = []
        for si, s in enumerate(statuses_list):
            ry = status_submenu_y + si * 19
            color = (180, 180, 180) if s == "done" else (0, 0, 0)
            window.blit(font_small.render(s, True, color), (status_submenu_x + 5, ry + 3))
            status_submenu_rects.append(pygame.Rect(status_submenu_x, ry, sub_w, 19))
            if si == status_submenu_hover_i:
                draw_raised_bevel(window, status_submenu_x + 2, ry + 1, sub_w - 4, 17)

    if tag_menu_open:
        pygame.draw.rect(window, (255, 255, 255), (tag_menu_x, tag_menu_y, 80, 55))
        window.blit(font_small.render("delete", True, (0, 0, 0)), (tag_menu_x + 7, tag_menu_y + 3))
        window.blit(font_small.render("rename", True, (0, 0, 0)), (tag_menu_x + 7, tag_menu_y + 19))
        tag_menu_delete_rect = pygame.Rect(tag_menu_x + 2, tag_menu_y + 2, 76, 19)
        tag_menu_rename_rect = pygame.Rect(tag_menu_x + 2, tag_menu_y + 19, 76, 19)
        draw_raised_bevel(window, tag_menu_x, tag_menu_y, 80, 55)

        if tag_menu_delete_hover:
            draw_raised_bevel(window, tag_menu_x + 2, tag_menu_y + 2, 76, 19)
        if tag_menu_delete_clicked:
            draw_sunken_bevel(window, tag_menu_x + 2, tag_menu_y + 2, 76, 19)
        if tag_menu_rename_hover:
            draw_raised_bevel(window, tag_menu_x + 2, tag_menu_y + 19, 76, 19)
        if tag_menu_rename_clicked:
            draw_sunken_bevel(window, tag_menu_x + 2, tag_menu_y + 19, 76, 19)

    pygame.display.update()

data = {"projects": projects, "tags": all_tags}
with open("data.json", "w") as f:
    json.dump(data, f)

pygame.quit()
sys.exit(0)
