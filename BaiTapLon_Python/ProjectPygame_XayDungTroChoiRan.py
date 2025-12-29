import pygame
from time import sleep
from random import randint
import math

pygame.init()

cols = 20
rows = 20
cell_size = 540 / cols

screen = pygame.display.set_mode((781, 661))
background = pygame.image.load("bg.png").convert()
background = pygame.transform.scale(background, (781, 661))

frame = pygame.image.load("overlay.png").convert_alpha()
frame = pygame.transform.scale(frame, (540, 540))

apple_img = pygame.image.load("redapple.png").convert_alpha()
apple_img = pygame.transform.scale(apple_img, (30, 30))

gold_img = pygame.image.load("goldapple.png").convert_alpha()
gold_img = pygame.transform.scale(gold_img, (30, 30))

pygame.display.set_caption('Snake')
running = True

GREEN = (0, 255, 0)
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GOLD = (255,215,0)

clock = pygame.time.Clock()

# Snake position
# tail - head
snakes = [[5,10]]
direction = "right"

apple = [randint(0, cols-1), randint(0, rows-1)]

gold_apple = None        
gold_timer = pygame.time.get_ticks()
gold_exist = False      
GOLD_COOLDOWN = 1000     
GOLD_LIFETIME = 3000     

font_small = pygame.font.SysFont('comicsansms', 20)
font_big = pygame.font.SysFont('impact', 35)
score = 0
high_score = 0

pausing = False

def draw_capsule(surface, p1, p2, color, radius):
    x1, y1 = p1; x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length < 1e-6:
        pygame.draw.circle(surface, color, (int(x1), int(y1)), radius)
        return
    nx, ny = dx / length, dy / length
    px, py = -ny * radius, nx * radius
    a = (x1 + px, y1 + py)
    b = (x1 - px, y1 - py)
    c = (x2 - px, y2 - py)
    d = (x2 + px, y2 + py)
    pygame.draw.polygon(surface, color, [a, b, c, d])
    pygame.draw.circle(surface, color, (int(x1), int(y1)), radius)
    pygame.draw.circle(surface, color, (int(x2), int(y2)), radius)

def draw_segment_with_wrap(surface, c1, c2, grid_x, grid_y, cell_size, cols, rows, color, radius):
    x1, y1 = c1
    x2, y2 = c2

    # Kiểm tra wrap theo trục ngang
    if y1 == y2 and abs(x2 - x1) > 1:
        # ví dụ: từ 0 -> cols-1 (qua trái) hoặc cols-1 -> 0 (qua phải)
        p1 = grid_to_center([x1, y1], grid_x, grid_y, cell_size)
        p2 = grid_to_center([x2, y2], grid_x, grid_y, cell_size)
        # điểm mép trái/phải theo y
        left_edge  = (grid_x,                 p1[1])
        right_edge = (grid_x + cols*cell_size, p1[1])
        if x1 == 0 and x2 == cols-1:
            # đi qua trái: cắt tại mép trái và mép phải
            draw_capsule(surface, p1, left_edge,  color, radius)
            draw_capsule(surface, right_edge, p2, color, radius)
        elif x1 == cols-1 and x2 == 0:
            # đi qua phải
            draw_capsule(surface, p1, right_edge, color, radius)
            draw_capsule(surface, left_edge,  p2, color, radius)
        return

    # Kiểm tra wrap theo trục dọc
    if x1 == x2 and abs(y2 - y1) > 1:
        # ví dụ: từ 0 -> rows-1 (qua trên) hoặc rows-1 -> 0 (qua dưới)
        p1 = grid_to_center([x1, y1], grid_x, grid_y, cell_size)
        p2 = grid_to_center([x2, y2], grid_x, grid_y, cell_size)
        top_edge    = (p1[0], grid_y)
        bottom_edge = (p1[0], grid_y + rows*cell_size)
        if y1 == 0 and y2 == rows-1:
            # đi lên vượt mép trên
            draw_capsule(surface, p1, top_edge,    color, radius)
            draw_capsule(surface, bottom_edge, p2, color, radius)
        elif y1 == rows-1 and y2 == 0:
            # đi xuống vượt mép dưới
            draw_capsule(surface, p1, bottom_edge, color, radius)
            draw_capsule(surface, top_edge,    p2, color, radius)
        return

    # Không wrap: vẽ bình thường
    p1 = grid_to_center([x1, y1], grid_x, grid_y, cell_size)
    p2 = grid_to_center([x2, y2], grid_x, grid_y, cell_size)
    draw_capsule(surface, p1, p2, color, radius)

