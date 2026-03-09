import pygame, sys, subprocess
pygame.init()

# hint: give the window a title — look up pygame.display.set_caption
#       it takes a string, like the name of your app

window = pygame.display.set_mode((600,750), pygame.RESIZABLE)

# --- polka dot background ---
# hint: you want to draw the dots ONCE before the loop starts, not every frame
#       (drawing every frame is wasteful — the dots never move)
# hint: pygame.Surface lets you create a blank canvas to draw on
#       think of it like a piece of paper separate from the window
# hint: fill that surface with white first, then draw dots on top of it
# hint: to make a grid of dots, use two nested for loops:
#       the outer loop moves across x (left to right), the inner loop moves down y (top to bottom)
#       increase x and y by the same fixed amount each step — that's your dot spacing
# hint: at each (x, y) grid point, draw a small filled circle — pygame.draw.circle is what you want
#       a radius of 2 or 3 pixels looks clean
# hint: save the finished surface in a variable so you can paste (blit) it onto the window each frame

# --- your project data ---
# hint: a list is a good way to store multiple projects
# hint: each project can be a dictionary — think of it like a row in a spreadsheet
#       each key is a column: name, status, tags
#       example status values: "todo", "in progress", "done"
#       tags can be another list inside the dict, like ["urgent", "client"]
# hint: write 3-4 fake projects by hand for now so you have something to display

# --- fonts ---
# hint: pygame can't render text without loading a font first
# hint: pygame.font.SysFont("arial", size) gives you a font using fonts already on your computer
# hint: make two — a smaller one for regular text (around 16) and a bigger one for headings (around 20)

run = True
while run:
    pygame.time.delay(100)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            command = "main.py"

    win_w, win_h = window.get_size()

    # hint: paste (blit) your polka dot surface onto the window here — this replaces window.fill
    #       window.blit(your_surface, (0, 0)) draws it starting from the top-left corner
    #       if you resize the window the dots won't cover the new area — don't worry about that yet

    window.fill((255, 255, 255))

    # --- layout lines ---
    pygame.draw.line(window, (0, 0, 0), (win_w // 4, 0), (win_w // 4, win_h), 2)
    pygame.draw.line(window, (0, 0, 0), (0, win_h // 2), (win_w // 4, win_h // 2), 2)

    # --- sidebar (the thin left strip, from x=0 to x=win_w//4) ---
    # hint: this is where you put navigation — like a list of your status categories
    # hint: to draw text, first do: text_surface = font.render("your text", True, (r, g, b))
    #       then blit it onto the window at a position: window.blit(text_surface, (x, y))
    # hint: top half of the sidebar (y from 0 to win_h//2): list the status names
    # hint: bottom half (y from win_h//2 to win_h): show counts, like "3 projects" or "1 done"

    # --- main panel (the big right area, from x=win_w//4 to x=win_w) ---
    # hint: this is where your project cards go — like the columns in the inspo screenshot
    # hint: figure out how many status columns you have, then divide the panel width equally
    #       so if you have 3 statuses and the panel is 450px wide, each column is 150px
    # hint: draw a heading at the top of each column (the status name)
    # hint: then loop through your projects list — for each project, check its status
    #       and draw a card in the matching column
    # hint: a card is just a rectangle — pygame.draw.rect draws one
    #       put the project name as text inside it
    # hint: to stack cards vertically, keep a counter per column
    #       each new card in that column is drawn lower by one card height

    pygame.display.update()
pygame.quit()
sys.exit(0)