def grid_to_center(cell, grid_x, grid_y, cell_size):
    return (grid_x + cell[0]*cell_size + cell_size//2,
            grid_y + cell[1]*cell_size + cell_size//2)

def draw_snake_head(surface, pos, direction, near_food=False, dead=False):
    x, y = pos
    head_r = 14
    base_color = (0,80,0) #if not dead else (180, 180, 180)
    pygame.draw.circle(surface, base_color, (int(x), int(y)), head_r)

    dir_map = {"up": (0,-1), "down": (0,1), "left": (-1,0), "right": (1,0)}
    dx, dy = dir_map.get(direction, (0,-1))

    # Mắt
    eye_offset = 7
    ex1 = x + dx*eye_offset + (-dy)*5
    ey1 = y + dy*eye_offset + (dx)*5
    ex2 = x + dx*eye_offset + (dy)*5
    ey2 = y + dy*eye_offset + (-dx)*5

    if dead:
        def draw_X(cx, cy, size=4):
            pygame.draw.line(surface, (20,20,20), (cx-size, cy-size), (cx+size, cy+size), 2)
            pygame.draw.line(surface, (20,20,20), (cx-size, cy+size), (cx+size, cy-size), 2)
        draw_X(ex1, ey1); draw_X(ex2, ey2)
    else:
        pygame.draw.circle(surface, (255,255,255), (int(ex1), int(ey1)), 4)
        pygame.draw.circle(surface, (255,255,255), (int(ex2), int(ey2)), 4)
        pygame.draw.circle(surface, (0,0,0), (int(ex1), int(ey1)), 2)
        pygame.draw.circle(surface, (0,0,0), (int(ex2), int(ey2)), 2)

    # Miệng (mở lớn khi gần táo)
    mouth_width = 6 if near_food else 3
    mx1 = x + dx*head_r*0.6 + (-dy)*mouth_width
    my1 = y + dy*head_r*0.6 + (dx)*mouth_width
    mx2 = x + dx*head_r*0.6 + (dy)*mouth_width
    my2 = y + dy*head_r*0.6 + (-dx)*mouth_width
    pygame.draw.line(surface, (0,0,0), (mx1,my1), (mx2,my2), 2)
# ====== HẾT PHẦN THÊM ======
def unwrap_points(points, width_px, height_px):
    # Điều chỉnh các điểm liên tiếp để khoảng cách ngắn nhất, tính theo wrap
    if not points:
        return points
    unwrapped = [points[0]]
    ox, oy = 0, 0  # offset tích lũy
    for i in range(1, len(points)):
        x0, y0 = unwrapped[-1]
        x1, y1 = points[i]
        # thử các dịch chuyển theo bề rộng/chiều cao để chọn khoảng cách ngắn nhất
        candidates = [
            (x1 + ox,         y1 + oy),
            (x1 + ox + width_px,  y1 + oy),
            (x1 + ox - width_px,  y1 + oy),
            (x1 + ox,         y1 + oy + height_px),
            (x1 + ox,         y1 + oy - height_px),
            (x1 + ox + width_px,  y1 + oy + height_px),
            (x1 + ox - width_px,  y1 + oy + height_px),
            (x1 + ox + width_px,  y1 + oy - height_px),
            (x1 + ox - width_px,  y1 + oy - height_px),
        ]
        # chọn candidate gần nhất với điểm trước
        best = min(candidates, key=lambda p: (p[0]-x0)**2 + (p[1]-y0)**2)
        unwrapped.append(best)
        # cập nhật offset tích lũy theo lựa chọn tốt nhất
        ox += best[0] - (x1 + ox)
        oy += best[1] - (y1 + oy)
    return unwrapped

while running:      
    clock.tick(60)
    # Vẽ background
    screen.blit(background, (0, 0))

    # Vẽ overlay frame (căn giữa màn hình)
    grid_width = cols * cell_size 
    grid_height = rows * cell_size
    frame_x = (screen.get_width() - grid_width) // 2
    frame_y = (screen.get_height() - grid_height) // 2
    screen.blit(frame, (frame_x, frame_y))

    tail_x = snakes[0][0]
    tail_y = snakes[0][1]

    # Draw grid
    GRID_COLOR = (30, 30, 30)
    rows = 20   # số ô dọc
    cols = 20   # số ô ngang
    cell_size = 540 / cols   # phủ kín chiều ngang, mỗi ô ≈ 31.76 px
    grid_x = frame_x
    grid_y = frame_y

    # Vẽ lưới 16x16 trong frame
    #for i in range(int(rows)+1):
        #pygame.draw.line(screen, GRID_COLOR,
                        #(grid_x, grid_y + i*cell_size),
                        #(grid_x + cols*cell_size, grid_y + i*cell_size))
    #for j in range(cols+1):
        #pygame.draw.line(screen, GRID_COLOR,
                        #(grid_x + j*cell_size, grid_y),
                        #(grid_x + j*cell_size, grid_y + rows*cell_size))

    # Chỉ cho phép vẽ trong khung lưới
    screen.set_clip(pygame.Rect(grid_x, grid_y, cols*cell_size, rows*cell_size))

    body_color = (0, 200, 0)
    body_radius = 12
    for i in range(len(snakes)-1):
        c1 = snakes[i]
        c2 = snakes[i+1]
        draw_segment_with_wrap(screen, c1, c2, grid_x, grid_y, cell_size, cols, rows, body_color, body_radius)

# Đầu rắn dùng đúng ô cuối
    head_cell = snakes[-1]
    head_pos = grid_to_center(head_cell, grid_x, grid_y, cell_size)

    ax, ay = grid_to_center(apple, grid_x, grid_y, cell_size)
    dist_to_apple = math.hypot(head_pos[0]-ax, head_pos[1]-ay)
    near_food = dist_to_apple < 40
    draw_snake_head(screen, head_pos, direction, near_food=near_food, dead=pausing)

    # Draw apple (sửa thụt dòng cho đúng)
    screen.blit(apple_img, (grid_x + apple[0]*cell_size, grid_y + apple[1]*cell_size))
    
    # Draw golden apple
    now = pygame.time.get_ticks()
    if now - gold_timer >= GOLD_COOLDOWN and not gold_exist:
        gold_apple = [randint(0, cols-1), randint(0, rows-1)]
        gold_exist = True
        gold_start_time = now   
        gold_timer = now

    # Draw gold apple
    if gold_exist:
        screen.blit(gold_img, (grid_x + gold_apple[0]*cell_size, grid_y + gold_apple[1]*cell_size))
        # Bỏ clip để vẽ phần khác (text, nền...)
        screen.set_clip(None)
    # Hide gold apple after lifetime
    if gold_exist and now - gold_start_time > GOLD_LIFETIME:
        gold_exist = False
        gold_apple = None

    # point
    # Eating apple
    if snakes[-1][0] == apple[0] and snakes[-1][1] == apple[1]:
        snakes.insert(0,[tail_x,tail_y])
        apple = [randint(0, cols-1), randint(0, rows-1)]

        score += 1
        
    # Eating golden apple
    if gold_exist and snakes[-1][0] == gold_apple[0] and snakes[-1][1] == gold_apple[1]:
        snakes.insert(0,[tail_x,tail_y])
        snakes.insert(0,[tail_x,tail_y])   
        score += 3                        
        gold_exist = False                
        gold_apple = None

    # Draw score
    score_txt = font_small.render("Score: " + str(score), True, WHITE)
    screen.blit(score_txt, (5,5))
    high_score_txt = font_small.render("High Score: " + str(high_score), True, WHITE)
    screen.blit(high_score_txt, (5,30))

    # Snake move
    if pausing == False:
        if direction == "right":
            new_head = [snakes[-1][0]+1, snakes[-1][1]]
        elif direction == "left":
            new_head = [snakes[-1][0]-1, snakes[-1][1]]
        elif direction == "up":
            new_head = [snakes[-1][0], snakes[-1][1]-1]
        elif direction == "down":
            new_head = [snakes[-1][0], snakes[-1][1]+1]

        snakes.append(new_head)

        # Kiểm tra va chạm với thân rắn trước khi xóa đuôi
        for i in range(len(snakes)-1):
            if new_head[0] == snakes[i][0] and new_head[1] == snakes[i][1]:
                pausing = True
            
        if not pausing:
            snakes.pop(0)

# Wrap từng ô trong thân rắn
        for s in snakes:
            s[0] = (s[0] + cols) % cols
            s[1] = (s[1] + rows) % rows


    # check crash with body
    for i in range(len(snakes)-1):
        if snakes[-1][0] == snakes[i][0] and snakes[-1][1] == snakes[i][1]:
            pausing = True
        if score > high_score:
            high_score = score

    # Draw game over
    if pausing:
        TEXT_COLOR = (0, 50, 0)
        game_over_txt = font_big.render("Game over! Score: " + str(score), True, TEXT_COLOR)
        press_space_txt = font_big.render("Press Space to continue", True, TEXT_COLOR)

        frame_width = cols * cell_size  # = 540
        frame_height = rows * cell_size  # = 337.5

        text_x = frame_x + (frame_width - game_over_txt.get_width()) // 2
        text_y = frame_y + (frame_height - game_over_txt.get_height() - press_space_txt.get_height()) // 2


        screen.blit(game_over_txt, (text_x, text_y))
        screen.blit(press_space_txt, (text_x, text_y + game_over_txt.get_height() + 10))

    speed = max(0.17 - len(snakes) * 0.003, 0.03)
    sleep(speed)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction != "down":
                direction = "up"
            if event.key == pygame.K_DOWN and direction != "up":
                direction = "down"
            if event.key == pygame.K_LEFT and direction != "right":
                direction = "left"
            if event.key == pygame.K_RIGHT and direction != "left":
                direction = "right"
            if event.key == pygame.K_SPACE and pausing == True:
                pausing = False
                snakes = [[5,10]]
                apple = [randint(0, cols-1), randint(0, rows-1)]
                score = 0

    pygame.display.flip()

pygame.quit()
